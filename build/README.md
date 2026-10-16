# Part 1 · BUILD: five steps, inside out · the 5 Bs

**Brain** (the model) → **Bridge** (the API) → **Browser** (the web page) → **Book** (the policy pages) → **Body** (hands that act: tools)

Each step adds one layer around the model. These are the same boxes you see on the slides.

```
step 1   [ LLM ]                                   ask_simple.py, ask.py
step 2   [ FastAPI [ LLM ] ]                       app.py         POST /chat, /docs
step 3   [ Browser [ FastAPI [ LLM ] ] ]           index.html     fetch → /chat
step 4   ... + Knowledge: the librarian            retrieval.py   policy pages → RAG
step 5   ... + Tools: the crew                     agent.py       Planner → Implementer → Reviewer
```

**Every folder:**
- contains the **finished** code of the step before, so you can start any step fresh;
- marks only the new piece with numbered `TODO`s (2–3 per step): that's the **CORE**, which everyone does (step 1 has none: you walk through `ask_simple.py` together);
- has a **STRETCH** section for fast finishers;
- has a `README.md`: what you build, how to run it, how you know you're done.

Run each step's commands **inside its folder**, with your virtual environment active. For example, from the project folder:

```bash
cd build/step2_api
```

**Every new terminal needs the venv activated again**: each step README starts with individually copyable commands for Windows and Mac. Everything in one place: [COMMANDS_WINDOWS.md](../COMMANDS_WINDOWS.md) · [COMMANDS_MAC.md](../COMMANDS_MAC.md).
Steps 2-5 start a server (`uvicorn`) that keeps its terminal busy: stop it with `Ctrl+C` before starting the next step's server, because only one thing can use port 8000.
Finished code: `../solutions/`. From the repo root, copy a finished step in place (replace `step3` with `step1` through `step9`):

```bash
python checkpoint.py step3
```
