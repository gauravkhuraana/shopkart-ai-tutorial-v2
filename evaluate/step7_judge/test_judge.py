"""
STEP 7 · The full version: the judge on every golden question, with the whole "Is it TRUE?" check.

judge_simple.py judged one answer with one or two metrics. This file is what you'd run in a real project:
    - every golden question marked `judge: true` (evaluate/golden_questions.yaml)
    - all four "Is it TRUE?" metrics + a Correctness check against the answer key
    - pass marks you choose, a clear failure message, and every score + reason on the scoreboard
      page evaluate/report.html (open it in your browser: it refreshes itself while the tests run)

Run it (from this folder, with the step 5 bot running):

    pytest test_judge.py -v                    # all judge questions (slower: several judge calls each)
    pytest test_judge.py -v -k price           # just one question

Search for "TODO": there is 1.  Stuck?  python ../../checkpoint.py step7

    Is it TRUE?    T  Truthful?          HallucinationMetric     contradicts the facts?
                   R  Relevant?          AnswerRelevancyMetric   answers the question that was asked?
                   U  Uses the source?   FaithfulnessMetric      every claim backed by the policy pages?
                   E  Even?              GEval "Coherence"       clear, no self-contradiction?
    + Correct?                           GEval "Correctness"     same answer as our answer key?
"""

import httpx
import pytest
import yaml
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    GEval,
    HallucinationMetric,
)
from deepeval.test_case import LLMTestCase, SingleTurnParams

import config  # shared/config.py: reads .env (SHOPKART_URL, JUDGE_*)

GOLDEN_FILE = config.ROOT / "evaluate" / "golden_questions.yaml"
golden_text = GOLDEN_FILE.read_text(encoding="utf-8")
GOLDEN = yaml.safe_load(golden_text)

# Only the golden questions that are marked for the AI judge.
JUDGE_CASES = []
CASE_IDS = []

for case in GOLDEN:
    if case.get("judge"):
        JUDGE_CASES.append(case)
        CASE_IDS.append(case["id"])

# TODO 1 · Choose your pass marks (0-1). Every metric passes when its score is AT LEAST its pass mark.
#          What's "good enough" for a refund bot? (try 0.7 for both, then make one stricter)
TRUTHFUL_PASS = 0.7  # T · Hallucination: 1 = no contradictions with the facts
GROUNDED_PASS = 0.8  # U · Faithfulness:  1 = every claim is backed by the policy pages


def ask_bot(question: str) -> dict:
    """Ask the bot over HTTP, getting a fresh response on every call."""
    message = {
        "role": "user",
        "content": question,
    }

    request_body = {
        "messages": [message],
    }

    response = httpx.post(
        f"{config.SHOPKART_URL}/chat",
        json=request_body,
        timeout=180,
    )

    response.raise_for_status()
    return response.json()


@pytest.mark.parametrize("case", JUDGE_CASES, ids=CASE_IDS)
def test_judge(case, scoreboard):
    if TRUTHFUL_PASS is None or GROUNDED_PASS is None:
        pytest.skip(
            "TODO 1: set TRUTHFUL_PASS and GROUNDED_PASS at the top of this file"
        )

    result = ask_bot(case["question"])

    pages = result["context"]
    if not pages:
        pages = ["(no policy pages were retrieved)"]

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=result["reply"],
        expected_output=case["expected"],  # the answer key
        context=[case["truth"]],  # the ground truth
        retrieval_context=pages,  # what the librarian brought
    )
    judge = (
        config.judge_model()
    )  # the same LocalModel(...) as in judge_simple.py, settings from .env
    metrics = [
        HallucinationMetric(
            threshold=TRUTHFUL_PASS,
            model=judge,
            async_mode=False,
        ),  # T
        AnswerRelevancyMetric(
            threshold=0.7,
            model=judge,
            async_mode=False,
        ),  # R
        FaithfulnessMetric(
            threshold=GROUNDED_PASS,
            model=judge,
            async_mode=False,
        ),  # U
        GEval(
            name="Coherence",
            model=judge,
            threshold=0.6,
            async_mode=False,  # E
            criteria="Is the actual output clear, logically consistent and free of self-contradiction? "
            "An answer that says yes and no to the same thing is incoherent.",
            evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        ),
        GEval(
            name="Correctness",
            model=judge,
            threshold=0.6,
            async_mode=False,  # + Correct?
            criteria="Does the actual output give the same answer as the expected output? "
            "Different wording is fine; missing or contradicting facts are not.",
            evaluation_params=[
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
        ),
        # BOSS LEVEL · write your own rubric, e.g. "never promises compensation that isn't in the policy":
        # GEval(
        #     name="No invented compensation",
        #     model=judge,
        #     threshold=0.7,
        #     async_mode=False,
        #     criteria="...",
        #     evaluation_params=[
        #         SingleTurnParams.ACTUAL_OUTPUT,
        #         SingleTurnParams.CONTEXT,
        #     ],
        # ),
    ]

    # The judge marks each rubric. (DeepEval's assert_test() does the same in one line,
    # but it doesn't keep the scores, and we want them on the scoreboard.)
    for metric in metrics:
        metric.measure(test_case)
    scoreboard.add(metrics)

    failed = []
    for metric in metrics:
        if not metric.is_successful():
            failure_message = (
                f"{metric.__name__}: {metric.score:.2f} "
                f"(pass mark {metric.threshold}) · {metric.reason}"
            )
            failed.append(failure_message)

    failure_details = "\n".join(failed)
    assert not failed, f"answer: {result['reply']}\n" + failure_details
