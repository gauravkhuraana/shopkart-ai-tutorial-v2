"""
LAB 6 · Mission: catch the liar.   Instructions: labs/LAB6.md
Search for "TODO": there are 3.  Stuck?  python checkpoint.py lab6

Run (from the repo root, with build/step5_agent running: uvicorn app:app --reload):   pytest tests/test_chatbot.py -v
Only the cheap checks:                            pytest tests/test_chatbot.py -v -k metal
Point at the hosted bot instead of yours:         set SHOPKART_URL in .env

Airport security, bottom-up:
  1. Metal detector  = plain rule checks (fast, free, run on every question)
  2. AI judge        = DeepEval metrics graded by a bigger model (relevancy, faithfulness, hallucination, coherence, correctness) (slower, costs calls: only on `judge: true` questions)
"""
from functools import lru_cache
from pathlib import Path

import httpx
import pytest
import yaml
from deepeval import assert_test
from deepeval.metrics import (AnswerRelevancyMetric, FaithfulnessMetric, GEval,
                              HallucinationMetric)
from deepeval.test_case import LLMTestCase, SingleTurnParams

import config

GOLDEN = yaml.safe_load((Path(__file__).parent / "golden_questions.yaml").read_text(encoding="utf-8"))
JUDGE_CASES = [c for c in GOLDEN if c.get("judge")]

# TODO 3 · Choose your pass marks (0-1). What's "good enough" for a refund bot?
GROUNDED_PASS = None       # Faithfulness must be AT LEAST this        (try 0.7)
HALLUCINATION_MAX = None   # Hallucination score must be AT MOST this  (lower = fewer contradictions)


@lru_cache(maxsize=None)
def ask_bot(question: str) -> dict:
    """Ask the bot over HTTP, exactly like the chat page does. Cached: each question is asked once per run."""
    response = httpx.post(f"{config.SHOPKART_URL}/chat",
                          json={"messages": [{"role": "user", "content": question}]}, timeout=180)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# 1. METAL DETECTOR: plain rules, no AI
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("case", GOLDEN, ids=[c["id"] for c in GOLDEN])
def test_metal_detector(case):
    answer = ask_bot(case["question"])["reply"].lower()

    # TODO 1 · Write the two rule checks, using the YAML fields:
    #   - case["must_include_any"]: the answer must contain AT LEAST ONE of these words (if the list isn't empty)
    #   - case["must_not_include"]: the answer must contain NONE of these
    #   Tip: compare lower-case text, and put the answer in the assert message so a failure explains itself.
    pytest.skip("TODO 1: write the metal-detector checks")


# ---------------------------------------------------------------------------
# 2. THE AI JUDGE: the fact-checker's four questions
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("case", JUDGE_CASES, ids=[c["id"] for c in JUDGE_CASES])
def test_ai_judge(case):
    result = ask_bot(case["question"])
    test_case = LLMTestCase(
        input=case["question"],
        actual_output=result["reply"],
        expected_output=case["expected"],                                  # the answer key
        retrieval_context=result["context"] or ["(no policy pages were retrieved)"],  # what the librarian brought
        context=[case["truth"]],                                           # the ground truth
    )
    judge = config.judge_model()
    if GROUNDED_PASS is None or HALLUCINATION_MAX is None:
        pytest.skip("TODO 3: set GROUNDED_PASS and HALLUCINATION_MAX at the top of this file")
    metrics = [
        # TODO 2 · Add the two missing fact-checker questions, graded by `judge`:
        #   Grounded?      FaithfulnessMetric(threshold=GROUNDED_PASS, model=judge, async_mode=False)
        #   Hallucinated?  HallucinationMetric(threshold=HALLUCINATION_MAX, model=judge, async_mode=False)

        # Relevant?      answers the question that was asked
        AnswerRelevancyMetric(threshold=0.7, model=judge, async_mode=False),
        # Coherent?     clear and free of self-contradiction (your own rubric, no answer key needed)
        GEval(name="Coherence", model=judge, threshold=0.6, async_mode=False,
              criteria="Is the actual output clear, logically consistent and free of self-contradiction? "
                       "An answer that says yes and no to the same thing is incoherent.",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT]),
        # Correct?       matches the answer key (a rubric-based judge)
        GEval(name="Correctness", model=judge, threshold=0.6, async_mode=False,
              criteria="Does the actual output give the same answer as the expected output? "
                       "Different wording is fine; missing or contradicting facts are not.",
              evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT]),
    ]
    assert_test(test_case, metrics)
