# Solutions

Finished code for every step. Each folder here mirrors the folder of the same name in `build/` (steps 1-5) or `evaluate/` (steps 6-9).

| Folder | Finished file(s) |
|---|---|
| `step1_model/` | `ask.py` (+ `ask_simple.py`) |
| `step2_api/` | `app.py` (+ `app_simple.py`) |
| `step3_ui/` | `index_simple.html`, `index.html`, `app_simple.py`, `app.py` (the full API with the extra endpoints) |
| `step4_ground/` | `app_simple.py` (self-contained), `app.py` (+ `retrieval.py`, `index_simple.html`, `index.html`) |
| `step5_agent/` | `agent_simple.py` (self-contained), `agent.py` (+ `app_simple.py`, `app.py`, `retrieval.py`, `index_simple.html`, `index.html`) |
| `step6_rules/` | `rules_simple.py`, `test_rules.py` |
| `step7_judge/` | `judge_simple.py`, `test_judge.py` |
| `step8_agent/` | `agent_check_simple.py`, `test_agents.py` |
| `step9_trial/` | `trial_simple.py` (+ `judge_the_judge.py`) |

**Use them:**
- **Compare.** Open your file and the solution side by side. Only the TODO parts differ.
- **Copy into place.** From the repo root (replace `step3` with `step1` through `step9`). Your own version is kept as `<name>.mine`:

  ```bash
  python checkpoint.py step3
  ```

- **Run directly.** With `.venv` active, every solution folder runs too. For example, from the repo root:

  ```bash
  cd solutions/step4_ground
  ```

  ```bash
  uvicorn app:app --reload
  ```


The Part 2 solutions need the scoreboard and answer key in `evaluate/`, so copy them in place from the project root, then run them in their evaluation step folders. For example (replace `step6` with `step7`, `step8` or `step9` as needed):

```bash
python checkpoint.py step6
```

The simple files (`*_simple.py`) also run straight from here.
