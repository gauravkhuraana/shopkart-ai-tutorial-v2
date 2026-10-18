# Part 2 · TEST the bot: four steps, cheapest first

You built ShopKart's bot in steps 1–5. Now you test it, the same way: **one folder per step, a simple file first, a full file when you're done.**

```
step 6   Rules            words it must say / must never say          rules_simple.py       test_rules.py
step 7   AI judge         a bigger model scores the answer (DeepEval)  judge_simple.py       test_judge.py
step 8   Agent            check the journey, not just the landing      agent_check_simple.py test_agents.py
step 9   Judge on trial   the judge is AI too: put a CAP on it         trial_simple.py       judge_the_judge.py
```

**Airport security, bottom-up:** the metal detector (step 6: plain rules, free, on every question) → the officer (step 7: the AI judge, only where judgement is needed) → the supervisor (step 9: a human checks the judge).

## Table of contents

- [Before you start: keep the step 5 bot running](#before-you-start-keep-the-step-5-bot-running)
- [Every folder](#every-folder)
- [The scoreboard: see your bot scored in your browser](#the-scoreboard-see-your-bot-scored-in-your-browser)
- [Want to break the real bot? (full files only)](#want-to-break-the-real-bot-full-files-only)

## Before you start: keep the step 5 bot running
Steps 6, 7 and 8 test your step 5 bot over HTTP, so it must be running. **Window 2**, leave it open.

**a)** Go to the project folder (the one that contains check_setup.py) and activate the venv. Change the path on the first line to where **you** saved the project. VS Code's built-in terminal already starts in the project folder, so there you can delete the first line:

**Windows (PowerShell)**

```powershell
cd path\to\shopkart-ai-tutorial-v2
.venv\Scripts\Activate.ps1
```

**Mac / Linux**

```bash
cd path/to/shopkart-ai-tutorial-v2
source .venv/bin/activate
```

**b)** Start the bot:

**Windows (PowerShell)**

```powershell
cd build\step5_agent
uvicorn app:app --reload
```

**Mac / Linux**

```bash
cd build/step5_agent
uvicorn app:app --reload
```

Then do your work in **window 3** (a new terminal: activate the venv again, then `cd` into the step folder). Step 9 does not need the bot.
Every test talks to the bot over HTTP, exactly like the chat page. Laptop can't run it? Put the hosted bot's address in `.env` as `SHOPKART_URL` (TROUBLESHOOTING.md #18).

Bot responses are not cached: every call makes a fresh request, even for a repeated question or order. Separate tests can therefore receive different LLM responses. In step 8, checking the same order in several tests means several crew runs, which takes more time and can increase API costs. Multiple checks or judge metrics within one test still use the response that test received.

| Step | Bot running? | Judge (internet)? | Copy-paste commands |
|---|---|---|---|
| 6 · Rules | yes | no | [step6_rules](step6_rules/README.md) |
| 7 · AI judge | yes | yes | [step7_judge](step7_judge/README.md) |
| 8 · Agent | yes | only `test_task_completion` | [step8_agent](step8_agent/README.md) |
| 9 · Judge on trial | no | yes | [step9_trial](step9_trial/README.md) |

Everything in one place: [COMMANDS_WINDOWS.md](../COMMANDS_WINDOWS.md) · [COMMANDS_MAC.md](../COMMANDS_MAC.md)

## Every folder

The Python examples use ordinary loops, descriptive intermediate variables and spacing between logical steps. Read each file from top to bottom: prepare the request, call the bot or judge, then check the result. Request dictionaries and metric settings are spread over multiple lines so you can inspect each field separately.

- `…_simple.py`: a plain Python script in 2–3 numbered parts. We walk through it together, you run it, and it **prints** what happened. It has 1–2 `TODO`s (the **CORE**) and a few `EXPERIMENT` lines: remove the `#` (Ctrl+/), run, see a bug get caught, put the `#` back.
- the full file (`test_….py`): the same idea as a real pytest suite, on many questions, with pass marks and clear failure messages. That's the **STRETCH**.
- `README.md`: what you do, how to run it, how you know you're done.

Run each step's commands **inside its folder**, with `.venv` active. For example, from the project folder:

```bash
cd evaluate/step6_rules
```

Fell behind? Copy a finished step from the repo root (replace `step6` with `step7`, `step8` or `step9` as needed):

```bash
python checkpoint.py step6
```

Finished code: `solutions/step6_rules` … `solutions/step9_trial`.

## The scoreboard: see your bot scored in your browser
Every time you run **pytest** in Part 2, it writes one page: **`evaluate/report.html`**. Open it in your browser (double-click it, or Ctrl+click the link pytest prints at the end). Leave it open: it refreshes itself while the tests run.

- One row per test: green, red or skipped (a TODO).
- For AI-judge tests: every metric's score as a bar, the pass mark as a line, and the judge's reason. Red tests open by themselves.
- No account, no server, no internet. It's a plain file on your laptop (written by `evaluate/conftest.py`).

## Want to break the real bot? (full files only)
The simple files fake their bugs with `EXPERIMENT` lines. The full files can test a bot that's really broken. From any step folder:
or: no_pages, skip_lookup, overpay, blind_reviewer, shared_memory, no_breaker, false_promise

```bash
python ../../plant_bug.py liar
```

healthy again

```bash
python ../../plant_bug.py off
```

The running bot reads the switch on every request: no restart needed.

For diagrams, explanations of all eight bugs, code locations, and focused demo commands, see the [planted-bug walkthrough](../plant_bug_README.md).
