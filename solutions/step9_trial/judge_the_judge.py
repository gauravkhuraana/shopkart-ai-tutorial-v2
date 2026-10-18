"""
STEP 9 · The full version: put BOTH judges on trial, on five answers, against YOUR scores.

trial_simple.py put one judge on trial with one answer. This file does the whole CAP at once:

    python judge_the_judge.py            # 3 runs per judge (default)
    python judge_the_judge.py --runs 2   # fewer calls if you hit rate limits

Scores the same 5 answers several times with two judges:
  - LOCAL  = the small model your bot runs on
  - HOSTED = the bigger judge model from .env (JUDGE_*)
Then compares both with YOUR scores from my_scores.yaml (in this folder).
Questions to answer: Which judge wobbles more? Which one agrees with you? Where do they disagree?
"""

import argparse
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
import config  # noqa: E402
from deepeval.metrics import GEval  # noqa: E402
from deepeval.test_case import LLMTestCase, SingleTurnParams  # noqa: E402

# The rubric. Stretch: make it more specific and see if the wobble shrinks.
RUBRIC = (
    "Does the actual output give the same answer as the expected output? "
    "Different wording is fine; missing facts, extra invented facts, or contradictions are not."
)


def score(judge, item) -> float:
    """Ask one judge to grade one answer. Returns its Correctness score (0 to 1)."""
    metric = GEval(
        name="Correctness",
        model=judge,
        criteria=RUBRIC,
        async_mode=False,
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
    )
    test_case = LLMTestCase(
        input=item["question"],
        actual_output=item["answer"],
        expected_output=item["expected"],
    )
    metric.measure(test_case)
    return metric.score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
    )
    args = parser.parse_args()

    scores_file = Path(__file__).parent / "my_scores.yaml"
    scores_text = scores_file.read_text(encoding="utf-8")
    items = yaml.safe_load(scores_text)

    judges = {
        "local": config.local_judge_model(),
        "hosted": config.judge_model(),
    }

    # Store runs as results[judge name][answer id].
    results = {}

    for name in judges:
        results[name] = {}

    # Every judge scores every answer several times, to see how much it wobbles.
    for name, judge in judges.items():
        for item in items:
            runs = []
            for _ in range(args.runs):
                try:
                    runs.append(score(judge, item))
                except Exception as err:  # rate limits, bad JSON from a small model...
                    print(f"  {name} judge failed on {item['id']}: {str(err)[:80]}")
            results[name][item["id"]] = runs
            formatted_runs = []

            for run_score in runs:
                formatted_runs.append(f"{run_score:.2f}")

            print(f"{name:>6} judge · answer {item['id']}: {formatted_runs}")
            time.sleep(0.5)

    # The table: for each answer, every judge's runs and spread, then YOUR score.
    print(f"\n{'':9}{'LOCAL judge':<26}{'HOSTED judge':<26}YOU")
    print(f"{'answer':9}{'runs':<18}{'range':>5}   {'runs':<18}{'range':>5}")
    # Each gap is the distance between a judge's average and your score.
    gaps = {}

    for name in judges:
        gaps[name] = []

    for item in items:
        row = f"  {item['id']:<7}"
        for name in judges:
            runs = results[name][item["id"]]
            if runs:
                spread = max(runs) - min(runs)
            else:
                spread = float("nan")

            formatted_runs = []
            for run_score in runs:
                formatted_runs.append(f"{run_score:.2f}")

            runs_text = " ".join(formatted_runs)
            row += f"{runs_text:<18}{spread:>5.2f}   "
            if runs and item.get("my_score") is not None:
                average = sum(runs) / len(runs)
                gaps[name].append(abs(average - float(item["my_score"])))

        my_score = item.get("my_score")
        if my_score is not None:
            row += str(my_score)
        else:
            row += "-"

        print(row)

    print()
    for name in judges:
        if gaps[name]:
            average_gap = sum(gaps[name]) / len(gaps[name])
            print(
                f"{name:>6} judge: average distance from YOUR scores = {average_gap:.2f}  (lower = agrees more)"
            )
        else:
            print(
                f"{name:>6} judge: fill in my_score in my_scores.yaml to measure agreement"
            )


if __name__ == "__main__":
    main()
