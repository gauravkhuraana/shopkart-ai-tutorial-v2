# LAB 8 · Put the judge on trial (17 min)
**Goal:** measure how much your AI judge wobbles, and whether it agrees with you.
**You'll learn:** eval flakiness, calibration against human scores, choosing a pass mark, what evals cost.

**Put a CAP on the judge:**
- **C**onsistent? Repeat it: same answer, three runs, how far apart are the scores?
- **A**grees with you? Compare it: does it score like a human would?
- **P**rice? What does one full test run cost?

---

## CORE (everyone · ~12 min, no coding)
1. Open `tests/my_scores.yaml`: five answers to ShopKart questions. **Score each one yourself** (0 = wrong, 1 = perfect) in `my_score`. Don't run anything first.
2. Put both judges on trial: the small model your bot uses (LOCAL) against the bigger hosted judge (HOSTED):
   ```bash
   python tests/judge_the_judge.py --runs 2
   ```
3. Read the table. The **range** shows how much each judge wobbles (**C**). The **distance from YOUR scores** shows how much it agrees with you (**A**).

**Done when:**
- You can say which judge is steadier, and by how much.
- You can say which judge agrees with you, and on which answer it doesn't.

---

## STRETCH (fast finishers)
- Run 3 rounds instead of 2: `python tests/judge_the_judge.py`
- Make the `RUBRIC` in `judge_the_judge.py` more specific (e.g. "an invented fee is a serious error"). Does the wobble shrink? Does agreement improve?

## Boss level
- From your data, pick a pass mark you could defend to your team.
- Work out the cost of one full test run: judge calls × tokens × price (**P**).

## Stuck?
Rate limits: FAQ #14 · LOCAL judge too slow on your laptop? Skip it and compare HOSTED with your own scores.
