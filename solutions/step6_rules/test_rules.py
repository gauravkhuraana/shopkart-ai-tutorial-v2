"""
STEP 6 · The full version: the same two rules, on ALL 10 golden questions, as a pytest suite.

rules_simple.py checked one question and printed PASS/FAIL. This file does what a test team does:
    - the questions and their rules live in ONE answer-key file: evaluate/golden_questions.yaml
    - pytest runs every question as its own test (parametrize), with a clear message when one fails
    - the result also lands on the scoreboard page: evaluate/report.html

Run it (from this folder, with the step 5 bot running):

    pytest test_rules.py -v

Finished version (solutions/step6_rules).  Copy it in place:  python ../../checkpoint.py step6
"""
from functools import lru_cache

import httpx
import pytest
import yaml

import config     # shared/config.py: reads .env (SHOPKART_URL = where the bot lives)

GOLDEN = yaml.safe_load((config.ROOT / "evaluate" / "golden_questions.yaml").read_text(encoding="utf-8"))   # the answer key


@lru_cache(maxsize=None)
def ask_bot(question: str) -> dict:
    """Ask the bot over HTTP, exactly like the chat page does. Cached: each question is asked once per run."""
    response = httpx.post(f"{config.SHOPKART_URL}/chat",
                          json={"messages": [{"role": "user", "content": question}]}, timeout=180)
    response.raise_for_status()
    return response.json()


@pytest.mark.parametrize("case", GOLDEN, ids=[c["id"] for c in GOLDEN])
def test_rules(case):
    answer = ask_bot(case["question"])["reply"].lower()

    must_have = [w.lower() for w in case.get("must_include_any", [])]
    if must_have:
        assert any(w in answer for w in must_have), f"expected one of {must_have} in: {answer}"

    for forbidden in case.get("must_not_include", []):
        assert forbidden.lower() not in answer, f"found forbidden '{forbidden}' in: {answer}"
