# Troubleshooting FAQ

**If you get stuck anywhere, contact [Gaurav Khurana on LinkedIn](https://www.linkedin.com/in/gauravkhuraana/).**

Can't message on LinkedIn? Email: **gaurav [dot] khuraana [at] gmail [dot] com** (replace `[dot]` with `.` and `[at]` with `@`, then remove the spaces).

From the project folder with `.venv` active, the setup check prints a FAQ number for every red line:
```bash
python check_setup.py
```

Find that number below. Stuck for more than 3 minutes? Pair with a neighbour, or switch to the hosted option (#6). Every step also has a checkpoint; for example, from the project folder:

```bash
python checkpoint.py step3
```

Or simply open the next `build/stepN` folder: it already contains the finished code of the step before.

---

## Table of contents

- [#1 · Wrong Python version](#1--wrong-python-version)
- [#2 · Library installation fails](#2--library-installation-fails)
- [#3 · Model server not reachable](#3--model-server-not-reachable)
- [#3b · `ModuleNotFoundError: No module named 'config'`](#3b--modulenotfounderror-no-module-named-config)
- [#4 · Windows won't activate the virtual environment](#4--windows-wont-activate-the-virtual-environment)
- [#5 · No admin rights on a company laptop](#5--no-admin-rights-on-a-company-laptop)
- [#6 · Switching between Groq and Ollama](#6--switching-between-groq-and-ollama)
- [#7 · `.env` missing or Groq key missing](#7--env-missing-or-groq-key-missing)
- [#8 · Port 8000 already in use](#8--port-8000-already-in-use)
- [#9 · Model not found](#9--model-not-found)
- [#10 · The bot ignores the policy documents](#10--the-bot-ignores-the-policy-documents)
- [#11 · The model doesn't call tools](#11--the-model-doesnt-call-tools)
- [#12 · The agent loops, or takes very long](#12--the-agent-loops-or-takes-very-long)
- [#13 · Judge error: "invalid JSON" / "could not parse"](#13--judge-error-invalid-json--could-not-parse)
- [#14 · Error 429 / "rate limit"](#14--error-429--rate-limit)
- [#15 · The tests are very slow](#15--the-tests-are-very-slow)
- [#16 · Agent mode / `/agent` shows an error, or the step log is empty](#16--agent-mode--agent-shows-an-error-or-the-step-log-is-empty)
- [#17 · SSL / certificate errors on a company network](#17--ssl--certificate-errors-on-a-company-network)
- [#18 · Using the hosted ShopKart bot instead of your own](#18--using-the-hosted-shopkart-bot-instead-of-your-own)
- [#19 · Tests are red for no reason / the bot says strange things](#19--tests-are-red-for-no-reason--the-bot-says-strange-things)

### #1 · Wrong Python version
Use a stable **Python 3.12.x**, the required workshop series. The recommended clean installation is **CPython 3.12.13 with uv 0.11.7**. Both setup scripts flag a different series or prerelease.

**Keep other Python versions installed.** Follow the [exact Windows/Mac installation commands](PRE_CONFERENCE.md#1--install-python-one-time). Do not select a source archive from the generic Python downloads page: 3.12.10 was the last official binary installer, while newer 3.12 security releases are source-only. The guide uses Astral's prebuilt Python instead and does not require a PATH checkbox.

Check the managed installation on **Windows**:

```powershell
& (& "$HOME\.shopkart-tools\bin\uv.exe" python find --managed-python --no-project 3.12.13) --version
```

**Mac**
```bash
"$("$HOME/.shopkart-tools/bin/uv" python find --managed-python --no-project 3.12.13)" --version
```

On Linux/Codespaces with Python 3.12 already provided, use `python3.12 --version` instead. On Windows/Mac expect **Python 3.12.13**, then run the execution/SSL smoke test in the installation guide. `python` or `py -3.12` outside `.venv` may still select an older installation; that is not evidence that the managed installation failed.

**uv executable missing?** Complete the platform-specific uv installation in the guide. **"No interpreter found"?** Run its exact `python install 3.12.13` command. Full paths work in new terminals without a PATH update. Do not replace the failing command with plain `python`. If company policy blocks downloads or scripts, use [the browser fallback](PRE_CONFERENCE.md#path-b--in-the-browser-github-codespaces); do not disable certificate verification or corporate controls.

**Already have `.venv` from another Python?** Activating it or installing another Python does not change its interpreter. Setup prints the environment's version and stops before package installation when it is incompatible.

1. Stop tutorial servers with **Ctrl+C**. If the current terminal has an active environment, run `deactivate`, then open a new terminal in the project folder.
2. Rename the existing environment with the command for your platform below. Run the rename **only if `.venv` exists** and the backup name **does not exist**; otherwise choose an unused backup name. This preserves a backup, but a moved environment is not intended to run from its backup location.
3. Run setup with 3.12. It creates a fresh `.venv`; it does not delete your `.env` settings or source files.

**Windows**

```powershell
Rename-Item -LiteralPath .venv -NewName .venv-before-python312
```

```powershell
& (& "$HOME\.shopkart-tools\bin\uv.exe" python find --managed-python --no-project 3.12.13) setup_env.py
```

**Mac**

```bash
mv .venv .venv-before-python312
```

```bash
"$("$HOME/.shopkart-tools/bin/uv" python find --managed-python --no-project 3.12.13)" setup_env.py
```

On Linux/Codespaces with Python 3.12 already provided, use `python3.12 setup_env.py` instead.

Activate the new `.venv` using your platform's command in the setup guide. Then `python --version` must show **3.12.x** and normal `python` commands use it, even if your system default is another version. Run `python check_setup.py` inside that environment.

VS Code is installed separately from [its official download page](https://code.visualstudio.com/download). Install Microsoft's **Python** extension, open the project folder, and select the `.venv` interpreter with **Python: Select Interpreter**. Installing the extension alone does not install Python.

### #2 · Library installation fails
- Easiest fix on **Windows**:

  ```powershell
  & (& "$HOME\.shopkart-tools\bin\uv.exe" python find --managed-python --no-project 3.12.13) setup_env.py
  ```

- On **Mac**:

  ```bash
  "$("$HOME/.shopkart-tools/bin/uv" python find --managed-python --no-project 3.12.13)" setup_env.py
  ```

On Linux/Codespaces with Python 3.12 already provided, use `python3.12 setup_env.py`. The setup script creates the virtual environment and installs the libraries. You can run it again after a failure. If the managed interpreter is missing, complete [preconference step 1](PRE_CONFERENCE.md#1--install-python-one-time) first.

- Use a virtual environment (see README, step 3) so you don't need admin rights. The setup script installs execution libraries into `.venv`; it does not install Python or VS Code.
- Behind a company proxy:

  ```bash
  pip install --proxy http://your-proxy:port -r requirements.txt
  ```

- SSL errors on a company network: see #17.
- "Microsoft Visual C++ required" on Windows: activate `.venv`, upgrade pip, then retry the installation. Recent packages ship pre-built:

  ```bash
  python -m pip install --upgrade pip
  ```

### #3 · Model server not reachable
Using **Groq** (the default)? Check your internet connection, and that `LLM_API_KEY` in `.env` holds your Groq key (see #7). Company network? See #17.

Using **Ollama** (`localhost:11434`)? Then Ollama isn't running.
- Windows/Mac: start the **Ollama** app (look for the llama icon in the tray/menu bar).
- Linux / any: open a **new terminal window** and start the server:

  ```bash
  ollama serve
  ```

  **Leave that window open** (closing it stops Ollama). If it says `address already in use`, verify the browser message below; the app may already be running.
- Test: open http://localhost:11434 in a browser. It should say "Ollama is running".
- Using LM Studio instead? Start its **local server** (Developer tab) and use Option C in `.env`.

### #3b · `ModuleNotFoundError: No module named 'config'`
Every step finds `shared/config.py` by itself, as long as the repo layout is intact. Do not move a step folder out of `build/`. Run commands from inside the step folder; for example, from the project folder:

```bash
cd build/step2_api
```

### #4 · Windows won't activate the virtual environment
PowerShell says "running scripts is disabled on this system":
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

```powershell
.venv\Scripts\Activate.ps1
```

Or use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### #5 · No admin rights on a company laptop
- Python: the [pinned uv/Python installation](PRE_CONFERENCE.md#1--install-python-one-time) uses your own account without administrator/root access or PATH changes. Corporate policy can still block it; do not try to bypass those restrictions.
- Ollama is required preparation for local attendees, but may need admin. If installation is blocked, contact Gaurav and use the documented Codespaces/Groq fallback in [PRE_CONFERENCE.md](PRE_CONFERENCE.md); Groq remains the default provider.
- Company firewall blocks sign-ups or downloads: pair with a neighbour for Part 1, then point your tests at the hosted bot for Part 2 (#18).

### #6 · Switching between Groq and Ollama
- **Groq** (the default, Option A in `.env`) runs in the cloud. Nothing to install, needs internet and a free key.
- **Ollama** (Option B in `.env`) runs on your laptop. Install it and download the model:

  ```bash
  ollama pull qwen3:4b
  ```

  Then switch the `LLM_*` lines in `.env` to Option B. Laptop too slow? Download a smaller model and set `LLM_MODEL=qwen3:1.7b`:

  ```bash
  ollama pull qwen3:1.7b
  ```

- Steps 1-3 (`ask_simple.py`, `ask.py`, `app_simple.py`, `app.py`) , step 4's `app_simple.py` and step 5's `agent_simple.py` choose the server in the file itself: put a `#` in front of the Groq lines and remove the `#` from the Ollama lines. They read only the key and the model name from `.env`. (Step 4's full `app.py` and step 5's `agent.py` read all `LLM_*` lines from `.env`.)

### #7 · `.env` missing or Groq key missing
1. Copy the template on **Windows**:

   ```powershell
   copy .env.example .env
   ```

   Or on **Mac/Linux**:

   ```bash
   cp .env.example .env
   ```

2. Create a free key at https://console.groq.com/keys (no credit card needed)
3. Paste it into `.env` twice: `LLM_API_KEY=gsk_...` (the bot) and `JUDGE_API_KEY=gsk_...` (the judge)
Never commit `.env`: it's in `.gitignore`.

### #8 · Port 8000 already in use
Something else is running on 8000 (maybe an earlier copy of your bot: close that terminal).
Or use another port and set `SHOPKART_URL=http://localhost:8001` in `.env`:

```bash
uvicorn app:app --reload --port 8001
```

### #9 · Model not found
- **Groq:** `LLM_MODEL` in `.env` must be a model Groq offers, e.g. `openai/gpt-oss-20b` (list: https://console.groq.com/docs/models).
- **Ollama:** download the model at home (about 2.5 GB), not on conference Wi-Fi:

  ```bash
  ollama pull qwen3:4b
  ```

  The name in `.env` (`LLM_MODEL`) must exactly match the model name shown by:

  ```bash
  ollama list
  ```

  In steps 1-3 the Ollama model name is written in the file itself (`qwen3:4b`).

### #10 · The bot ignores the policy documents
(Step 4, `build/step4_ground/app_simple.py` or `app.py`)
- Check TODO 1: is `retrieve(...)` actually called and `pages` filled? The terminal prints `librarian brought: [...]`.
- Check TODO 3: the chat page shows "from: returns.md …" under the answer only if the API returns `sources`.
- Check TODO 2: does the system prompt say "answer ONLY from the policy pages"?
- Small models sometimes still drift. That's a real finding, and exactly what the step 6 and 7 tests catch.

### #11 · The model doesn't call tools
Not every model supports tool calling. Use one that does: `qwen3:4b` (default), `qwen3:8b`, `llama3.1:8b`, or the hosted option (#6).

### #12 · The agent loops, or takes very long
- Simple version: `agent_simple.py` stops after `MAX_STEPS` model calls (TODO 3 hands over to a human). Full version: step 5, TODO 2 (`route_after_review`) must stop after `MAX_ROUNDS`, otherwise the Reviewer can send work back forever.
- Each run makes 3–8 model calls, so on a slow laptop one order can take a minute. Run one order instead of `all`. For the simple agent:

  ```bash
  python agent_simple.py 1043
  ```

  Or, for the full crew:

  ```bash
  python agent.py 1043
  ```

### #13 · Judge error: "invalid JSON" / "could not parse"
The judge model returned something that isn't valid JSON. Small local models do this often, which is why the default judge is a bigger hosted model. Check `JUDGE_MODEL` in `.env` points at Groq/Cerebras, not your local model.

### #14 · Error 429 / "rate limit"
Free tiers limit requests or tokens per minute. The project lets DeepEval retry transient failures up to 6 times by default.
- Wait a minute and re-run only what failed:

  ```bash
  pytest --lf
  ```

- Run fewer judge tests. For rule checks, start in the project folder; these need no judge:

  ```bash
  cd evaluate/step6_rules
  ```

  ```bash
  pytest test_rules.py
  ```

  For a single judge question, first return to the project folder and enter the judge step:

  ```bash
  cd ../..
  ```

  ```bash
  cd evaluate/step7_judge
  ```

  ```bash
  pytest test_judge.py -k price
  ```

- If your provider needs longer backoff, set `DEEPEVAL_RETRY_MAX_ATTEMPTS` and `DEEPEVAL_RETRY_CAP_SECONDS` in `.env`
- Step 9:

  ```bash
  python judge_the_judge.py --runs 2
  ```

- Switch to the backup judge (Cerebras) in `.env`

### #15 · The tests are very slow
The AI-judge tests make several judge calls per question. That's the "taxi meter" from the slides.
- Only questions marked `judge: true` in `golden_questions.yaml` use the judge. Set more of them to `false` while practising.
- Run the cheap checks first:

  ```bash
  pytest -k "not ai_judge"
  ```

### #16 · Agent mode / `/agent` shows an error, or the step log is empty
- Are you running uvicorn in `build/step5_agent`? Agent mode only exists from step 5 ("Agent mode arrives in step 5").
- Is `agent_simple.py` (or `agent.py`) saved and free of syntax errors? Run this inside the step 5 folder for clearer errors:

  ```bash
  python agent_simple.py 1043
  ```

- Still stuck:

  ```bash
  python checkpoint.py step5
  ```

### #17 · SSL / certificate errors on a company network
Your company inspects HTTPS traffic. Options:
- Try your phone's hotspot or the conference Wi-Fi.
- Ask IT for the company root certificate and set `SSL_CERT_FILE=path\to\cert.pem`.
- Don't disable certificate checks.

### #18 · Using the hosted ShopKart bot instead of your own
If your laptop can't run the bot, the tests in Part 2 can test the hosted one (normally they test `build/step5_agent` on localhost:8000):
set `SHOPKART_URL=<URL from the slide>` in `.env`. The tests call the bot over HTTP, so they don't care where it runs.

### #19 · Tests are red for no reason / the bot says strange things
A planted bug from the missions may still be active. From the project folder, show the active bug:

```bash
python plant_bug.py
```

Then restore the healthy bot:

```bash
python plant_bug.py off
```
