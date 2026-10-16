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

## Before the tutorial: set up your laptop (about 20 minutes)

Please do this **at home**, before the day. The Python libraries are about 150 MB. Local attendees must also download the Ollama model (about 2.5 GB) so we can demo it if the session allows.

**Two ways to get ready** (full step-by-step in [PRE_CONFERENCE.md](PRE_CONFERENCE.md)):
- **Path A · your own laptop** (below): install and test Python, install VS Code and Ollama, then use the setup script to install the execution libraries.
- **Path B · in the browser** with GitHub Codespaces: nothing to install, for locked-down laptops. See [PRE_CONFERENCE.md](PRE_CONFERENCE.md).

### Step 1 · Install Python and VS Code; get Git if needed

| Program | Where to get it | Note |
|---|---|---|
| **Python** 3.11, 3.12 or 3.13 | https://www.python.org/downloads/ | Windows: tick **"Add python.exe to PATH"** during install |
| **VS Code** | https://code.visualstudio.com/download | Install the **Python** extension published by **Microsoft** |
| **Git** | https://git-scm.com/downloads | Or skip Git and download this project as a ZIP |

**Test Python immediately after installing it**, before downloading the project. Open a **new terminal** so it picks up PATH changes.

**Windows**
```powershell
python --version
```

```powershell
python -c "print('Python is working')"
```

**Mac / Linux**
```bash
python3 --version
```

```bash
python3 -c "print('Python is working')"
```

Expect Python **3.11, 3.12 or 3.13**, then **Python is working**. These tests run with base Python before a venv exists. If either fails, fix [FAQ #1](TROUBLESHOOTING.md#1--wrong-python-version) before continuing.

> **What is a terminal?** A window where you type commands.
> Windows: press Start, type **PowerShell**, press Enter. Mac: press Cmd+Space, type **Terminal**, press Enter.

### Step 2 · Install and test Ollama (required on local laptops)

Install [Ollama](https://ollama.com/download), launch its app, and open a new terminal. Prepare it at home for a possible local-model demo. **Groq remains the default** for the bot and judge; installing Ollama does not change `.env`. Browser-only or restricted-laptop attendees can use the Codespaces/Groq fallback in [PRE_CONFERENCE.md](PRE_CONFERENCE.md).

**a) Check installation.** Expect an Ollama version number:
```text
ollama --version
```

**b) Check that Ollama is running.** Open **http://localhost:11434** in your web browser. It should say **Ollama is running**. If the app is not serving requests, run this in a dedicated terminal:
```bash
ollama serve
```

**Leave this window open** all the time you use the tutorial. Ollama works in this window. If you close it, Ollama stops.

> It says `address already in use`? Good news: Ollama is already running (the Ollama app does this by itself on Windows and Mac). Close this window and go on.

**c) Download the model.** Use another terminal (one time only, about 2.5 GB):
```bash
ollama pull qwen3:4b
```

**d) Verify the download.** Expect **qwen3:4b** in the list:
```text
ollama list
```
**e) Test inference.** Expect a non-empty greeting; the wording can vary:
```text
ollama run qwen3:4b "Reply with one short greeting."
```
Ollama commands do not need the Python venv. If installation or inference fails, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or contact Gaurav about the fallback.

### Step 3 · Get the code and install execution libraries

Clone the project with the commands for your platform below, or download and unzip it from GitHub's **Code → Download ZIP** menu. After getting the code, open that project folder in VS Code with **File → Open Folder**, then choose **Terminal → New Terminal** before running the setup command. If you used a ZIP, skip the Git and directory-change commands.

The setup script installs libraries from `requirements.txt`: **FastAPI**, **Uvicorn**, **OpenAI SDK**, **LangGraph**, **DeepEval**, **pytest**, and supporting libraries. It does **not** install Python or VS Code. It creates `.venv` and `.env`, and runs its initial check using the venv's Python. Missing Groq-key failures are expected until step 4. It is safe to run again.

**Windows (PowerShell): get the code**
```powershell
git clone https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2.git
```

```powershell
cd shopkart-ai-tutorial-v2
```

**In VS Code's terminal, inside the project folder:**

```powershell
python setup_env.py
```

```powershell
.venv\Scripts\Activate.ps1
```

**Mac / Linux: get the code**
```bash
git clone https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2.git
```

```bash
cd shopkart-ai-tutorial-v2
```

**In VS Code's terminal, inside the project folder:**

```bash
python3 setup_env.py
```

```bash
source .venv/bin/activate
```

You now see `(.venv)` at the start of the line. That means it worked.
**Every time you open a new terminal for this tutorial**, go to the project folder and run the `activate` line again.

> Windows says "running scripts is disabled"? See FAQ #4 in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
> Prefer to do it by hand? Use the separate manual-setup commands in [COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md#set-up-one-time) or [COMMANDS_MAC.md](COMMANDS_MAC.md#set-up-one-time).

### Step 4 · Create your settings file and get a free Groq key

**a)** The setup script already created `.env`. If it is missing, duplicate `.env.example` as `.env` in VS Code's Explorer.

**b)** Get a free Groq key (no credit card needed): https://console.groq.com/keys

**c)** In your already-open VS Code project, click `.env` in **Explorer**. Put your key in **both** lines that say `gsk_your_key_here`: `LLM_API_KEY` (the bot) and `JUDGE_API_KEY` (the judge). Save the file.

> The model name is in `.env` too: `LLM_MODEL`. Want the bot on your laptop instead? Use **Option B** (Ollama) in `.env` (see FAQ #6).

### Step 5 · Check that everything works

Run this from the project folder with **`(.venv)` active** (activate it again in every new terminal before Python scripts or tests). In VS Code, use **Python: Select Interpreter** and select `.venv` too.

```bash
python check_setup.py
```

- Every line says **OK**? You are ready.
- A line says **FAIL**? It shows a FAQ number. Look up that number in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## On the day: the terminal windows you need

| Window | What runs there | When |
|---|---|---|
| **1 · Ollama** | Ollama app or dedicated server terminal | local-model demo; keep it ready, but Groq stays the default |
| **2 · Bot** | the current step's Uvicorn server | steps 2 to 5, and all of Part 2 |
| **3 · Work** | Python scripts and pytest commands from the current step | always |

Remember: in windows 2 and 3, run the `activate` line first (see Step 3 above).

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
python setup_env.py
```

**Initial setup, from the project folder (Mac/Linux):**

```bash
python3 setup_env.py
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

**Run all of Part 2**, from the project folder with the step 5 bot running:

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
| `plant_bug.py` | switch bugs on and off for Part 2 |
| `checkpoint.py` | copy in the finished code if you fall behind |
| `check_setup.py` | checks if your laptop is ready |
| `setup_env.py` | one-command setup: virtual environment, packages, `.env` |
| `PRE_CONFERENCE.md` | how to get ready before the day (own laptop, or in the browser) |
| `COMMANDS_WINDOWS.md` · `COMMANDS_MAC.md` | every command for steps 1 to 9, copy-paste ready |
| `.devcontainer/` | settings for running the tutorial in GitHub Codespaces (browser) |
| `tools/` | tools for the presenter (`PRESENTER_CHECKLIST.md` inside) |

## Want to build it again later? The 9 ideas

1. **Call a model.** A few lines of code with the OpenAI library. *(step 1)*
2. **Give it a job description.** Tell it its role, its topic, and its rules. *(step 1)*
3. **Give it memory.** Send the whole chat every time. *(step 2)*
4. **Put it behind an API**, so web pages, tools and tests can use it. *(step 2)*
5. **Give it a face.** A web page that calls the API. *(step 3)*
6. **Give it the book.** Find the right rule pages and tell the AI to answer only from them. *(step 4)*
7. **Give it tools.** The AI *asks* for an action, your code *does* it. Put hard rules in code, not in the prompt. *(step 5)*
8. **Split the work and record every step.** Planner → Implementer → Reviewer. The record makes it testable. *(step 5)*
9. **Test from the bottom up, and plant bugs on purpose.** Rule checks first, then an AI judge, then the agent's journey, then test the judge. *(steps 6-9)*

## For the presenter
- Sending this to attendees (what to send, when, and how to test both setup paths): [tools/PRESENTER_CHECKLIST.md](tools/PRESENTER_CHECKLIST.md).
- After changing any code, check that the step folders still match each other and that all code compiles:

  ```bash
  python tools/check_steps.py
  ```

- Practise without a real model. From the project folder:

  ```bash
  cd tools
  ```

  Start the fake model server and leave it running:

  ```bash
  uvicorn fake_llm:app --port 9999
  ```

  In `.env`, set `LLM_BASE_URL=http://localhost:9999/v1` and `LLM_MODEL=fake`. It can play the judge too: set `JUDGE_BASE_URL=http://localhost:9999/v1` and `JUDGE_MODEL=fake` to rehearse steps 7-9 offline.

## Credits & licence
Built for AutomationSTAR 2026 by Gaurav Khurana ([gauravkhurana.com](https://gauravkhurana.com)). ShopKart, its orders and its rules are made up.
Tools used: FastAPI, OpenAI Python SDK, LangGraph, DeepEval, pytest, Ollama. Optional extra: LangSmith.
