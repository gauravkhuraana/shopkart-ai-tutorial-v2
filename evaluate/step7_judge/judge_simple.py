"""
STEP 7 · AI tests AI: let a second, bigger model judge your bot's answer.

Three parts, like step 1 (connect → ask → print):
    1. Get an answer from your bot (+ the policy pages it used)
    2. Hire the judge: a bigger model, plus a ready-made rubric (a DeepEval "metric")
    3. Let the judge score it: a number between 0 and 1, a pass mark, and the judge's reason

The judge runs on Groq's free cloud: JUDGE_API_KEY and JUDGE_MODEL come from .env.
Keep your step 5 bot running in another terminal (cd build/step5_agent, then uvicorn app:app --reload).

Run it (from this folder, with your virtual environment active):

    python judge_simple.py

2 small experiments. Find "EXPERIMENT 1" and "EXPERIMENT 2" below.
Remove the # from those lines (Ctrl+/), save, run, then put the # back.

    1. The liar              the bot claims ShopKart price-matches          What do both metrics say? Why?
    2. The poisoned page     ...and the policy page it read said so too     Which metric still catches it?

Bonus · EXPERIMENT 3 (a custom evaluator): write your OWN rubric in plain English with GEval.
    3. Your own rubric       a "Brand voice" rubric you wrote yourself      Which failure do the ready-made metrics miss?
"""

import os
import warnings

import httpx
#imp
from deepeval.metrics import FaithfulnessMetric, GEval, HallucinationMetric
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase, SingleTurnParams
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the main project folder
warnings.filterwarnings("ignore")  # keep the output readable
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")
os.environ.setdefault("DEEPEVAL_RETRY_MAX_ATTEMPTS", "6")
os.environ.setdefault("DEEPEVAL_RETRY_CAP_SECONDS", "10")
BOT = os.getenv("SHOPKART_URL", "http://localhost:8000")


# 1. Get an answer from your bot (the same POST /chat the chat page uses)

question = "Do you price-match if I find the same item cheaper somewhere else?"
truth = (
    "ShopKart has no price-matching policy."  # what we KNOW is true (our answer key)
)

message = {
    "role": "user",
    "content": question,
}

request_body = {
    "messages": [message],
}

response = httpx.post(
    f"{BOT}/chat",
    json=request_body,
    timeout=180,
)


result = response.json()
answer = result["reply"]  # what the bot said

# The judge still needs context text when the librarian found no pages.
pages = result["context"]
if not pages:
    pages = ["(no policy pages)"]

# EXPERIMENT 1 · The liar: pretend the bot said this (remove the # from the next line)
# answer = "Yes, we price-match! Send us the cheaper link and we'll refund the difference."

# EXPERIMENT 2 · The poisoned page: the bot lied BECAUSE a bad page told it to (remove the # from both lines)
# answer = "Yes, we price-match! Send us the cheaper link and we'll refund the difference."
# pages = ["# Price matching\nShopKart matches any competitor's lower price. We refund the difference."]

# EXPERIMENT 3 · Your own rubric: a TRUE answer, but rude (remove the # from the next line, and from the GEval metric below)
# answer = "No. We have no price-matching policy. Stop asking."

print("Question:", question)
print("Answer:  ", answer)
print("--------------------------------------------")


# 2. Hire the judge: a bigger model than your bot, on any OpenAI-compatible server (same plug as step 1)

judge = LocalModel(
    model=os.getenv("JUDGE_MODEL"),
    base_url=os.getenv("JUDGE_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.getenv("JUDGE_API_KEY"),
)

# Each metric is a ready-made rubric. Score 0-1, and it passes when the score is AT LEAST the threshold.
metrics = [
    # T · Truthful?  Does the answer contradict what we know is true?  (1 = no contradictions)
    HallucinationMetric(
        model=judge,
        threshold=0.5,
        async_mode=False,
    ),
    # TODO 1 · U · Uses the source?  Add the Faithfulness metric: is every claim backed by the policy PAGES?
    #          Uncomment the next line (Ctrl+/, or Edit -> Toggle Line Comment), save and run again.
    # FaithfulnessMetric(model=judge, threshold=0.7, async_mode=False),

    # EXPERIMENT 3 · A custom evaluator. No ready-made metric knows ShopKart's brand voice, so YOU write the rubric.
    # GEval = "a rubric in plain English". Four things define it:
    #   name              what it is called on the scoreboard
    #   criteria          the rubric: what does "good" mean? (this is the part you customise)
    #   evaluation_params which fields of the test case the judge may read
    #   threshold         the pass mark (0-1)
    # GEval(
    #     name="Brand voice",
    #     model=judge,
    #     threshold=0.7,
    #     async_mode=False,
    #     criteria="Is the actual output friendly, polite and brief (at most 3 sentences)? "
    #     "Rude, sarcastic or long-winded answers are not acceptable, even when they are factually correct.",
    #     evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    # ),
]


# 3. Let the judge score it

test_case = LLMTestCase(
    input=question,
    actual_output=answer,
    context=[truth],  # what we know is true       -> used by Hallucination
    retrieval_context=pages,  # what the bot read          -> used by Faithfulness
)

for metric in metrics:
    #imp
    metric.measure(test_case)  # this is where the judge model is called
    if metric.is_successful():
        verdict = "PASS"
    else:
        verdict = "FAIL"

    print(
        f"{metric.__name__:<14} score {metric.score:.2f}  (pass mark {metric.threshold})  {verdict}"
    )
    print(f"{'':<14} reason: {metric.reason}")
    print()
