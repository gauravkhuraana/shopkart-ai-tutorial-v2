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

## Path A · My own laptop

### 1 · Install Python (one time)
Download **Python 3.12** (3.11 and 3.13 also work): https://www.python.org/downloads/
- **Windows:** on the first installer screen, tick **"Add python.exe to PATH"**. No admin rights? Choose "Install for me only".
- **Mac:** use the installer from the same page.

**Test Python now, before downloading the project.** Open a **new** terminal after installation so it picks up PATH changes: Windows → Start → PowerShell; Mac → Cmd+Space → Terminal.

**Windows**
```powershell
python --version
```

```powershell
python -c "print('Python is working')"
```

**Mac**
```bash
python3 --version
```

```bash
python3 -c "print('Python is working')"
```

Expect Python **3.11, 3.12 or 3.13**, then **Python is working**. These installation/PATH tests use your base Python: there is no virtual environment yet. If Python is not found, opens the Microsoft Store, or shows the wrong version, fix [FAQ #1](TROUBLESHOOTING.md#1--wrong-python-version) before continuing.

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
python setup_env.py
```

**Mac**
```bash
python3 setup_env.py
```

It creates a private Python environment (`.venv`), installs the libraries from `requirements.txt` **inside it**, and creates your settings file `.env`. It also runs the setup check using **the Python inside `.venv`**, even though this first setup command uses base Python. Groq/key checks can fail until you complete step 5; check again in step 6. If library installation stops with an error, **run the same setup command again**: it reuses the environment.

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
python check_setup.py
```

**Mac**
```bash
source .venv/bin/activate
```

```bash
python check_setup.py
```

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
