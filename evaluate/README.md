# Part 2 · TEST the bot: four steps, cheapest first

You built ShopKart's bot in steps 1–5. Now you test it, the same way: **one folder per step, a simple file first, a full file when you're done.**

```
step 6   Rules            words it must say / must never say          rules_simple.py       test_rules.py
step 7   AI judge         a bigger model scores the answer (DeepEval)  judge_simple.py       test_judge.py
step 8   Agent            check the journey, not just the landing      agent_check_simple.py test_agents.py
step 9   Judge on trial   the judge is AI too: put a CAP on it         trial_simple.py       judge_the_judge.py
```

**Airport security, bottom-up:** the metal detector (step 6: plain rules, free, on every question) → the officer (step 7: the AI judge, only where judgement is needed) → the supervisor (step 9: a human checks the judge).

## Before you start: keep the step 5 bot running
In a separate terminal (window 2):
```bash
cd build/step5_agent
uvicorn app:app --reload
```
Every test talks to it over HTTP, exactly like the chat page. Laptop can't run it? Put the hosted bot's address in `.env` as `SHOPKART_URL` (TROUBLESHOOTING.md #18).

## Every folder
- `…_simple.py`: a plain Python script in 2–3 numbered parts. We walk through it together, you run it, and it **prints** what happened. It has 1–2 `TODO`s (the **CORE**) and a few `EXPERIMENT` lines: remove the `#` (Ctrl+/), run, see a bug get caught, put the `#` back.
- the full file (`test_….py`): the same idea as a real pytest suite, on many questions, with pass marks and clear failure messages. That's the **STRETCH**.
- `README.md`: what you do, how to run it, how you know you're done.

Run every command **inside the step folder** (e.g. `cd evaluate/step6_rules`).
Fell behind? From the repo root: `python checkpoint.py step6` (… `step9`). Finished code: `solutions/step6_rules` … `solutions/step9_trial`.

## The scoreboard: see your bot scored in your browser
Every time you run **pytest** in Part 2, it writes one page: **`evaluate/report.html`**. Open it in your browser (double-click it, or Ctrl+click the link pytest prints at the end). Leave it open: it refreshes itself while the tests run.

- One row per test: green, red or skipped (a TODO).
- For AI-judge tests: every metric's score as a bar, the pass mark as a line, and the judge's reason. Red tests open by themselves.
- No account, no server, no internet. It's a plain file on your laptop (written by `evaluate/conftest.py`).

## Want to break the real bot? (full files only)
The simple files fake their bugs with `EXPERIMENT` lines. The full files can test a bot that's really broken. From any step folder:
```bash
python ../../plant_bug.py liar        # or: no_pages, skip_lookup, overpay, blind_reviewer, shared_memory, no_breaker, false_promise
python ../../plant_bug.py off         # healthy again
```
The running bot reads the switch on every request: no restart needed.
