# Solutions

Finished code for every step. Each folder here mirrors the folder of the same name in `build/`.

| Folder | Finished file(s) |
|---|---|
| `step1_model/` | `ask.py` (+ `ask_simple.py`) |
| `step2_api/` | `app.py` (+ `app_simple.py`) |
| `step3_ui/` | `index_simple.html`, `index.html`, `app_simple.py`, `app.py` (the full API with the extra endpoints) |
| `step4_ground/` | `app_simple.py` (self-contained), `app.py` (+ `retrieval.py`, `index_simple.html`, `index.html`) |
| `step5_agent/` | `agent_simple.py` (self-contained), `agent.py` (+ `app_simple.py`, `app.py`, `retrieval.py`, `index_simple.html`, `index.html`) |
| `tests/` | `test_chatbot.py` (LAB 6), `test_agents.py` (LAB 7) |

**Use them:**
- **Compare.** Open your file and the solution side by side. Only the TODO parts differ.
- **Copy into place.** From the repo root: `python checkpoint.py step3` (or `step1` … `step5`, `lab6`, `lab7`). Your own version is kept as `<name>.mine`.
- **Run directly.** Every solution folder runs too, e.g. `cd solutions/step4_ground && uvicorn app:app --reload`.

The test solutions need the answer key in `tests/`, so run them via `python checkpoint.py lab6` / `lab7`.
