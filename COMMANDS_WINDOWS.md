# ShopKart tutorial · all commands (Windows · PowerShell)

**If you get stuck anywhere, contact [Gaurav Khurana on LinkedIn](https://www.linkedin.com/in/gauravkhuraana/).**

Can't message on LinkedIn? Email: **gaurav [dot] khuraana [at] gmail [dot] com** (replace `[dot]` with `.` and `[at]` with `@`, then remove the spaces).

One page, steps 1 to 9, in order. **Copy a block, paste it, read the one-line explanation.**
Mac user? Use [COMMANDS_MAC.md](COMMANDS_MAC.md). Stuck? [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Using the tutorial

- **Local laptop:** install and test Python, VS Code and Ollama using [PRE_CONFERENCE.md](PRE_CONFERENCE.md). Open the project with **File → Open Folder**, then **Terminal → New Terminal** in VS Code.
- **Every new tutorial terminal:** start in the project folder and activate `.venv` using the commands below before Python scripts or tests. The initial base-Python installation tests and setup script are the exceptions.
- **Bot:** follow the current step's commands. The server keeps its terminal busy; keep it open and use another activated terminal for tests. Press **Ctrl+C** before switching server versions/steps.
- **Local scoreboard:** after a pytest run, open `evaluate\report.html` in your browser.

### GitHub Codespaces (even when your laptop runs Windows)

A Codespace runs **Linux**, not Windows. Use [the Mac/Linux command guide](COMMANDS_MAC.md#using-the-tutorial) for activation and all tutorial commands; do not paste PowerShell commands from this page into its terminal. VS Code opens in your browser and prepares the environment automatically.

When the bot starts, open forwarded port **8000** for the chat page. For the scoreboard, follow the [Mac/Linux scoreboard instructions](COMMANDS_MAC.md#github-codespaces-browser-users-including-windows-laptops): start the HTTP server from the project folder, open forwarded port **8080**, and click **report.html**.

The browser fallback uses **Groq**, not Ollama on your laptop. Stop the Codespace when finished (bottom-left menu → **Stop Current Codespace**) to save free hours. Corporate accounts sometimes block Codespaces; use a personal laptop/account where permitted, or pair with a neighbour.

**How to read this page**
- Unless a setup section says otherwise, start each step in the **project folder** (the one that contains `check_setup.py`) with **`(.venv)`** active, then follow the directory changes in order.
- After a step, return to the project folder:

  ```powershell
  cd ..\..
  ```

- Each code block contains one command. Read the explanation beside it before copying the next command.

**Contents**
[0 · Common commands](#0--common-commands) · [Which step needs what](#which-step-needs-what) ·
[1](#step-1--talk-to-the-model) · [2](#step-2--wrap-it-in-an-api) · [3](#step-3--give-it-a-face) · [4](#step-4--ground-it) · [5](#step-5--let-it-act) ·
[6](#step-6--rules-first) · [7](#step-7--ai-tests-ai-the-judge) · [8](#step-8--test-the-agent) · [9](#step-9--put-the-judge-on-trial) ·
[Bonus](#bonus) · [Quick fixes](#quick-fixes)

---

## 0 · Common commands

### Open a terminal in the project folder
Easiest: in VS Code, File > Open Folder > pick the project folder, then Terminal > New Terminal.

Or, in PowerShell (Start, type PowerShell):

change to where YOU put the folder

```powershell
cd C:\Users\YourName\Downloads\shopkart-ai-tutorial-v2
```

(a GitHub ZIP unpacks to shopkart-ai-tutorial-v2-main: use that name)

you should see this file: you are in the right place

```powershell
dir check_setup.py
```

### Set up (one time)
Expect Python 3.11, 3.12 or 3.13:

```powershell
python --version
```

Before creating the venv, confirm Python runs and PATH works. Expect **Python is working**:

```powershell
python -c "print('Python is working')"
```

Create `.venv`, install execution libraries, create `.env`, and run the initial setup check:

```powershell
python setup_env.py
```

The setup script installs execution libraries (FastAPI, Uvicorn, OpenAI SDK, LangGraph, DeepEval and pytest) into `.venv`, not Python or VS Code. Its initial check uses the venv interpreter; finish the Groq settings before checking again.

Prefer to do it by hand? Run these four commands individually:
```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

```powershell
pip install -r requirements.txt
```

```powershell
copy .env.example .env
```

In your already-open VS Code project, click `.env` in Explorer and paste your free Groq key (https://console.groq.com/keys) in **both** places that say `gsk_your_key_here` (`LLM_API_KEY` and `JUDGE_API_KEY`). Save, then use **Python: Select Interpreter** to choose `.venv`.

### Activate the virtual environment (EVERY new terminal)
your project folder

```powershell
cd C:\Users\YourName\Downloads\shopkart-ai-tutorial-v2
```

you now see (.venv) at the start of the line

```powershell
.venv\Scripts\Activate.ps1
```

"Running scripts is disabled on this system"? Run this once, then activate again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Or use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### Is my laptop ready?
Run this from the project folder **after activation**, while the terminal shows **`(.venv)`**. Every line OK means ready. A FAIL shows the FAQ number in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

```powershell
python check_setup.py
```

**Only when you have finished** working, you can leave the venv with the following command. Do not run it before the tutorial scripts/tests; if you do, activate `.venv` again.
```powershell
deactivate
```

### The three terminal windows (on the day)
| Window | What runs there | When | Activate the venv? |
|---|---|---|---|
| **1 · Ollama** | Ollama app or dedicated server terminal | local-model demo; prepare it before the event | no |
| **2 · Bot** | the current step's Uvicorn server (keeps the terminal busy) | steps 2 to 5, and steps 6 to 8 | **yes** |
| **3 · Work** | Python scripts and pytest commands from the current step | always | **yes** |

### Start the bot (window 2)
```powershell
cd build\step5_agent
```

the full bot with the agent crew. Open http://localhost:8000

```powershell
uvicorn app:app --reload
```

Ctrl+C stops it

Port 8000 busy ("address already in use")?
stop whatever uses it

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess }
```

or use another port, and tell the tests (window 3):

```powershell
uvicorn app:app --reload --port 8001
```

```powershell
$env:SHOPKART_URL="http://localhost:8001"
```

### Fell behind? Jump to a working step
the menu: step1 ... step9

```powershell
python checkpoint.py
```

copies the finished files in place and tells you what to run next

```powershell
python checkpoint.py step3
```

your own file is kept next to it as <name>.mine

### Break the bot on purpose (Part 2), and ALWAYS fix it after
list the bugs and show which one is active

```powershell
python plant_bug.py
```

or: no_pages, skip_lookup, overpay, blind_reviewer, shared_memory, no_breaker, false_promise

```powershell
python plant_bug.py liar
```

healthy again. No restart needed

```powershell
python plant_bug.py off
```

### The scoreboard and "run everything"
from the project folder: all of Part 2 (the bot must be running)

```powershell
pytest evaluate -v
```

every pytest run writes this page: green/red + the judge's scores and reasons

```powershell
start evaluate\report.html
```

### Run without the real model (practice, or bad internet)
```powershell
cd tools
```

a pretend model and a pretend judge. Not smart, but the plumbing works

```powershell
uvicorn fake_llm:app --port 9999
```

then, in .env:  LLM_BASE_URL=http://localhost:9999/v1   LLM_MODEL=fake   JUDGE_BASE_URL=http://localhost:9999/v1   JUDGE_MODEL=fake

### Ollama (required preparation on local laptops)
Install [Ollama](https://ollama.com/download), launch the app, and open a new PowerShell terminal. Do this before the event for a possible local-model demo; Groq remains the default. Browser-only attendees use the Codespaces fallback above.

These commands do not require the Python venv. Expect a version number first:
```powershell
ollama --version
```

Check **http://localhost:11434** for **Ollama is running**. If the app is not serving requests, start the server in window 1 and leave it open; run the remaining commands in another terminal:
window 1, leave it open. "address already in use" = it is already running: good

```powershell
ollama serve
```

one time, about 2.5 GB. Do this at home, not on conference Wi-Fi

```powershell
ollama pull qwen3:4b
```

the name in .env (LLM_MODEL) must match exactly

```powershell
ollama list
```

Expect **qwen3:4b** in the model list, then test a real response:
```powershell
ollama run qwen3:4b "Reply with one short greeting."
```

Expect a non-empty greeting; wording varies. Keep `.env` on Groq for normal checks. For the demo, switch providers using [FAQ #6](TROUBLESHOOTING.md#6--switching-between-groq-and-ollama); the judge stays on Groq.

---

## Which step needs what

| Step | Folder | Virtual env | Bot running (window 2)? | Internet |
|---|---|---|---|---|
| 1 · Brain | `build\step1_model` | yes | no | Groq (or Ollama) |
| 2 · Bridge | `build\step2_api` | yes | it **is** the server | Groq (or Ollama) |
| 3 · Browser | `build\step3_ui` | yes | it **is** the server | Groq (or Ollama) |
| 4 · Book | `build\step4_ground` | yes | it **is** the server | Groq (or Ollama) |
| 5 · Body | `build\step5_agent` | yes | it **is** the server | Groq (or Ollama) |
| 6 · Rules | `evaluate\step6_rules` | yes | **yes** (step 5 bot) | for the bot's model |
| 7 · AI judge | `evaluate\step7_judge` | yes | **yes** | bot's model **and** judge (Groq) |
| 8 · Agent | `evaluate\step8_agent` | yes | **yes** | bot's model; judge only for `task_completion` |
| 9 · Judge on trial | `evaluate\step9_trial` | yes | no | judge (Groq) |

---

# Part 1 · BUILD the bot

## Step 1 · Talk to the model
One call to the model: a system prompt + a question in, an answer out.
```powershell
cd build\step1_model
```

core: one question, one answer

```powershell
python ask_simple.py
```

stretch: the same call with 6 experiments (remove a # in the file, run, put it back)

```powershell
python ask.py
```

```powershell
cd ..\..
```

**Done when:** it prints a real answer from ShopKart's assistant.

## Step 2 · Wrap it in an API
The same call behind a web address, so pages, tools and tests can use it. The terminal stays busy: that is the server.
```powershell
cd build\step2_api
```

core. Open http://localhost:8000/docs > POST /chat > Try it out

```powershell
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the stretch version (prints HOP 2/3/4 for every message):

```powershell
uvicorn app:app --reload
```

Ctrl+C when done

```powershell
cd ..\..
```

**Done when:** `/docs` returns `{"reply": "...a real answer..."}`.

## Step 3 · Give it a face
A chat web page that calls your API. Stop any earlier `uvicorn` first (Ctrl+C): one thing per port.
```powershell
cd build\step3_ui
```

core. Open http://localhost:8000 (after editing the HTML, just refresh)

```powershell
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the full chat app (saved chats, Show JSON, Orders, ...):

```powershell
uvicorn app:app --reload
```

Ctrl+C when done

```powershell
cd ..\..
```

**Done when:** you can chat in the browser and it remembers your name.

## Step 4 · Ground it
The librarian finds the right ShopKart policy pages and the model answers only from them (RAG).
```powershell
cd build\step4_ground
```

no server needed: which pages does the librarian find?

```powershell
python retrieval.py "Do you price-match?"
```

```powershell
python retrieval.py "Can I return shoes after 20 days?"
```

core. Open http://localhost:8000 and ask "Do you price-match?"

```powershell
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the full version:

```powershell
uvicorn app:app --reload
```

Ctrl+C when done

```powershell
cd ..\..
```

**Done when:** "Do you price-match?" gets an honest "not in our policy" and the page shows the sources under the answer.

## Step 5 · Let it act
The bot gets tools (look up an order, issue a refund, escalate). Every step is recorded: the flight recorder that Part 2 tests.
```powershell
cd build\step5_agent
```

core: broken headphones, 49 EUR, should end with action 'refund'

```powershell
python agent_simple.py 1043
```

laptop, 899 EUR, should go to a human

```powershell
python agent_simple.py 2001
```

all 10 seeded orders

```powershell
python agent_simple.py all
```

open http://localhost:8000 and tick "Agent mode"

```powershell
uvicorn app_simple:app --reload
```

Ctrl+C to stop, then the full crew (Planner > Implementer > Reviewer):

also: 2001, all, --graph

```powershell
python agent.py 1043
```

LEAVE THIS RUNNING. Steps 6 to 8 test this bot

```powershell
uvicorn app:app --reload
```

**Done when:** order 1043 ends in a refund, order 2001 goes to a human, and the full bot is running in window 2.

---

# Part 2 · TEST the bot

> **Window 2** keeps the step 5 bot running. Do all the commands below in **window 3**: a NEW terminal where you activate the venv again.
> Window 2 (skip if it is already running):
> ```powershell
> cd C:\Users\YourName\Downloads\shopkart-ai-tutorial-v2
> ```
>
>
> ```powershell
> .venv\Scripts\Activate.ps1
> ```
>
>
> ```powershell
> cd build\step5_agent
> ```
>
>
> ```powershell
> uvicorn app:app --reload
> ```
>
>
> Window 3 (every Part 2 step starts like this):
> ```powershell
> cd C:\Users\YourName\Downloads\shopkart-ai-tutorial-v2
> ```
>
>
> ```powershell
> .venv\Scripts\Activate.ps1
> ```
>
>

## Step 6 · Rules first
Plain Python rules: words the answer must say or must never say. No AI, free, instant.
```powershell
cd evaluate\step6_rules
```

core: one question, two rules, PASS or FAIL (EXPERIMENT 1 = the liar)

```powershell
python rules_simple.py
```

stretch: the same rules on all 10 golden questions

```powershell
python -m pytest test_rules.py -v
```

break the REAL bot: price-match goes red

```powershell
python ..\..\plant_bug.py liar
```

```powershell
python -m pytest test_rules.py -v
```

always switch it off again

```powershell
python ..\..\plant_bug.py off
```

```powershell
cd ..\..
```

**Done when:** experiment 1 prints FAIL with the forbidden phrase, and the normal run prints PASS.

## Step 7 · AI tests AI: the judge
A bigger model marks the answer with a rubric (DeepEval). Score 0 to 1, a pass mark, and the judge's reason. Needs internet for the judge.
```powershell
cd evaluate\step7_judge
```

core: two scores and the judge's reasons (EXPERIMENT 1 = the liar, 2 = the poisoned page)

```powershell
python judge_simple.py
```

stretch: one question first (several judge calls)

```powershell
pytest test_judge.py -v -k price
```

stretch: all judge questions (slower)

```powershell
pytest test_judge.py -v
```

the scoreboard: every score with its reason

```powershell
start ..\report.html
```

break the real bot, run the price question again

```powershell
python ..\..\plant_bug.py liar
```

```powershell
pytest test_judge.py -v -k price
```

```powershell
python ..\..\plant_bug.py off
```

```powershell
cd ..\..
```

**Done when:** you have seen experiment 2 give one PASS and one FAIL, and can explain why.

## Step 8 · Test the agent
Check the journey, not just the landing: which tools ran, in which order, and the amount. Plus DeepEval's ready-made agent metric (`ToolCorrectnessMetric`) and a menu of the others at the bottom of the file.
```powershell
cd evaluate\step8_agent
```

core: the flight recorder + the checks

```powershell
python agent_check_simple.py
```

refund before lookup: the journey checks go red

```powershell
python ..\..\plant_bug.py skip_lookup
```

```powershell
python agent_check_simple.py
```

double refund: the money check goes red

```powershell
python ..\..\plant_bug.py overpay
```

```powershell
python agent_check_simple.py
```

always restore the healthy crew

```powershell
python ..\..\plant_bug.py off
```

stretch: fast, no judge calls

```powershell
pytest test_agents.py -v -k "not task_completion"
```

stretch: everything (uses the judge)

```powershell
pytest test_agents.py -v
```

optional: all 10 orders instead of 3

```powershell
$env:ALL_ORDERS=1
```

```powershell
pytest test_agents.py -v -k "not task_completion"
```

back to 3 orders

```powershell
Remove-Item Env:ALL_ORDERS
```

```powershell
cd ..\..
```

**Done when:** `skip_lookup` makes the journey checks red, `overpay` makes the money check red, and `off` makes everything green again.

## Step 9 · Put the judge on trial
The judge is AI too, so it can be wrong. Put a **CAP** on it: **C**onsistent? (same answer scored 3 times) · **A**grees with you? · **P**rice (time and calls). The bot is not needed.
```powershell
cd evaluate\step9_trial
```

FIRST open trial_simple.py and set MY_SCORE (0 = wrong, 1 = perfect). No peeking at the judge!

core: C, A and P for one answer

```powershell
python trial_simple.py
```

For the stretch, FIRST score the 5 answers in my_scores.yaml yourself, then:

both judges (small local vs big hosted) against YOUR scores

```powershell
python judge_the_judge.py --runs 2
```

```powershell
cd ..\..
```

**Done when:** you can say how much the judge wobbles (C), how far it is from you (A) and what 3 verdicts cost in seconds (P).

---

## Bonus

optional: LangSmith cloud UI (needs an account, see extras\langsmith\README.md)

```powershell
python extras\langsmith\langsmith_eval.py
```

presenter: do the step folders still fit together?

```powershell
python tools\check_steps.py
```

## Quick fixes
| Problem | Fix |
|---|---|
| No `(.venv)` at the start of the line | **Command 1** (from the project folder) |
| "running scripts is disabled" | **Command 2**, then activate again |
| `ModuleNotFoundError` | the venv is not active, or run **Command 3** |
| Tests say "connection refused" | the bot is not running: start it in window 2 (see above) |
| "address already in use" | **Command 4** |
| Judge says 429 / rate limit | wait a minute, or **Command 5** (TROUBLESHOOTING #14) |
| Tests red for no reason | a bug is still planted: **Command 6** (TROUBLESHOOTING #19) |
| Anything else | **Command 7**, then look up the FAQ number it prints in [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

**Command 1**

```powershell
.venv\Scripts\Activate.ps1
```

**Command 2**

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Command 3**

```powershell
pip install -r requirements.txt
```

**Command 4**

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess }
```

**Command 5**

```powershell
python judge_the_judge.py --runs 1
```

**Command 6**

```powershell
python plant_bug.py off
```

**Command 7**

```powershell
python check_setup.py
```
