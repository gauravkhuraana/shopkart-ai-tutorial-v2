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

Run every command **inside the step folder** (e.g. `cd build/step2_api`).
Finished code: `../solutions/` · copy it in place: `python checkpoint.py stepN` from the repo root.
