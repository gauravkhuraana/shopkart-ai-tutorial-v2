# Get ready before the conference

**If you get stuck anywhere, contact [Gaurav Khurana on LinkedIn](https://www.linkedin.com/in/gauravkhuraana/).**

Can't message on LinkedIn? Email: **gaurav [dot] khuraana [at] gmail [dot] com** (replace `[dot]` with `.` and `[at]` with `@`, then remove the spaces).

**Do this at home, any evening in the week before.** It takes about 20 to 30 minutes, most of it waiting for a download.
On the day you then only need a working laptop.

> **Tip:** links in this guide open on the same page. **Ctrl+click** a link (Mac: **Cmd+click**) to open it in a new tab, so you do not lose your place here.

Pick **one** path. Not sure? Start with Path A. If it does not work, switch to Path B.

| | Path | Choose it if | Time |
|---|---|---|---|
| **A** | **Install on my laptop** (recommended) | it is your own laptop, or your work laptop lets you install programs | 20-30 min |
| **B** | **Use it in the browser** (GitHub Codespaces; needs a free GitHub account, signed in) | you are **not allowed to install programs** (for example a work or school laptop that asks for an administrator password or says "blocked by your administrator"), or Path A keeps failing | 10 min |

**Path A:** do steps 1 to 7. **Path B:** do only the [Path B section](#path-b--in-the-browser-github-codespaces).

Whichever path you pick, finish by running the setup check. Every line must say **OK**. Take a screenshot.

---

## Table of contents

- [Path A · My own laptop](#path-a--my-own-laptop)
  - [1 · Install Python (one time)](#1--install-python-one-time)
    - [Windows: one command](#windows-one-command)
    - [Mac: two commands](#mac-two-commands)
    - [Test it now, before downloading the project](#test-it-now-before-downloading-the-project)
    - [Installation validation status](#installation-validation-status)
  - [2 · Get the project](#2--get-the-project)
  - [3 · Open the project in VS Code](#3--open-the-project-in-vs-code)
  - [4 · Install the Python libraries needed for execution](#4--install-the-python-libraries-needed-for-execution)
  - [5 · Get your free Groq key and put it in `.env`](#5--get-your-free-groq-key-and-put-it-in-env)
  - [6 · Check it](#6--check-it)
  - [7 · Install and test Ollama (Path A only)](#7--install-and-test-ollama-path-a-only)
- [Path B · In the browser (GitHub Codespaces)](#path-b--in-the-browser-github-codespaces)
- [Prefer pressing ▶? The notebook](#prefer-pressing--the-notebook)
- [Checklist](#checklist)
- [If something goes wrong](#if-something-goes-wrong)

## Path A · My own laptop

### 1 · Install Python (one time)
**Use Python 3.12.10 for this workshop.** Do not pick a version from the python.org download page: it now advertises 3.14, and the workshop is built and tested on 3.12. Python 3.12.10 is the last 3.12 release that has a normal installer, and it is a stable 3.12.x, which is exactly what the setup check accepts. Newer 3.12 releases are source-only.

**Keep other Python versions installed.** You do not need to uninstall anything. Python 3.14 or 3.13 can live side by side with 3.12.

#### Windows: one command

Open **Start → PowerShell** and run:

```powershell
winget install --id Python.Python.3.12 --version 3.12.10 --exact --source winget
```

Accept any prompt (type `Y` to agree to the source terms, and click **Yes** if Windows asks for permission). winget downloads the official installer from python.org and runs it for you. There is nothing to tick or choose.

- It says **"Found an existing package already installed"** and **"No available upgrade found"**? Good: Python 3.12.10 is already there. Carry on.
- It says **"winget is not recognized"**? Use the [official 3.12.10 installer](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe) instead: double-click it and click **Install Now**.

#### Mac: two commands

Open **Cmd+Space → Terminal**. Download the official 3.12.10 installer, then open it:

```bash
curl --fail --location --output ~/Downloads/python-3.12.10-macos11.pkg https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg
```

```bash
open ~/Downloads/python-3.12.10-macos11.pkg
```

In the installer window click **Continue** a few times, then **Install**, and enter your Mac password if asked. It works on both Apple Silicon and Intel Macs.

Already use Homebrew? This one command does the same job: `brew install python@3.12`.

#### Test it now, before downloading the project

**Open a new terminal first** (close the old one) so it can find the new installation.

**Windows**
```powershell
py -3.12 --version
```

```powershell
py -3.12 -c "print('Python is working')"
```

**Mac**
```bash
python3.12 --version
```

```bash
python3.12 -c "print('Python is working')"
```

Expect **Python 3.12.x** (for example 3.12.10), then **Python is working**. If the version command is not found, close the terminal, open a new one, and try again. Still stuck? See [FAQ #1](TROUBLESHOOTING.md#1--wrong-python-version) or use [Path B](#path-b--in-the-browser-github-codespaces).

**Why not just the newest Python?** The workshop's libraries are tested on 3.12, so every attendee uses the same version. 3.12.10 does not include the later source-only security fixes. That is acceptable for a short workshop on a personal laptop; see the [Python 3.12.13 release notes](https://www.python.org/downloads/release/python-31213/) for the lifecycle details.

#### Installation validation status

| Platform | Status |
|---|---|
| Windows x64 | The winget package is official 3.12.10. This machine already had 3.12.10, so the "already installed" message was checked, not a fresh install. **Setup, requirements, `pip check` and rerun passed** on 3.12.10 |
| Mac | Commands prepared; **native Mac installation not yet tested** |

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
py -3.12 setup_env.py
```

**Mac**
```bash
python3.12 setup_env.py
```

These commands use the **already installed** Python 3.12; they do not install Python itself. If you get "not found", finish step 1 first and open a new terminal. Setup creates a private Python 3.12 environment (`.venv`), installs the libraries from `requirements.txt` **inside it**, and creates your settings file `.env`. It also runs the setup check using **the Python inside `.venv`**. Groq/key checks can fail until you complete step 5; check again in step 6. If library installation stops with an error, **run the same setup command again**: it reuses a compatible environment.

**Linux/Codespaces:** `python3.12 setup_env.py` works there too. Path B prepares it automatically.

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

> From now on, **every new tutorial terminal** needs the activate command first, from the project folder, before running Python scripts or tests. You see **`(.venv)`** at the start of the line when it worked. **Optional:** if VS Code asks which interpreter to use, choose the one in `.venv`. You can ignore the prompt: the terminal commands work without it. It only makes the editor's Run button and import underlines behave.

### 7 · Install and test Ollama (Path A only)
Ollama is a small AI that runs on your own laptop. We may demo it if time allows. **Path B users skip this step.** Do it **at home**, not on conference Wi-Fi. Groq stays the default for the tutorial and the AI judge; installing Ollama does not change your project settings.

1. Install [Ollama](https://ollama.com/download) for your operating system. Launch the Ollama app, then open a **new terminal**. Ollama commands do not need the Python venv.
2. Check the installation:
   ```text
   ollama --version
   ```
   Expect an Ollama version number. If the command is not found, reopen the terminal and check the installation/PATH.
3. Open **http://localhost:11434** in a browser (Ctrl+click or Cmd+click the link for a new tab).
   - **It says "Ollama is running"?** This step is done. **Do not run `ollama serve`.** The Ollama app already started the server for you. Go to step 4.
   - **The page does not load?** Open the Ollama app from the Start menu (Windows) or Applications (Mac) and refresh the page. Still nothing? Start the server yourself in a dedicated terminal and leave that terminal open:
     ```text
     ollama serve
     ```
   - **Did you run `ollama serve` and get an error** such as *"Only one usage of each socket address (protocol/network address/port) is normally permitted"* (Windows) or *"address already in use"* (Mac/Linux)? That is **good news**, not a problem. It only means Ollama is already running. Check that the browser page says **Ollama is running**, then go on.
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

Leave your project on Groq for the normal setup check. For the local-model demo, follow [FAQ #6](TROUBLESHOOTING.md#6--switching-between-groq-and-ollama) to switch providers. If Ollama cannot be installed or your laptop cannot run it, tell Gaurav and use Path B below instead. Please do not skip a failed step silently.

---

## Path B · In the browser (GitHub Codespaces)

Nothing to install. You need a free GitHub account. **You must be signed in to GitHub, or you will not see the Codespaces option.**

1. Sign in at https://github.com/login (no account yet? Create a free one at https://github.com/signup first). Ctrl+click, or Cmd+click on Mac, opens a link in a new tab.
2. Open https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2 in a new tab. Check that your profile picture is in the top-right corner: that means you are signed in. If you see **Sign in** there instead, sign in first.
3. Click the green **Code** button → **Codespaces** tab → **Create codespace on main**. No **Codespaces** tab? You are probably not signed in, so go back to step 1.
4. It asks for two secrets, `LLM_API_KEY` and `JUDGE_API_KEY`. Paste your free Groq key (https://console.groq.com/keys) in **both**. (No secrets screen? Continue anyway, and after step 5 paste the key into `.env` in **both** places that say `gsk_your_key_here`, as in Path A step 5.)
5. **Wait a few minutes.** Do not close the page: VS Code opens in your browser and installs everything by itself, and this takes time.
6. In its terminal, check that the line starts with `(.venv)`. If it does not, activate it first:
   ```bash
   source .venv/bin/activate
   ```

   Then run the setup check:
   ```bash
   python check_setup.py
   ```

   Every line **OK**? You are ready.

   **Key typed wrong?** Secrets win over `.env`, so fixing `.env` does not help. Change the secret at https://github.com/settings/codespaces (**Codespaces secrets**), then stop and restart the Codespace.

Using a work GitHub account and Codespaces does not open? Some companies block it. Try a free personal GitHub account, or use Path A on a personal laptop, or pair with a neighbour on the day.

---

## Prefer pressing ▶? The notebook

Not comfortable typing terminal commands? On the day you can follow every step in **`workshop.ipynb`** instead: the same steps, the same files, you press ▶ on a cell instead of typing. You still need the setup above (Path A **or** Path B). The notebook only replaces typing on the day.

Try it now, so you know it works:

1. Open **`workshop.ipynb`** from the VS Code Explorer (Codespaces opens it for you).
   **Path A only:** if VS Code offers to install the **Jupyter** extension, click **Install**.
2. Click the first grey code cell (under **0 · Ready?**) and press **▶** (or Shift+Enter).
3. If VS Code asks for a kernel: **Python Environments** → **.venv**.
   It says `ipykernel` is missing? Your `.venv` is older than this notebook: run the step 4 install command again (`python -m pip install -r requirements.txt` with `.venv` active).
4. Every line should say **OK** or ✅, the same as `python check_setup.py`.

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
