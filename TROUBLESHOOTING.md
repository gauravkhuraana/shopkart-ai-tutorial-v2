# Troubleshooting FAQ

`python check_setup.py` prints a FAQ number for every red line. Find it below.
Stuck for more than 3 minutes? Pair with a neighbour, or switch to the hosted option (#6). Every step also has a checkpoint: `python checkpoint.py step3` etc. Or simply open the next `build/stepN` folder: it already contains the finished code of the step before.

---

### #1 · Wrong Python version
Use **Python 3.11, 3.12 or 3.13**. Newer versions (3.14+) sometimes lack ready-made packages.
- Check: `python --version` (Windows) or `python3 --version` (Mac/Linux)
- Install: https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH")

### #2 · `pip install -r requirements.txt` fails
- Use a virtual environment (see README, step 2) so you don't need admin rights.
- Behind a company proxy: `pip install --proxy http://your-proxy:port -r requirements.txt`
- SSL errors on a company network: see #17.
- "Microsoft Visual C++ required" on Windows: upgrade pip first, `python -m pip install --upgrade pip`, then retry. Recent packages ship pre-built.

### #3 · Model server not reachable
Using **Groq** (the default)? Check your internet connection, and that `LLM_API_KEY` in `.env` holds your Groq key (see #7). Company network? See #17.

Using **Ollama** (`localhost:11434`)? Then Ollama isn't running.
- Windows/Mac: start the **Ollama** app (look for the llama icon in the tray/menu bar).
- Linux / any: open a **new terminal window**, run `ollama serve`, and **leave that window open** (closing it stops Ollama). If it says `address already in use`, Ollama is already running.
- Test: open http://localhost:11434 in a browser. It should say "Ollama is running".
- Using LM Studio instead? Start its **local server** (Developer tab) and use Option C in `.env`.

### #3b · `ModuleNotFoundError: No module named 'config'`
Every step finds `shared/config.py` by itself, as long as the repo layout is intact. Run the commands from inside the step folder (`cd build/step2_api`), and don't move a step folder out of `build/`.

### #4 · Windows won't activate the virtual environment
PowerShell says "running scripts is disabled on this system":
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.venv\Scripts\Activate.ps1
```
Or use Command Prompt instead: `.venv\Scripts\activate.bat`

### #5 · No admin rights on a company laptop
- Python: the python.org installer works without admin ("Install for me only").
- Ollama may need admin. If it's blocked, skip it: the default (Groq) needs nothing installed.
- Company firewall blocks sign-ups or downloads: pair with a neighbour for Part 1, then point your tests at the hosted bot for Part 2 (#18).

### #6 · Switching between Groq and Ollama
- **Groq** (the default, Option A in `.env`) runs in the cloud. Nothing to install, needs internet and a free key.
- **Ollama** (Option B in `.env`) runs on your laptop. Install it, `ollama pull qwen3:4b`, then switch the `LLM_*` lines in `.env` to Option B. Laptop too slow? Try a smaller model: `ollama pull qwen3:1.7b` and `LLM_MODEL=qwen3:1.7b`.
- Steps 1-3 (`ask_simple.py`, `ask.py`, `app_simple.py`, `app.py`) , step 4's `app_simple.py` and step 5's `agent_simple.py` choose the server in the file itself: put a `#` in front of the Groq lines and remove the `#` from the Ollama lines. They read only the key and the model name from `.env`. (Step 4's full `app.py` and step 5's `agent.py` read all `LLM_*` lines from `.env`.)

### #7 · `.env` missing or Groq key missing
1. Copy the template: `copy .env.example .env` (Windows) · `cp .env.example .env` (Mac/Linux)
2. Create a free key at https://console.groq.com/keys (no credit card needed)
3. Paste it into `.env` twice: `LLM_API_KEY=gsk_...` (the bot) and `JUDGE_API_KEY=gsk_...` (the judge)
Never commit `.env`: it's in `.gitignore`.

### #8 · Port 8000 already in use
Something else is running on 8000 (maybe an earlier copy of your bot: close that terminal).
Or use another port: `uvicorn app:app --reload --port 8001`, and set `SHOPKART_URL=http://localhost:8001` in `.env`.

### #9 · Model not found
- **Groq:** `LLM_MODEL` in `.env` must be a model Groq offers, e.g. `openai/gpt-oss-20b` (list: https://console.groq.com/docs/models).
- **Ollama:** download it: `ollama pull qwen3:4b` (about 2.5 GB, so do it at home, not on conference Wi-Fi). The name in `.env` (`LLM_MODEL`) must match `ollama list` exactly. In steps 1-3 the Ollama model name is written in the file itself (`qwen3:4b`).

### #10 · The bot ignores the policy documents
(Step 4, `build/step4_ground/app_simple.py` or `app.py`)
- Check TODO 1: is `retrieve(...)` actually called and `pages` filled? The terminal prints `librarian brought: [...]`.
- Check TODO 3: the chat page shows "from: returns.md …" under the answer only if the API returns `sources`.
- Check TODO 2: does the system prompt say "answer ONLY from the policy pages"?
- Small models sometimes still drift. That's a real finding, and exactly what the LAB 6 tests catch.

### #11 · The model doesn't call tools
Not every model supports tool calling. Use one that does: `qwen3:4b` (default), `qwen3:8b`, `llama3.1:8b`, or the hosted option (#6).

### #12 · The agent loops, or takes very long
- Simple version: `agent_simple.py` stops after `MAX_STEPS` model calls (TODO 3 hands over to a human). Full version: step 5, TODO 2 (`route_after_review`) must stop after `MAX_ROUNDS`, otherwise the Reviewer can send work back forever.
- Each run makes 3–8 model calls, so on a slow laptop one order can take a minute. Run one order (`python agent_simple.py 1043` or `python agent.py 1043`) instead of `all`.

### #13 · Judge error: "invalid JSON" / "could not parse"
The judge model returned something that isn't valid JSON. Small local models do this often, which is why the default judge is a bigger hosted model. Check `JUDGE_MODEL` in `.env` points at Groq/Cerebras, not your local model.

### #14 · Error 429 / "rate limit"
Free tiers limit requests per minute.
- Wait a minute and re-run only what failed: `pytest --lf`
- Run fewer judge tests: `pytest tests/test_chatbot.py -k metal` (no AI judge)
- LAB 8: `python tests/judge_the_judge.py --runs 2`
- Switch to the backup judge (Cerebras) in `.env`

### #15 · The tests are very slow
The AI-judge tests make several judge calls per question. That's the "taxi meter" from the slides.
- Only questions marked `judge: true` in `golden_questions.yaml` use the judge. Set more of them to `false` while practising.
- Run the cheap checks first: `pytest -k "not ai_judge"`

### #16 · Agent mode / `/agent` shows an error, or the step log is empty
- Are you running uvicorn in `build/step5_agent`? Agent mode only exists from step 5 ("Agent mode arrives in step 5").
- Is `agent_simple.py` (or `agent.py`) saved and free of syntax errors? Try `python agent_simple.py 1043` in that folder: errors are clearer there.
- Still stuck: `python checkpoint.py step5`

### #17 · SSL / certificate errors on a company network
Your company inspects HTTPS traffic. Options:
- Try your phone's hotspot or the conference Wi-Fi.
- Ask IT for the company root certificate and set `SSL_CERT_FILE=path\to\cert.pem`.
- Don't disable certificate checks.

### #18 · Using the hosted ShopKart bot instead of your own
If your laptop can't run the bot, the tests in Part 2 can test the hosted one (normally they test `build/step5_agent` on localhost:8000):
set `SHOPKART_URL=<URL from the slide>` in `.env`. The tests call the bot over HTTP, so they don't care where it runs.

### #19 · Tests are red for no reason / the bot says strange things
A planted bug from the missions may still be active. Check and remove it:
```bash
python plant_bug.py        # shows the active bug
python plant_bug.py off
```
