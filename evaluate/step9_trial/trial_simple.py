"""
STEP 9 · Put the judge on trial.  The judge is AI too, so it can be wrong.

We check the judge with a CAP:

    C · Consistent?   Score the SAME answer 3 times.   How far apart are the scores?
    A · Agrees?       Compare with YOUR own score.     Does the judge mark like you?
    P · Price?        Count the time.                  How long do 3 verdicts take?

The script has 3 parts:

    1. The answer on trial, the answer key, and YOUR score   (TODO 1: do this before you run!)
    2. The judge, plus one rubric                            (G-Eval = a rubric in plain English)
    3. Score the answer 3 times, then print the CAP

Run it from this folder, with your virtual environment active.
The bot does NOT need to run:

    python trial_simple.py

2 small experiments: find "EXPERIMENT 1" and "EXPERIMENT 2" below.
Remove the # (Ctrl+/), save, run, then put the # back.

    #   Experiment         What changes                          What to look for
    1   The small judge    your bot's small model is the judge   Does it wobble more? Agree less?
    2   A perfect answer   the answer matches the key exactly    Does the judge give it about 1?
"""

import os
import statistics
import time
import warnings

from deepeval.metrics import GEval
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase, SingleTurnParams
from dotenv import load_dotenv

load_dotenv()                      # reads the .env file in the main project folder
warnings.filterwarnings("ignore")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")


# ---------------------------------------------------------------------------
# 1. The answer on trial
# ---------------------------------------------------------------------------

question = "Can I return shoes I bought 20 days ago? I haven't worn them."

# The answer key: what we KNOW is right
expected = "Yes. Unused items can be returned within 30 days of delivery for a full refund."

# What a bot said (it invents a fee, so it is NOT fully right)
answer = "Yes, within 30 days, but there is a 5 EUR restocking fee."

# EXPERIMENT 2 · A perfect answer (remove the # from the next line)
# answer = "Yes! Unused items can go back within 30 days of delivery, and you'll get a full refund."

# TODO 1 · Score the answer YOURSELF first, before you run anything.
#          0 = wrong, 1 = perfect   (for example: 0.3)
MY_SCORE = None


# ---------------------------------------------------------------------------
# 2. The judge and the rubric
# ---------------------------------------------------------------------------

# The big judge from .env (same as step 7)
judge = LocalModel(
    model=os.getenv("JUDGE_MODEL"),
    base_url=os.getenv("JUDGE_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.getenv("JUDGE_API_KEY"),
)

# EXPERIMENT 1 · The small judge: your bot's own model (LLM_* in .env). Remove the # from all 5 lines.
# judge = LocalModel(
#     model=os.getenv("LLM_MODEL"),
#     base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
#     api_key=os.getenv("LLM_API_KEY"),
# )

RUBRIC = (
    "Does the actual output give the same answer as the expected output? "
    "Different wording is fine; missing facts, extra invented facts, or contradictions are not."
)


# ---------------------------------------------------------------------------
# 3. Score the SAME answer 3 times
# ---------------------------------------------------------------------------

test_case = LLMTestCase(input=question, actual_output=answer, expected_output=expected)

scores = []
started = time.time()

for run in range(1, 4):
    metric = GEval(
        name="Correctness",
        model=judge,
        criteria=RUBRIC,
        async_mode=False,
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
    )
    metric.measure(test_case)      # one judge verdict (G-Eval makes 1-2 model calls)
    scores.append(metric.score)
    print(f"run {run}: {metric.score:.2f}   {metric.reason}")

seconds = time.time() - started


# ---------------------------------------------------------------------------
# The CAP result
# ---------------------------------------------------------------------------

score_range = max(scores) - min(scores)
average = statistics.mean(scores)

print()
print("============================================")
print(f"Answer on trial: {answer}")
print("============================================")

# C · Consistent?  A small range = the judge gives the same score each time
print(f"C · Consistent?  scores {', '.join(f'{s:.2f}' for s in scores)}  ->  range {score_range:.2f}")

# A · Agrees?  A small distance = the judge marks like you
if MY_SCORE is None:
    print("A · Agrees?      TODO 1: fill in MY_SCORE at the top first")
else:
    distance = abs(average - MY_SCORE)
    print(f"A · Agrees?      judge average {average:.2f} vs YOUR {MY_SCORE}  ->  distance {distance:.2f}  (lower = agrees more)")

# P · Price?  Time grows fast with more questions and metrics
print(f"P · Price?       3 verdicts took {seconds:.1f} s. Now imagine 100 questions x 5 metrics, on every commit.")
