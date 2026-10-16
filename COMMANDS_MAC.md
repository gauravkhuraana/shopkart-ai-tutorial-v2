# ShopKart tutorial · all commands (Mac · Terminal, also works on Linux)

**If you get stuck anywhere, contact [Gaurav Khurana on LinkedIn](https://www.linkedin.com/in/gauravkhuraana/).**

One page, steps 1 to 9, in order. **Copy a block, paste it, read the one-line explanation.**
Windows user? Use [COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md). Stuck? [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Using the tutorial

- **Local laptop:** install and test Python, VS Code and Ollama using [PRE_CONFERENCE.md](PRE_CONFERENCE.md). Open the project with **File → Open Folder**, then **Terminal → New Terminal** in VS Code.
- **Every new tutorial terminal:** start in the project folder and activate `.venv` using the commands below before Python scripts or tests. The initial base-Python installation tests and setup script are the exceptions.
- **Bot:** follow the current step's commands. The server keeps its terminal busy; keep it open and use another activated terminal for tests. Press **Ctrl+C** before switching server versions/steps.
- **Local scoreboard:** after a pytest run, open `evaluate/report.html` in your browser.

### GitHub Codespaces (browser users, including Windows laptops)

A Codespace runs **Linux**: use this guide's Mac/Linux commands, not PowerShell. VS Code opens in your browser; the environment is prepared automatically. Confirm the terminal shows `(.venv)`; otherwise activate it from the project folder:
```bash
source .venv/bin/activate
```

When the step's bot starts, VS Code offers to open forwarded port **8000**: that is your chat page.

For the scoreboard, use a separate activated terminal in the **project folder** after running pytest:
```bash
python -m http.server 8080 --directory evaluate
```

Open forwarded port **8080** from VS Code's **Ports** panel and click **report.html**. Leave this terminal open while viewing the scoreboard; **Ctrl+C** stops it.

This browser fallback uses **Groq**, not Ollama on your own laptop. **Save your free hours:** stop the Codespace when finished (bottom-left menu → **Stop Current Codespace**). Corporate GitHub accounts sometimes block Codespaces; use a personal laptop/account where permitted, or pair with a neighbour.

**How to read this page**
- Unless a setup section says otherwise, start each step in the **project folder** (the one that contains `check_setup.py`) with **`(.venv)`** active, then follow the directory changes in order.
- After a step, return to the project folder:

  ```bash
  cd ../..
  ```

- Each code block contains one command. Read the explanation beside it before copying the next command.
- On Mac, creating the venv uses **`python3`**. Once `(.venv)` is active, plain `python` works.

**Contents**
[0 · Common commands](#0--common-commands) · [Which step needs what](#which-step-needs-what) ·
[1](#step-1--talk-to-the-model) · [2](#step-2--wrap-it-in-an-api) · [3](#step-3--give-it-a-face) · [4](#step-4--ground-it) · [5](#step-5--let-it-act) ·
[6](#step-6--rules-first) · [7](#step-7--ai-tests-ai-the-judge) · [8](#step-8--test-the-agent) · [9](#step-9--put-the-judge-on-trial) ·
[Bonus](#bonus) · [Quick fixes](#quick-fixes)

---

## 0 · Common commands

### Open a terminal in the project folder
Easiest: in VS Code, File > Open Folder > pick the project folder, then Terminal > New Terminal.

Or, in Terminal (Cmd+Space, type Terminal, Enter):

change to where YOU put the folder

```bash
cd ~/Downloads/shopkart-ai-tutorial-v2
```

(a GitHub ZIP unpacks to shopkart-ai-tutorial-v2-main: use that name)

you should see this file: you are in the right place

```bash
ls check_setup.py
```

### Set up (one time)
Expect Python 3.11, 3.12 or 3.13:

```bash
python3 --version
```

Before creating the venv, confirm Python runs and PATH works. Expect **Python is working**:

```bash
python3 -c "print('Python is working')"
```

Create `.venv`, install execution libraries, create `.env`, and run the initial setup check:

```bash
python3 setup_env.py
```

The setup script installs execution libraries (FastAPI, Uvicorn, OpenAI SDK, LangGraph, DeepEval and pytest) into `.venv`, not Python or VS Code. Its initial check uses the venv interpreter; finish the Groq settings before checking again.

Prefer to do it by hand? Run these four commands individually:
```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
```

In your already-open VS Code project, click `.env` in Explorer and paste your free Groq key (https://console.groq.com/keys) in **both** places that say `gsk_your_key_here` (`LLM_API_KEY` and `JUDGE_API_KEY`). Save. Use **Python: Select Interpreter** to choose `.venv`.

### Activate the virtual environment (EVERY new terminal)
your project folder

```bash
cd ~/Downloads/shopkart-ai-tutorial-v2
```

you now see (.venv) at the start of the line

```bash
source .venv/bin/activate
```

### Is my laptop ready?
Run this from the project folder **after activation**, while the terminal shows **`(.venv)`**. Every line OK means ready. A FAIL shows the FAQ number in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

```bash
python check_setup.py
```

**Only when you have finished** working, you can leave the venv with the following command. Do not run it before the tutorial scripts/tests; if you do, activate `.venv` again.
```bash
deactivate
```

### The three terminal windows (on the day)
| Window | What runs there | When | Activate the venv? |
|---|---|---|---|
| **1 · Ollama** | Ollama app or dedicated server terminal | local-model demo; prepare it before the event | no |
| **2 · Bot** | the current step's Uvicorn server (keeps the terminal busy) | steps 2 to 5, and steps 6 to 8 | **yes** |
| **3 · Work** | Python scripts and pytest commands from the current step | always | **yes** |

New window on Mac: Cmd+T (new tab) in Terminal.

### Start the bot (window 2)
```bash
cd build/step5_agent
```

the full bot with the agent crew. Open http://localhost:8000

```bash
uvicorn app:app --reload
```

Ctrl+C stops it

Port 8000 busy ("address already in use")?
stop whatever uses port 8000

```bash
lsof -ti :8000 | xargs kill
```

or use another port, and tell the tests (window 3):

```bash
uvicorn app:app --reload --port 8001
```

```bash
export SHOPKART_URL=http://localhost:8001
```

### Fell behind? Jump to a working step
the menu: step1 ... step9

```bash
python checkpoint.py
```

copies the finished files in place and tells you what to run next

```bash
python checkpoint.py step3
```

your own file is kept next to it as <name>.mine

### Break the bot on purpose (Part 2), and ALWAYS fix it after
list the bugs and show which one is active

```bash
python plant_bug.py
```

or: no_pages, skip_lookup, overpay, blind_reviewer, shared_memory, no_breaker, false_promise

```bash
python plant_bug.py liar
```

healthy again. No restart needed

```bash
python plant_bug.py off
```

### The scoreboard and "run everything"
from the project folder: all of Part 2 (the bot must be running)

```bash
pytest evaluate -v
```

every pytest run writes this page: green/red + the judge's scores and reasons (Linux: xdg-open)

```bash
open evaluate/report.html
```

### Run without the real model (practice, or bad internet)
```bash
cd tools
```

a pretend model and a pretend judge. Not smart, but the plumbing works

```bash
uvicorn fake_llm:app --port 9999
```

then, in .env:  LLM_BASE_URL=http://localhost:9999/v1   LLM_MODEL=fake   JUDGE_BASE_URL=http://localhost:9999/v1   JUDGE_MODEL=fake

### Ollama (required preparation on local laptops)
Install [Ollama](https://ollama.com/download), launch the app, and open a new terminal. Do this before the event for a possible local-model demo; Groq remains the default. Browser-only attendees use the Codespaces fallback above.

These commands do not require the Python venv. Expect a version number first:
```bash
ollama --version
```

Check **http://localhost:11434** for **Ollama is running**. If the app is not serving requests, start the server in window 1 and leave it open; run the remaining commands in another terminal:
window 1, leave it open. "address already in use" = it is already running: good

```bash
ollama serve
```

one time, about 2.5 GB. Do this at home, not on conference Wi-Fi

```bash
ollama pull qwen3:4b
```

the name in .env (LLM_MODEL) must match exactly

```bash
ollama list
```

Expect **qwen3:4b** in the model list, then test a real response:
```bash
ollama run qwen3:4b "Reply with one short greeting."
```

Expect a non-empty greeting; wording varies. Keep `.env` on Groq for normal checks. For the demo, switch providers using [FAQ #6](TROUBLESHOOTING.md#6--switching-between-groq-and-ollama); the judge stays on Groq.

---

## Which step needs what

| Step | Folder | Virtual env | Bot running (window 2)? | Internet |
|---|---|---|---|---|
| 1 · Brain | `build/step1_model` | yes | no | Groq (or Ollama) |
| 2 · Bridge | `build/step2_api` | yes | it **is** the server | Groq (or Ollama) |
| 3 · Browser | `build/step3_ui` | yes | it **is** the server | Groq (or Ollama) |
| 4 · Book | `build/step4_ground` | yes | it **is** the server | Groq (or Ollama) |
| 5 · Body | `build/step5_agent` | yes | it **is** the server | Groq (or Ollama) |
| 6 · Rules | `evaluate/step6_rules` | yes | **yes** (step 5 bot) | for the bot's model |
| 7 · AI judge | `evaluate/step7_judge` | yes | **yes** | bot's model **and** judge (Groq) |
| 8 · Agent | `evaluate/step8_agent` | yes | **yes** | bot's model; judge only for `task_completion` |
| 9 · Judge on trial | `evaluate/step9_trial` | yes | no | judge (Groq) |

---

# Part 1 · BUILD the bot

## Step 1 · Talk to the model
One call to the model: a system prompt + a question in, an answer out.
```bash
cd build/step1_model
```

core: one question, one answer

```bash
python ask_simple.py
```

stretch: the same call with 6 experiments (remove a # in the file, run, put it back)

```bash
python ask.py
```

```bash
cd ../..
```

**Done when:** it prints a real answer from ShopKart's assistant.

## Step 2 · Wrap it in an API
The same call behind a web address, so pages, tools and tests can use it. The terminal stays busy: that is the server.
```bash
cd build/step2_api
```

core. Open http://localhost:8000/docs > POST /chat > Try it out

```bash
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the stretch version (prints HOP 2/3/4 for every message):

```bash
uvicorn app:app --reload
```

Ctrl+C when done

```bash
cd ../..
```

**Done when:** `/docs` returns `{"reply": "...a real answer..."}`.

## Step 3 · Give it a face
A chat web page that calls your API. Stop any earlier `uvicorn` first (Ctrl+C): one thing per port.
```bash
cd build/step3_ui
```

core. Open http://localhost:8000 (after editing the HTML, just refresh)

```bash
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the full chat app (saved chats, Show JSON, Orders, ...):

```bash
uvicorn app:app --reload
```

Ctrl+C when done

```bash
cd ../..
```

**Done when:** you can chat in the browser and it remembers your name.

## Step 4 · Ground it
The librarian finds the right ShopKart policy pages and the model answers only from them (RAG).
```bash
cd build/step4_ground
```

no server needed: which pages does the librarian find?

```bash
python retrieval.py "Do you price-match?"
```

```bash
python retrieval.py "Can I return shoes after 20 days?"
```

core. Open http://localhost:8000 and ask "Do you price-match?"

```bash
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the full version:

```bash
uvicorn app:app --reload
```

Ctrl+C when done

```bash
cd ../..
```

**Done when:** "Do you price-match?" gets an honest "not in our policy" and the page shows the sources under the answer.

## Step 5 · Let it act
The bot gets tools (look up an order, issue a refund, escalate). Every step is recorded: the flight recorder that Part 2 tests.
```bash
cd build/step5_agent
```

core: broken headphones, 49 EUR, should end with action 'refund'

```bash
python agent_simple.py 1043
```

laptop, 899 EUR, should go to a human

```bash
python agent_simple.py 2001
```

all 10 seeded orders

```bash
python agent_simple.py all
```

open http://localhost:8000 and tick "Agent mode"

```bash
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the full crew (Planner > Implementer > Reviewer):

also: 2001, all, --graph

```bash
python agent.py 1043
```

LEAVE THIS RUNNING. Steps 6 to 8 test this bot

```bash
uvicorn app:app --reload
```

**Done when:** order 1043 ends in a refund, order 2001 goes to a human, and the full bot is running in window 2.

---

# Part 2 · TEST the bot

> **Window 2** keeps the step 5 bot running. Do all the commands below in **window 3**: a NEW terminal where you activate the venv again.
> Window 2 (skip if it is already running):
> ```bash
> cd ~/Downloads/shopkart-ai-tutorial-v2
> ```
>
>
> ```bash
> source .venv/bin/activate
> ```
>
>
> ```bash
> cd build/step5_agent
> ```
>
>
> ```bash
> uvicorn app:app --reload
> ```
>
>
> Window 3 (every Part 2 step starts like this):
> ```bash
> cd ~/Downloads/shopkart-ai-tutorial-v2
> ```
>
>
> ```bash
> source .venv/bin/activate
> ```
>
>

## Step 6 · Rules first
Plain Python rules: words the answer must say or must never say. No AI, free, instant.
```bash
cd evaluate/step6_rules
```

core: one question, two rules, PASS or FAIL (EXPERIMENT 1 = the liar)

```bash
python rules_simple.py
```

stretch: the same rules on all 10 golden questions

```bash
python -m pytest test_rules.py -v
```

break the REAL bot: price-match goes red

```bash
python ../../plant_bug.py liar
```

```bash
python -m pytest test_rules.py -v
```

always switch it off again

```bash
python ../../plant_bug.py off
```

```bash
cd ../..
```

**Done when:** experiment 1 prints FAIL with the forbidden phrase, and the normal run prints PASS.

## Step 7 · AI tests AI: the judge
A bigger model marks the answer with a rubric (DeepEval). Score 0 to 1, a pass mark, and the judge's reason. Needs internet for the judge.
```bash
cd evaluate/step7_judge
```

core: two scores and the judge's reasons (EXPERIMENT 1 = the liar, 2 = the poisoned page)

```bash
python judge_simple.py
```

stretch: one question first (several judge calls)

```bash
pytest test_judge.py -v -k price
```

stretch: all judge questions (slower)

```bash
pytest test_judge.py -v
```

the scoreboard: every score with its reason

```bash
open ../report.html
```

break the real bot, run the price question again

```bash
python ../../plant_bug.py liar
```

```bash
pytest test_judge.py -v -k price
```

```bash
python ../../plant_bug.py off
```

```bash
cd ../..
```

**Done when:** you have seen experiment 2 give one PASS and one FAIL, and can explain why.

## Step 8 · Test the agent
Check the journey, not just the landing: which tools ran, in which order, and the amount. Plus DeepEval's ready-made agent metric (`ToolCorrectnessMetric`) and a menu of the others at the bottom of the file.
```bash
cd evaluate/step8_agent
```

core: the flight recorder + the checks

```bash
python agent_check_simple.py
```

refund before lookup: the journey checks go red

```bash
python ../../plant_bug.py skip_lookup
```

```bash
python agent_check_simple.py
```

double refund: the money check goes red

```bash
python ../../plant_bug.py overpay
```

```bash
python agent_check_simple.py
```

always restore the healthy crew

```bash
python ../../plant_bug.py off
```

stretch: fast, no judge calls

```bash
pytest test_agents.py -v -k "not task_completion"
```

stretch: everything (uses the judge)

```bash
pytest test_agents.py -v
```

optional: all 10 orders instead of 3

```bash
export ALL_ORDERS=1
```

```bash
pytest test_agents.py -v -k "not task_completion"
```

back to 3 orders

```bash
unset ALL_ORDERS
```

```bash
cd ../..
```

**Done when:** `skip_lookup` makes the journey checks red, `overpay` makes the money check red, and `off` makes everything green again.

## Step 9 · Put the judge on trial
The judge is AI too, so it can be wrong. Put a **CAP** on it: **C**onsistent? (same answer scored 3 times) · **A**grees with you? · **P**rice (time and calls). The bot is not needed.
```bash
cd evaluate/step9_trial
```

FIRST open trial_simple.py and set MY_SCORE (0 = wrong, 1 = perfect). No peeking at the judge!

core: C, A and P for one answer

```bash
python trial_simple.py
```

For the stretch, FIRST score the 5 answers in my_scores.yaml yourself, then:

both judges (small local vs big hosted) against YOUR scores

```bash
python judge_the_judge.py --runs 2
```

```bash
cd ../..
```

**Done when:** you can say how much the judge wobbles (C), how far it is from you (A) and what 3 verdicts cost in seconds (P).

---

## Bonus

optional: LangSmith cloud UI (needs an account, see extras/langsmith/README.md)

```bash
python extras/langsmith/langsmith_eval.py
```

presenter: do the step folders still fit together?

```bash
python tools/check_steps.py
```

## Quick fixes
| Problem | Fix |
|---|---|
| No `(.venv)` at the start of the line | **Command 1** (from the project folder) |
| `python: command not found` | use `python3` to create the venv; once `(.venv)` is active, `python` works |
| `ModuleNotFoundError` | the venv is not active, or run **Command 2** |
| Tests say "connection refused" | the bot is not running: start it in window 2 (see above) |
| "address already in use" | **Command 3** |
| SSL / certificate errors | TROUBLESHOOTING #17 |
| Judge says 429 / rate limit | wait a minute, or **Command 4** (TROUBLESHOOTING #14) |
| Tests red for no reason | a bug is still planted: **Command 5** (TROUBLESHOOTING #19) |
| Anything else | **Command 6**, then look up the FAQ number it prints in [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

**Command 1**

```bash
source .venv/bin/activate
```

**Command 2**

```bash
pip install -r requirements.txt
```

**Command 3**

```bash
lsof -ti :8000 | xargs kill
```

**Command 4**

```bash
python judge_the_judge.py --runs 1
```

**Command 5**

```bash
python plant_bug.py off
```

**Command 6**

```bash
python check_setup.py
```
