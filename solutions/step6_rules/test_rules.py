"""
STEP 6 · The full version: the same two rules, on ALL 10 golden questions, as a pytest suite.

rules_simple.py checked one question and printed PASS/FAIL. This file does what a test team does:
    - the questions and their rules live in ONE answer-key file: evaluate/golden_questions.yaml
    - pytest runs every question as its own test (parametrize), with a clear message when one fails
    - the result also lands on the scoreboard page: evaluate/report.html

Run it (from this folder, with the step 5 bot running):

    pytest test_rules.py -v

The two rule checks are ready to run.
"""

import httpx
import pytest
import yaml

import config  # shared/config.py: SHOPKART_URL is the bot's address.

# 1. Load the questions and give each test a readable name.

golden_file = config.ROOT / "evaluate" / "golden_questions.yaml"
golden_text = golden_file.read_text(encoding="utf-8")
GOLDEN = yaml.safe_load(golden_text)

CASE_IDS = []

for case in GOLDEN:
    CASE_IDS.append(case["id"])


# 2. Ask the bot. Every call makes a fresh request.


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


# 3. Run the same two checks for each question in the answer key.


@pytest.mark.parametrize("case", GOLDEN, ids=CASE_IDS)
def test_rules(case):
    question = case["question"]
    response_data = ask_bot(question)

    # Lower-case both sides so matching does not depend on capitalization.
    answer = response_data["reply"].lower()
    must_have = []

    for word in case.get("must_include_any", []):
        must_have.append(word.lower())

    # Rule 1: if alternatives are listed, at least one must appear.
    if must_have:
        found_required_word = False

        for word in must_have:
            if word in answer:
                found_required_word = True
                break

        assert found_required_word, f"expected one of {must_have} in: {answer}"

    # Rule 2: none of the forbidden phrases may appear.
    for forbidden in case.get("must_not_include", []):
        forbidden_lower = forbidden.lower()

        assert (
            forbidden_lower not in answer
        ), f"found forbidden '{forbidden}' in: {answer}"
