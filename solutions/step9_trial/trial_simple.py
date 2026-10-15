"""
STEP 9 · Put the judge on trial. The judge is AI too, so it can be wrong.

Put a CAP on the judge:
    C · Consistent?   Repeat it:  score the SAME answer 3 times. How far apart are the scores?
    A · Agrees?       Compare it: does the judge score it like YOU would?
    P · Price?        Count it:   how many judge calls, how many seconds?

Three parts:
    1. One answer to put on trial, the answer key, and YOUR score (given before running anything!)
    2. Hire the judge, with one rubric (G-Eval: a rubric in plain English)
    3. Score it 3 times, then print the CAP

Run it (from this folder, with your virtual environment active). The bot does NOT need to run:

    python trial_simple.py

2 small experiments. Find "EXPERIMENT 1" and "EXPERIMENT 2" below.
Remove the # from those lines (Ctrl+/), save, run, then put the # back.

    1. The small judge     your bot's own small model acts as the judge     Does it wobble more? Agree less?
    2. A perfect answer    an answer that matches the key exactly           Does the judge give it ~1?
"""

import os
import statistics
import time
import warnings

from deepeval.metrics import GEval
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase, SingleTurnParams
from dotenv import load_dotenv

load_dotenv()                                     # reads the .env file in the main project folder
warnings.filterwarnings("ignore")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")


# 1. One answer to put on trial

question = "Can I return shoes I bought 20 days ago? I haven't worn them."
expected = "Yes. Unused items can be returned within 30 days of delivery for a full refund."     # the answer key
answer = "Yes, within 30 days, but there is a 5 EUR restocking fee."                             # what a bot said

# EXPERIMENT 2 · A perfect answer (remove the # from the next line)
# answer = "Yes! Unused items can go back within 30 days of delivery, and you'll get a full refund."

# Your own score, BEFORE running anything: 0 = wrong, 1 = perfect. (The invented fee makes it mostly wrong.)
MY_SCORE = 0.3


# 2. Hire the judge (the big one from .env, like step 7) and give it one rubric

judge = LocalModel(model=os.getenv("JUDGE_MODEL"),
                   base_url=os.getenv("JUDGE_BASE_URL", "https://api.groq.com/openai/v1"),
                   api_key=os.getenv("JUDGE_API_KEY"))

# EXPERIMENT 1 · The small judge: your bot's own model (LLM_* in .env) marks the answer (remove the # from 3 lines)
# judge = LocalModel(model=os.getenv("LLM_MODEL"),
#                    base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
#                    api_key=os.getenv("LLM_API_KEY"))

RUBRIC = ("Does the actual output give the same answer as the expected output? "
          "Different wording is fine; missing facts, extra invented facts, or contradictions are not.")


# 3. Score the same answer 3 times

test_case = LLMTestCase(input=question, actual_output=answer, expected_output=expected)
scores = []
started = time.time()
for run in range(1, 4):
    metric = GEval(name="Correctness", model=judge, criteria=RUBRIC, async_mode=False,
                   evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT])
    metric.measure(test_case)                      # one judge verdict (G-Eval makes 1-2 model calls)
    scores.append(metric.score)
    print(f"run {run}: {metric.score:.2f}   {metric.reason}")
seconds = time.time() - started

print("--------------------------------------------")
print(f"Answer on trial: {answer}")
print(f"C · Consistent?  scores {', '.join(f'{s:.2f}' for s in scores)}  ->  range {max(scores) - min(scores):.2f}")
if MY_SCORE is None:
    print("A · Agrees?      fill in MY_SCORE at the top first")
else:
    print(f"A · Agrees?      judge average {statistics.mean(scores):.2f} vs YOUR {MY_SCORE}  ->  "
          f"distance {abs(statistics.mean(scores) - MY_SCORE):.2f}  (lower = agrees more)")
print(f"P · Price?       3 verdicts took {seconds:.1f} s. Now imagine 100 questions x 5 metrics, on every commit.")
