# Get ready before the conference

**If you get stuck anywhere, contact [Gaurav Khurana on LinkedIn](https://www.linkedin.com/in/gauravkhuraana/).**

Can't message on LinkedIn? Email: **gaurav [dot] khuraana [at] gmail [dot] com** (replace `[dot]` with `.` and `[at]` with `@`, then remove the spaces).

**Do this at home, any evening in the week before.** It takes about 20 to 30 minutes, most of it waiting for a download.
On the day you then only need a working laptop.

Pick **one** path:

| | Path | Choose it if | Time |
|---|---|---|---|
| **A** | **My own laptop** (recommended) | you can install Python on your laptop | 20-30 min |
| **B** | **In the browser** (GitHub Codespaces) | your laptop is locked down, or the install keeps failing | 10 min |

Whichever you pick, the final setup check in step 6 must show **OK on every line**. Take a screenshot. Local attendees must also complete the Ollama installation and test below.

---

## Table of contents

- [Path A · My own laptop](#path-a--my-own-laptop)
  - [1 · Install Python (one time)](#1--install-python-one-time)
    - [Windows: install with PowerShell](#windows-install-with-powershell)
    - [Mac: install with Terminal](#mac-install-with-terminal)
    - [Installation validation status](#installation-validation-status)
  - [2 · Get the project](#2--get-the-project)
  - [3 · Open the project in VS Code](#3--open-the-project-in-vs-code)
  - [4 · Install the Python libraries needed for execution](#4--install-the-python-libraries-needed-for-execution)
  - [5 · Get your free Groq key and put it in `.env`](#5--get-your-free-groq-key-and-put-it-in-env)
  - [6 · Check it](#6--check-it)
  - [7 · Install and test Ollama (required on local laptops)](#7--install-and-test-ollama-required-on-local-laptops)
- [Path B · In the browser (GitHub Codespaces)](#path-b--in-the-browser-github-codespaces)
- [Checklist](#checklist)
- [If something goes wrong](#if-something-goes-wrong)

## Path A · My own laptop

### 1 · Install Python (one time)
**Install CPython 3.12.13 using the commands below. Do not choose a release from the generic Python downloads page.** The workshop supports stable 3.12.x, but **3.12.13 is our exact clean-install version**, not 3.12.0 or whichever release the download button suggests.

**Why does python.org mention a newer version?** Python 3.12 is in its security-fixes-only stage. Newer feature releases can be stable too, but they are not the workshop target. The [official 3.12.13 release notes](https://www.python.org/downloads/release/python-31213/) explain that newer 3.12 releases are source-only; **3.12.10 was the last official Windows/Mac binary installer**, and does not include the later security fixes. You do not need to build Python from source.

We use [uv](https://docs.astral.sh/uv/guides/install-python/), a third-party tool from Astral, to download a prebuilt CPython 3.12.13 from Astral's `python-build-standalone` project. We pin the installer tool to **uv 0.11.7** too. These are reproducible version choices, not a claim that they will always be the newest releases.

**Keep other Python versions installed.** These commands install tools in your own account, do not require administrator/root access, and do not change PATH, shell profiles, the Windows Python registry, or your default Python. There is **no PATH checkbox to find**. We invoke the workshop tools by their full paths instead.

**Stop if any command fails.** Do not continue using an unversioned `python`, disable certificate verification, or uninstall another Python to work around it. If company policy blocks Astral/GitHub downloads or script execution, contact Gaurav and use [Path B](#path-b--in-the-browser-github-codespaces).

#### Windows: install with PowerShell

Open **Start → PowerShell** (not Command Prompt). Run each block in order. The first two settings apply only to this terminal; they tell the uv installer where to put the tool and not to modify PATH.

```powershell
$env:UV_INSTALL_DIR = "$HOME\.shopkart-tools\bin"
```

```powershell
$env:UV_NO_MODIFY_PATH = "1"
```

The following downloads and executes Astral's pinned uv installer. Only run it if your organization's policy permits it.

```powershell
Invoke-RestMethod https://astral.sh/uv/0.11.7/install.ps1 | Invoke-Expression
```

```powershell
& "$HOME\.shopkart-tools\bin\uv.exe" --version
```

Expect **uv 0.11.7** (additional build details are normal). Install the exact interpreter without executable aliases or Windows launcher registration:

```powershell
& "$HOME\.shopkart-tools\bin\uv.exe" python install 3.12.13 --no-bin --no-registry
```

**Test it now, before downloading the project.** These commands select only uv-managed 3.12.13, not an older Python that an existing `py` launcher might find:

```powershell
& (& "$HOME\.shopkart-tools\bin\uv.exe" python find --managed-python --no-project 3.12.13) --version
```

```powershell
& (& "$HOME\.shopkart-tools\bin\uv.exe" python find --managed-python --no-project 3.12.13) -c "import sys, ssl, venv, ensurepip; assert sys.version_info[:3] == (3, 12, 13); print(sys.executable); print(ssl.OPENSSL_VERSION); print('Python is working')"
```

Expect **Python 3.12.13**, then an absolute executable path inside uv's Python installation directory, an OpenSSL version, and **Python is working**. A plain `python --version` or `py -3.12 --version` may still show your old Python: that is intentional.

#### Mac: install with Terminal

Open **Cmd+Space → Terminal**. These commands work with the usual zsh/bash shells. They use a dedicated tool directory and disable the installer's PATH/profile changes; no Homebrew or `sudo` is required.

```bash
uv_installer="$(mktemp)"
```

Run the following blocks in that same terminal so `uv_installer` still names your temporary file:

```bash
curl --fail --show-error --silent --location https://astral.sh/uv/0.11.7/install.sh -o "$uv_installer"
```

The following executes the downloaded Astral installer. Do not run it if the download failed.

```bash
env UV_INSTALL_DIR="$HOME/.shopkart-tools/bin" UV_NO_MODIFY_PATH=1 sh "$uv_installer"
```

```bash
rm "$uv_installer"
```

```bash
"$HOME/.shopkart-tools/bin/uv" --version
```

Expect **uv 0.11.7**. Install the exact interpreter without executable aliases:

```bash
"$HOME/.shopkart-tools/bin/uv" python install 3.12.13 --no-bin
```

**Test it now, before downloading the project:**

```bash
"$("$HOME/.shopkart-tools/bin/uv" python find --managed-python --no-project 3.12.13)" --version
```

```bash
"$("$HOME/.shopkart-tools/bin/uv" python find --managed-python --no-project 3.12.13)" -c "import sys, ssl, venv, ensurepip; assert sys.version_info[:3] == (3, 12, 13); print(sys.executable); print(ssl.OPENSSL_VERSION); print('Python is working')"
```

Expect **Python 3.12.13**, then an absolute executable path inside uv's Python installation directory, an OpenSSL version, and **Python is working**. Your system's `python3` and any existing `python3.12` stay unchanged.

**New VS Code terminal later?** The full-path selection commands work there too; they do not depend on an earlier shell variable or PATH update. Follow the platform-specific setup command in step 4.

#### Installation validation status

| Platform | Status |
|---|---|
| Windows x64 | **Passed in an isolated workspace:** pinned uv/Python download and install, exact setup command from a path containing spaces, requirements installation, required imports, `pip check`, and repeat setup without changing settings or default Python/PATH/registry |
| Mac Apple Silicon | CPython 3.12.13 build listed by uv; **native installation/setup validation pending** |
| Mac Intel | CPython 3.12.13 build listed by uv; **native installation/setup validation pending** |

For native Mac validation, run the commands above, then step 4 and step 6 in fresh VS Code terminals. Check `.venv`'s version, run `python -m pip check`, and repeat setup to verify it reuses the environment. Until someone performs that run on a Mac, these instructions are not Mac-tested.

**Install VS Code too:** download and install [Visual Studio Code](https://code.visualstudio.com/download). Open it, choose **Extensions**, search for **Python**, and install the extension published by **Microsoft**. Python and VS Code are separate installations; step 4 does not install either of them.

### 2 · Get the project
Either with Git:
```bash
git clone https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2.git
```

Or without Git: open https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2 → green **Code** button → **Download ZIP** → unzip it. (The unzipped folder may be called `shopkart-ai-tutorial-v2-main`: that is fine.)

### 3 · Open the project in VS Code
Use **File → Open Folder** and select the downloaded/cloned project folder. Keep it open for the remaining steps. Choose **Terminal → New Terminal**; it opens in the project folder.

You are in the right place when the following lists `check_setup.py`.

**Windows**
```powershell
Get-Item check_setup.py
```

**Mac**
```bash
ls check_setup.py
```

### 4 · Install the Python libraries needed for execution
This installs the libraries used to run the tutorial: **FastAPI** (API framework), **Uvicorn** (web server), **OpenAI SDK** (model calls), **LangGraph** (agent workflow), **DeepEval** (AI judging), and **pytest** (tests), plus their supporting libraries. It does **not** install Python or VS Code; you installed those in step 1.

**Windows**
```powershell
& (& "$HOME\.shopkart-tools\bin\uv.exe" python find --managed-python --no-project 3.12.13) setup_env.py
```

**Mac**
```bash
"$("$HOME/.shopkart-tools/bin/uv" python find --managed-python --no-project 3.12.13)" setup_env.py
```

These commands select the **already installed, uv-managed Python 3.12.13**; they do not install Python itself. If uv or that Python is missing, stop and complete step 1. Setup creates a private Python 3.12 environment (`.venv`), installs the libraries from `requirements.txt` **inside it**, and creates your settings file `.env`. It also runs the setup check using **the Python inside `.venv`**. Groq/key checks can fail until you complete step 5; check again in step 6. If library installation stops with an error, **run the same setup command again**: it reuses a compatible environment.

**Linux/Codespaces with Python 3.12 already provided:** use `python3.12 setup_env.py` instead. Path B prepares this automatically; it does not need the desktop uv installation.

**Already created `.venv` with another Python version?** Setup stops before installing packages and tells you which version it found. It does not convert or delete the environment. Follow [FAQ #1](TROUBLESHOOTING.md#1--wrong-python-version) to rename it and create a fresh one with 3.12.

### 5 · Get your free Groq key and put it in `.env`
1. Create a free key (no credit card): https://console.groq.com/keys
2. In your already-open VS Code project, click `.env` in the **Explorer** sidebar.
3. Replace `gsk_your_key_here` with your key in **both** places: `LLM_API_KEY` and `JUDGE_API_KEY`. Save.

### 6 · Check it
**Windows**
```powershell
.venv\Scripts\Activate.ps1
```

```powershell
python --version
```

```powershell
python check_setup.py
```

**Mac**
```bash
source .venv/bin/activate
```

```bash
python --version
```

```bash
python check_setup.py
```

The activated environment must report **Python 3.12.x**. From now on, normal `python` commands use that version, even if another version is your system default.

Every line **OK**? You are ready. A line says **FAIL**? It shows a number: look it up in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
(Port 8000 saying FAIL just means something is already running there. If that is your own bot, it is fine.)

> From now on, **every new tutorial terminal** needs the activate command first, from the project folder, before running Python scripts or tests. You see **`(.venv)`** at the start of the line when it worked. In VS Code, use **Python: Select Interpreter** in the Command Palette and choose the interpreter in `.venv`.

### 7 · Install and test Ollama (required on local laptops)
Prepare this **at home**, not on conference Wi-Fi. We will demo a local model if the session allows. Groq remains the default for the tutorial and the AI judge; installing Ollama does not switch your project settings.

1. Install [Ollama](https://ollama.com/download) for your operating system. Launch the Ollama app, then open a **new terminal**. Ollama commands do not need the Python venv.
2. Check the installation:
   ```text
   ollama --version
   ```
   Expect an Ollama version number. If the command is not found, reopen the terminal and check the installation/PATH.
3. Open **http://localhost:11434** in a browser. Expect **Ollama is running**. If the app is not serving requests, start it in a dedicated terminal and leave that terminal open:
   ```text
   ollama serve
   ```
   If it says **address already in use**, verify the browser message above; the app may already be running.
4. In another terminal, download the model (about 2.5 GB):
   ```text
   ollama pull qwen3:4b
   ```
5. Verify that the downloaded model appears in the list:
   ```text
   ollama list
   ```
   Expect a row named **qwen3:4b**.
6. Test a real response:
   ```text
   ollama run qwen3:4b "Reply with one short greeting."
   ```
   Expect a non-empty greeting; wording and response speed vary. A download alone is not the full test.

Leave your project on Groq for the normal setup check. For the local-model demo, follow [FAQ #6](TROUBLESHOOTING.md#6--switching-between-groq-and-ollama) to switch providers. If installation is blocked or your laptop cannot run the model, use the Codespaces/Groq fallback below and contact Gaurav; do not silently skip a failed local setup.

---

## Path B · In the browser (GitHub Codespaces)

Nothing to install. You need a free GitHub account.

1. Open https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2
2. Click the green **Code** button → **Codespaces** tab → **Create codespace on main**.
3. It asks for two secrets, `LLM_API_KEY` and `JUDGE_API_KEY`. Paste your free Groq key (https://console.groq.com/keys) in **both**.
4. Wait a few minutes. VS Code opens in your browser and installs everything by itself.
5. In its terminal (it already shows `(.venv)`):
   ```bash
   python check_setup.py
   ```

   Every line **OK**? You are ready.

Corporate GitHub accounts sometimes cannot use Codespaces. Then use Path A with a personal laptop, or pair with a neighbour on the day.

---

## Checklist

| When | Do this | Done |
|---|---|---|
| After Python installation (Path A) | Version and execution smoke tests in step 1 both pass | ☐ |
| Any evening this week | Path A or B above, until the step 6 setup check is all OK inside `.venv`; keep a screenshot | ☐ |
| Before the event (Path A) | Ollama version, service, model list and greeting test in step 7 all work, or contact Gaurav about the fallback | ☐ |
| 3 days before | Repeat the step 6 activation and setup check; keep the screenshot. This proves your Groq key works | ☐ |
| The day before | Charge the laptop. Pack the charger. Repeat the step 6 activation and setup check | ☐ |
| On the day | Bring a phone with a hotspot, in case the venue Wi-Fi is slow. The tutorial sends only small text requests to Groq, so a hotspot is plenty | ☐ |

## If something goes wrong
1. Look up the FAQ number that `check_setup.py` printed, in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
2. Still stuck? Contact [Gaurav Khurana](https://www.linkedin.com/in/gauravkhuraana/). **Nobody gets left behind**: on the day, pair with a neighbour. Every step also has a checkpoint that gives you the finished code; for example, from the project folder with `.venv` active:
   ```bash
   python checkpoint.py step3
   ```
