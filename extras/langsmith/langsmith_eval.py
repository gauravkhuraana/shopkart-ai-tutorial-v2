"""
Upload ShopKart's golden questions to LangSmith and run a dashboard experiment.

The step 5 bot must already be running:
    cd build/step5_agent
    uvicorn app:app --reload

From the project root:
    python extras/langsmith/langsmith_eval.py
    python extras/langsmith/langsmith_eval.py --with-ai-judge
"""
import argparse
import json
import os
import sys
import uuid
from pathlib import Path

import httpx
import yaml
from langsmith import Client, evaluate
from langsmith.schemas import ExampleCreate
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import config  # noqa: E402

DATASET_NAME = "shopkart-golden-questions"
EXPERIMENT_PREFIX = "shopkart-chatbot"
GOLDEN_PATH = Path(__file__).resolve().parents[2] / "evaluate" / "golden_questions.yaml"


def load_cases() -> list[dict]:
    cases = yaml.safe_load(GOLDEN_PATH.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{GOLDEN_PATH} must contain a non-empty list of cases")
    return cases


def require_langsmith_key() -> None:
    key = os.getenv("LANGSMITH_API_KEY", "")
    if not key or "your_key_here" in key:
        raise RuntimeError("Set LANGSMITH_API_KEY in .env before running the LangSmith evaluation.")


def sync_dataset(client: Client, cases: list[dict]) -> None:
    if not client.has_dataset(dataset_name=DATASET_NAME):
        client.create_dataset(
            dataset_name=DATASET_NAME,
            description="ShopKart golden questions (steps 6-7), expected answers and safety rules.",
        )

    namespace = uuid.uuid5(uuid.NAMESPACE_URL, DATASET_NAME)
    examples = [
        ExampleCreate(
            id=uuid.uuid5(namespace, case["id"]),
            inputs={"question": case["question"]},
            outputs={
                "expected": case["expected"],
                "truth": case["truth"],
                "must_include_any": case["must_include_any"],
                "must_not_include": case["must_not_include"],
            },
            metadata={"case_id": case["id"], "group": case["group"], "ai_judge": bool(case["judge"])},
        )
        for case in cases
    ]
    client.create_examples(dataset_name=DATASET_NAME, examples=examples)


def target(inputs: dict) -> dict:
    response = httpx.post(
        f"{config.SHOPKART_URL}/chat",
        json={"messages": [{"role": "user", "content": inputs["question"]}]},
        timeout=180,
    )
    response.raise_for_status()
    result = response.json()
    return {
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "context": result.get("context", []),
    }


def must_include_any(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    del inputs
    answer = outputs["reply"].lower()
    required = [phrase.lower() for phrase in reference_outputs["must_include_any"]]
    found = [phrase for phrase in required if phrase in answer]
    passed = not required or bool(found)

    if not required:
        comment = "No required phrases for this case."
    elif found:
        comment = f"Found required phrase(s): {found}"
    else:
        comment = f"Missing all required phrases: {required}"

    return {"key": "must_include_any", "score": int(passed), "comment": comment}


def must_not_include(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    del inputs
    answer = outputs["reply"].lower()
    forbidden = [phrase.lower() for phrase in reference_outputs["must_not_include"]]
    found = [phrase for phrase in forbidden if phrase in answer]
    return {
        "key": "must_not_include",
        "score": int(not found),
        "comment": f"Forbidden phrase(s) found: {found}" if found else "No forbidden phrases found.",
    }


def build_ai_judge():
    judge = OpenAI(base_url=config.JUDGE_BASE_URL, api_key=config.JUDGE_API_KEY)

    def ai_correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        response = judge.chat.completions.create(
            model=config.JUDGE_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Grade the assistant reply against the expected answer and ground truth. "
                        "Return JSON with score from 0 to 1 and a short reason. Different wording is fine; "
                        "missing facts, invented facts, unsafe promises and contradictions reduce the score."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": inputs["question"],
                            "reply": outputs["reply"],
                            "expected": reference_outputs["expected"],
                            "truth": reference_outputs["truth"],
                        }
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or ""
        result = json.loads(raw)
        score = float(result["score"])
        if not 0 <= score <= 1:
            raise ValueError(f"Judge returned a score outside 0-1: {score}")
        return {"key": "ai_correctness", "score": score, "comment": str(result["reason"])}

    return ai_correctness


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ShopKart evaluations in the LangSmith UI.")
    parser.add_argument("--with-ai-judge", action="store_true", help="Add one paid/model call per dataset case.")
    parser.add_argument("--dataset-only", action="store_true", help="Upload/update the dataset without running it.")
    args = parser.parse_args()

    require_langsmith_key()
    cases = load_cases()
    client = Client()
    sync_dataset(client, cases)
    print(f"LangSmith dataset ready: {DATASET_NAME} ({len(cases)} cases)")

    if args.dataset_only:
        return

    evaluators = [must_include_any, must_not_include]
    if args.with_ai_judge:
        if not config.JUDGE_API_KEY or "your_key_here" in config.JUDGE_API_KEY:
            raise RuntimeError("Set JUDGE_API_KEY in .env before using --with-ai-judge.")
        evaluators.append(build_ai_judge())

    evaluate(
        target,
        data=DATASET_NAME,
        evaluators=evaluators,
        experiment_prefix=EXPERIMENT_PREFIX,
        description="ShopKart golden-question regression evaluation.",
        metadata={"judge_model": config.JUDGE_MODEL if args.with_ai_judge else "rules-only"},
        max_concurrency=1,
        client=client,
    )
    print("Evaluation uploaded. Open https://smith.langchain.com and select the ShopKart project/experiment.")


if __name__ == "__main__":
    main()
