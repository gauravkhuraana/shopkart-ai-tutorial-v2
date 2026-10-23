# Poison Kills Poison: AI Tests AI

Hands-on tutorial · AutomationSTAR 2026 · Gaurav Khurana · #SharingIsCaring

**If you get stuck anywhere, contact [Gaurav Khurana on LinkedIn](https://www.linkedin.com/in/gauravkhuraana/).**

Can't message on LinkedIn? Email: **gaurav [dot] khuraana [at] gmail [dot] com** (replace `[dot]` with `.` and `[at]` with `@`, then remove the spaces).

**What you will do today**
1. **Build** a small AI helper for a pretend online shop called **ShopKart**. It answers refund questions. You build it in 5 small steps.
2. **Test** it. First with simple rule checks, then with a second AI that acts as the "judge".

Everything is free and runs on your own laptop (or in your browser).

**Quick links:** [PRE_CONFERENCE.md](PRE_CONFERENCE.md) (get ready, 8 days before) · [COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md) · [COMMANDS_MAC.md](COMMANDS_MAC.md) (every command, steps 1 to 9) · [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Table of contents

- [Before the tutorial: set up your laptop (about 20 to 30 minutes)](#before-the-tutorial-set-up-your-laptop-about-20-to-30-minutes)
- [On the day: two ways to follow along (terminal or notebook)](#on-the-day-two-ways-to-follow-along-terminal-or-notebook)
- [On the day: the terminal windows you need](#on-the-day-the-terminal-windows-you-need)
- [Part 1 · BUILD the bot (5 steps)](#part-1--build-the-bot-5-steps)
- [Part 2 · TEST the bot (4 steps)](#part-2--test-the-bot-4-steps)
- [All steps at a glance](#all-steps-at-a-glance)
- [Cheat sheet: the other commands](#cheat-sheet-the-other-commands)
- [Stuck?](#stuck)
- [What's in this project](#whats-in-this-project)
- [Want to build it again later? The 9 ideas](#want-to-build-it-again-later-the-9-ideas)
- [Credits & licence](#credits--licence)

## Before the tutorial: set up your laptop (about 20 to 30 minutes)

Please do this **at home**, in the week before the tutorial. **Follow [PRE_CONFERENCE.md](PRE_CONFERENCE.md)**: it is the one setup guide, step by step.

> **Tip:** links open on the same page. **Ctrl+click** a link (Mac: **Cmd+click**) to open it in a new tab, so you do not lose your place.

**Two ways to get ready:**
- **Path A · install on your laptop** (recommended): Python 3.12, VS Code, one setup command, a free Groq key, and Ollama for an optional demo. Choose this if it is your own laptop, or your work laptop lets you install programs.
- **Path B · use it in the browser** with GitHub Codespaces: nothing to install, but you must be **signed in to GitHub** (a free account). Choose this if you are **not allowed to install programs**, or Path A keeps failing.

**You are ready when** this command, run from the project folder with `(.venv)` active, prints **OK** on every line:

```bash
python check_setup.py
```

> **What is a terminal?** A window where you type commands.
> Windows: press Start, type **PowerShell**, press Enter. Mac: press Cmd+Space, type **Terminal**, press Enter.

## On the day: two ways to follow along (terminal or notebook)

Both ways run **the same steps 1 to 9 on the same files**. Pick one, and stay with it for the day.

| | **Terminal path** | **Notebook path** (press ▶) |
|---|---|---|
| How | type the commands from [COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md) / [COMMANDS_MAC.md](COMMANDS_MAC.md) | open **[workshop.ipynb](workshop.ipynb)** and press ▶ on each cell |
| The bot (steps 2 to 9) | runs in terminal window 2 | runs in the background, started by a cell |
| TODOs | uncomment them in the real files | the same: uncomment them in the real files, then press ▶ |
| Fell behind? | `python checkpoint.py step3` | the **Short on time?** cell of that step |
| Works in | your laptop (Path A) and GitHub Codespaces (Path B) | the same |

**First time with a notebook?** Open `workshop.ipynb`, click the first grey code cell, press ▶ (or Shift+Enter). If VS Code asks for a kernel, pick **.venv**. The notebook explains the rest.

> **Don't mix them:** only one bot fits on port 8000. A bot started in a terminal and a bot started by the notebook will collide.

## On the day: the terminal windows you need

| Window | What runs there | When |
|---|---|---|
| **1 · Ollama** | Ollama app or dedicated server terminal | local-model demo; keep it ready, but Groq stays the default |
| **2 · Bot** | the current step's Uvicorn server | steps 2 to 5, and all of Part 2 |
| **3 · Work** | Python scripts and pytest commands from the current step | always |

Remember: in windows 2 and 3, activate `.venv` first (Windows: `.venv\Scripts\Activate.ps1` · Mac/Linux: `source .venv/bin/activate`).

---

## Part 1 · BUILD the bot (5 steps)

Each step has its own folder. Each folder has a **README.md** that tells you:
**what to do** · **how to run it** · **how you know you're done**.

| Step | What you add | Folder | File you edit | Time |
|---|---|---|---|---|
| 1 · **Brain** | Talk to the AI model | [`build/step1_model`](build/step1_model/README.md) | `ask_simple.py` (then experiments in `ask.py`) | 8 min |
| 2 · **Bridge** | Put it behind a web API | [`build/step2_api`](build/step2_api/README.md) | `app_simple.py` (then experiments in `app.py`) | 10 min |
| 3 · **Browser** | Give it a chat page | [`build/step3_ui`](build/step3_ui/README.md) | `index_simple.html` (then `index.html`) | 5 min |
| 4 · **Book** | Make it answer from ShopKart's rules | [`build/step4_ground`](build/step4_ground/README.md) | `app_simple.py` (then `app.py`) | 12 min |
| 5 · **Body** | Let it take actions (refund, or ask a human) | [`build/step5_agent`](build/step5_agent/README.md) | `agent_simple.py` (then `agent.py`) | 18 min |

**How it works**
- In each file, look for the lines marked **`TODO`**. That's where you write code.
- Every folder already has the **finished** code of the step before it. So each step works on its own.
- **Fell behind? No problem.** Run this from the project folder, and the finished file is copied in for you:
  ```bash
  python checkpoint.py step3
  ```

  Your own file is kept as `<name>.mine`. It also tells you what to run next.
- All finished code is in [`solutions/`](solutions/README.md).
- All settings are in one file: `.env`.

---

## Part 2 · TEST the bot (4 steps)

**First, start your step 5 bot in window 2 and leave it running:**
```bash
cd build/step5_agent
```

```bash
uvicorn app:app --reload
```

**Then make sure the full crew is finished.** Part 2 tests `build/step5_agent/agent.py`. If you did not uncomment its three blocks in step 5, run this in window 3 from the project folder (your own files are kept as `.mine`):

```bash
python checkpoint.py step5
```

Then work in window 3. Same pattern as Part 1: one folder per step, a **simple** file we walk through together, then a **full** file if you finish early. Each folder has a **README.md**.

| Step | What you test | Easy way to remember | Folder | Simple file → full file | Time |
|---|---|---|---|---|---|
| 6 · **Rules** | words it must say / must never say | airport security: the metal detector | [`evaluate/step6_rules`](evaluate/step6_rules/README.md) | `rules_simple.py` → `test_rules.py` | 8 min |
| 7 · **AI judge** | is the answer true? (DeepEval) | **Is it TRUE?** Truthful · Relevant · Uses the source · Even | [`evaluate/step7_judge`](evaluate/step7_judge/README.md) | `judge_simple.py` → `test_judge.py` | 13 min |
| 8 · **Agent** | the journey, not just the landing | **Real Teams Make Outcomes Outstanding** (5 layers) | [`evaluate/step8_agent`](evaluate/step8_agent/README.md) | `agent_check_simple.py` → `test_agents.py` | 22 min |
| 9 · **Judge on trial** | can we trust the judge? | **CAP**: Consistent · Agrees · Price | [`evaluate/step9_trial`](evaluate/step9_trial/README.md) | `trial_simple.py` → `judge_the_judge.py` | 17 min |

**See your bot scored in your browser.** Every pytest run in Part 2 writes **`evaluate/report.html`**: green/red per test, and every judge score with its reason. Open it and leave it open: it refreshes itself. No account, nothing leaves your laptop.

Overview of Part 2: [evaluate/README.md](evaluate/README.md).

---

## All steps at a glance

Copy-paste commands for every step, for your system: **[COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md)** · **[COMMANDS_MAC.md](COMMANDS_MAC.md)**. Each step folder's README starts with individually copyable commands.
Every row starts from the project folder with `(.venv)` active. Windows paths use `\`, Mac paths use `/`.

| Step | Folder | Individually copyable commands | Bot running first? |
|---|---|---|---|
| 1 · Brain | `build/step1_model` | [Run step 1](build/step1_model/README.md) | no |
| 2 · Bridge | `build/step2_api` | [Run step 2](build/step2_api/README.md) | it **is** the server |
| 3 · Browser | `build/step3_ui` | [Run step 3](build/step3_ui/README.md) | it **is** the server |
| 4 · Book | `build/step4_ground` | [Run step 4](build/step4_ground/README.md) | it **is** the server |
| 5 · Body | `build/step5_agent` | [Run step 5](build/step5_agent/README.md), then leave the full bot running | it **is** the server |
| 6 · Rules | `evaluate/step6_rules` | [Run step 6](evaluate/step6_rules/README.md) | **yes** |
| 7 · AI judge | `evaluate/step7_judge` | [Run step 7](evaluate/step7_judge/README.md) | **yes** |
| 8 · Agent | `evaluate/step8_agent` | [Run step 8](evaluate/step8_agent/README.md) | **yes** |
| 9 · Judge on trial | `evaluate/step9_trial` | [Run step 9](evaluate/step9_trial/README.md) | no |

From a step folder, return to the project folder:

```bash
cd ../..
```


## Cheat sheet: the other commands

These are **independent shortcuts**, not a sequence to run top to bottom. Except for initial setup, activate `.venv` first.

**Initial setup, from the project folder (Windows):** creates `.venv`, installs execution libraries and creates `.env`.

```powershell
py -3.12 setup_env.py
```

**Initial setup, from the project folder (Mac/Linux):**

```bash
python3.12 setup_env.py
```

**Readiness check, from the project folder with `.venv` active:**

```bash
python check_setup.py
```

**Fell behind?** Get the finished step from the project folder:

```bash
python checkpoint.py step3
```

**Step 1**, inside `build/step1_model`: the model call with six experiments.

```bash
python ask.py
```

**Step 4**, inside `build/step4_ground`: which policy pages does the librarian find?

```bash
python retrieval.py "price match"
```

**Step 5**, inside `build/step5_agent`: let the crew handle order 1043 (other arguments include `all` and `--graph`).

```bash
python agent.py 1043
```

**Part 2**, inside an evaluation step folder, with the step 5 bot running: break the bot on purpose.

```bash
python ../../plant_bug.py liar
```

Always restore the healthy bot afterwards, from that same step folder:

```bash
python ../../plant_bug.py off
```

**Run all of Part 2**, from the project folder with the step 5 bot running (`-v` = verbose: show each test's name and PASSED/FAILED):

```bash
pytest evaluate -v
```

Then open `evaluate/report.html` in your browser.

## Stuck?

1. Look in [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Most problems are there.
2. Jump to a finished step from the project folder (replace `step3` with `step1` through `step9`):

   ```bash
   python checkpoint.py step3
   ```

3. Ask your neighbour. Nobody gets left behind.

---

## What's in this project

| Folder / file | What it is |
|---|---|
| `build/step1_model` … `build/step5_agent` | the 5 build steps (Part 1). Each has a README |
| `evaluate/step6_rules` … `evaluate/step9_trial` | the 4 test steps (Part 2). Each has a README |
| `evaluate/golden_questions.yaml` | the answer key for steps 6 and 7 |
| `evaluate/report.html` | your scoreboard, written by every pytest run in Part 2 |
| `solutions/` | the finished code for every step (1-9) |
| `extras/langsmith/` | optional: the same evaluation in LangSmith's cloud UI (needs an account) |
| `shared/config.py` | reads your settings from `.env` (which model, which judge) |
| `shared/data/policies/` | ShopKart's 10 rule pages (refunds, returns...) |
| `shared/data/orders.json` | 10 example orders to test with |
| [plant_bug.py](plant_bug.py) | switch bugs on and off for Part 2; [visual guide, code locations, and demo commands](plant_bug_README.md) |
| `workshop.ipynb` | the notebook path: the same steps 1 to 9, press ▶ instead of typing commands |
| `tools/notebook_helpers.py` | the small functions the notebook cells call (run a step, start/stop the bot, check TODOs) |
| `checkpoint.py` | copy in the finished code if you fall behind |
| `check_setup.py` | checks if your laptop is ready |
| `setup_env.py` | one-command setup: virtual environment, packages, `.env` |
| `PRE_CONFERENCE.md` | how to get ready before the day (own laptop, or in the browser) |
| `COMMANDS_WINDOWS.md` · `COMMANDS_MAC.md` | every command for steps 1 to 9, copy-paste ready |
| `.devcontainer/` | settings for running the tutorial in GitHub Codespaces (browser) |
| `tools/` | repository checks, regression tests and a fake model for offline practice |

## Want to build it again later? The 9 ideas

1. **Call a model.** A few lines of code with the OpenAI library. *(step 1)*
2. **Give it a job description.** Tell it its role, its topic, and its rules. *(step 1)*
3. **Give it memory.** Send the whole chat every time. *(step 2)*
4. **Put it behind an API**, so web pages, tools and tests can use it. *(step 2)*
5. **Give it a face.** A web page that calls the API. *(step 3)*
6. **Give it the book.** Find the right rule pages and tell the AI to answer only from them. *(step 4)*
7. **Give it tools.** The AI *asks* for an action, your code *does* it. Put hard rules in code, not in the prompt. *(step 5)*
8. **Split the work and record every step.** Request Planner → Case Investigator → Policy Reviewer. The record makes it testable. *(step 5)*
9. **Test from the bottom up, and plant bugs on purpose.** Rule checks first, then an AI judge, then the agent's journey, then test the judge. *(steps 6-9)*

## Credits & licence
Built for AutomationSTAR 2026 by Gaurav Khurana ([gauravkhurana.com](https://gauravkhurana.com)). ShopKart, its orders and its rules are made up.
Tools used: FastAPI, OpenAI Python SDK, LangGraph, DeepEval, pytest, Ollama. Optional extra: LangSmith.
