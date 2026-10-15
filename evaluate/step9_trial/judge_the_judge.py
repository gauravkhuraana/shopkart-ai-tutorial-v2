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
RUBRIC = ("Does the actual output give the same answer as the expected output? "
          "Different wording is fine; missing facts, extra invented facts, or contradictions are not.")


def score(judge, item) -> float:
    metric = GEval(name="Correctness", model=judge, criteria=RUBRIC, async_mode=False,
                   evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT])
    metric.measure(LLMTestCase(input=item["question"], actual_output=item["answer"],
                               expected_output=item["expected"]))
    return metric.score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    items = yaml.safe_load((Path(__file__).parent / "my_scores.yaml").read_text(encoding="utf-8"))
    judges = {"local": config.local_judge_model(), "hosted": config.judge_model()}
    results = {name: {} for name in judges}

    for name, judge in judges.items():
        for item in items:
            runs = []
            for _ in range(args.runs):
                try:
                    runs.append(score(judge, item))
                except Exception as err:          # rate limits, bad JSON from a small model...
                    print(f"  {name} judge failed on {item['id']}: {str(err)[:80]}")
            results[name][item["id"]] = runs
            print(f"{name:>6} judge · answer {item['id']}: {['%.2f' % r for r in runs]}")
            time.sleep(0.5)

    print(f"\n{'':9}{'LOCAL judge':<26}{'HOSTED judge':<26}YOU")
    print(f"{'answer':9}{'runs':<18}{'range':>5}   {'runs':<18}{'range':>5}")
    gaps = {name: [] for name in judges}
    for item in items:
        row = f"  {item['id']:<7}"
        for name in judges:
            runs = results[name][item["id"]]
            spread = (max(runs) - min(runs)) if runs else float("nan")
            row += f"{' '.join('%.2f' % r for r in runs):<18}{spread:>5.2f}   "
            if runs and item.get("my_score") is not None:
                gaps[name].append(abs(sum(runs) / len(runs) - float(item["my_score"])))
        row += f"{item.get('my_score', '-') if item.get('my_score') is not None else '-'}"
        print(row)

    print()
    for name in judges:
        if gaps[name]:
            print(f"{name:>6} judge: average distance from YOUR scores = {sum(gaps[name]) / len(gaps[name]):.2f}  (lower = agrees more)")
        else:
            print(f"{name:>6} judge: fill in my_score in my_scores.yaml to measure agreement")


if __name__ == "__main__":
    main()
