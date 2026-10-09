# Poison Kills Poison: AI Tests AI

Hands-on tutorial · AutomationSTAR 2026 · Gaurav Khurana · #SharingIsCaring

**What you will do today**
1. **Build** a small AI helper for a pretend online shop called **ShopKart**. It answers refund questions. You build it in 5 small steps.
2. **Test** it. First with simple rule checks, then with a second AI that acts as the "judge".

Everything is free and runs on your own laptop.

---

## Before the tutorial: set up your laptop (about 20 minutes)

Please do this **at home**, before the day. The download is big (about 2.5 GB).

### Step 1 · Install three programs

| Program | Where to get it | Note |
|---|---|---|
| **Python** 3.11, 3.12 or 3.13 | https://www.python.org/downloads/ | Windows: tick **"Add python.exe to PATH"** during install |
| **Ollama** (optional: runs the AI model on your laptop, offline) | https://ollama.com/download | Not needed if you use Groq (the default) |
| **Git** | https://git-scm.com/downloads | Or skip Git and download this project as a ZIP |

Check Python: open a terminal and type `python --version` (Mac/Linux: `python3 --version`).

> **What is a terminal?** A window where you type commands.
> Windows: press Start, type **PowerShell**, press Enter. Mac: press Cmd+Space, type **Terminal**, press Enter.

### Step 2 · (Optional) Start Ollama and download the model

By default the bot runs on **Groq's free cloud**, so you can skip this step. Do it only if you want the model on your own laptop (it then works without internet).

**a) Open a NEW terminal window just for Ollama** and type:
```bash
ollama serve
```
**Leave this window open** all the time you use the tutorial. Ollama works in this window. If you close it, Ollama stops.

> It says `address already in use`? Good news: Ollama is already running (the Ollama app does this by itself on Windows and Mac). Close this window and go on.

**b) Check that Ollama is running.** Open this page in your web browser: **http://localhost:11434**
It should say: **"Ollama is running"**.

**c) Download the model.** Open **another** terminal window and type (one time only, about 2.5 GB):
```bash
ollama pull qwen3:4b
```

### Step 3 · Get the code and install the packages

In a terminal, type these lines one by one:

**Windows (PowerShell)**
```powershell
git clone <repo-url>
cd shopkart-ai-tutorial
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux**
```bash
git clone <repo-url>
cd shopkart-ai-tutorial
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You now see `(.venv)` at the start of the line. That means it worked.
**Every time you open a new terminal for this tutorial**, go to the project folder and run the `activate` line again.

> Windows says "running scripts is disabled"? See FAQ #4 in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Step 4 · Create your settings file and get a free Groq key

**a)** Copy the example settings file:
```bash
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
```

**b)** Get a free Groq key (no credit card needed): https://console.groq.com/keys

**c)** Open the file `.env` in any text editor. Put your key in **both** lines that say `gsk_your_key_here`: `LLM_API_KEY` (the bot) and `JUDGE_API_KEY` (the judge). Save the file.

> The model name is in `.env` too: `LLM_MODEL`. Want the bot on your laptop instead? Use **Option B** (Ollama) in `.env` (see FAQ #6).

### Step 5 · Check that everything works

```bash
python check_setup.py
```
- Every line says **OK**? You are ready.
- A line says **FAIL**? It shows a FAQ number. Look up that number in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## On the day: the terminal windows you need

| Window | What runs there | When |
|---|---|---|
| **1 · Ollama** | `ollama serve` (or the Ollama app) | only if you use Ollama instead of Groq |
| **2 · Bot** | your bot: `uvicorn app:app --reload` | steps 2 to 5, and all of Part 2 |
| **3 · Work** | your own commands: `python ask.py`, `pytest`... | always |

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

## Part 2 · TEST the bot

**First, start your step 5 bot in window 2 and leave it running:**
```bash
cd build/step5_agent
uvicorn app:app --reload
```
Then do the labs in window 3, from the **main project folder**.

| Lab | Your mission | Easy way to remember | Instructions | File you edit |
|---|---|---|---|---|
| 6 | Catch the chatbot when it lies | **Is it TRUE?** Truthful · Relevant · Uses the source · Even | [labs/LAB6.md](labs/LAB6.md) | `tests/test_chatbot.py` |
| 7 | Catch the agent when it does something dangerous | **Real Teams Make Outcomes Outstanding** (5 layers) | [labs/LAB7.md](labs/LAB7.md) | `tests/test_agents.py` |
| 8 | Check if the AI judge itself can be trusted | **CAP**: Consistent · Agrees · Price | [labs/LAB8.md](labs/LAB8.md) | `tests/my_scores.yaml` |

Each lab has a **CORE** part (for everyone) and a **STRETCH** part (if you finish early).

**Break the bot on purpose**, then write a test that catches it:
```bash
python plant_bug.py               # show the list of bugs
python plant_bug.py liar          # switch one bug on (no restart needed)
python plant_bug.py off           # switch all bugs off again
```

---

## Cheat sheet: all commands

```bash
# Setup (main project folder)
python check_setup.py               # is my laptop ready?
python checkpoint.py step3          # fell behind? get the finished step

# Part 1 (inside the step folder, for example: cd build/step1_model)
python ask_simple.py                # step 1: ask one question, get one answer
python ask.py                       # step 1: the same, with 6 small experiments to try (see its README)
uvicorn app_simple:app --reload     # step 2: the simplest API, then open http://localhost:8000/docs
uvicorn app:app --reload            # steps 2-5: start the bot, then open http://localhost:8000
python retrieval.py "price match"   # step 4: which rule pages does it find?
python agent.py 1043                # step 5: let the agents handle order 1043 (or: all, --graph)

# Part 2 (main project folder, with the step 5 bot running)
pytest tests -v                     # run all tests
pytest tests -v -k "not ai_judge"   # only the quick, free tests (no AI judge)
python tests/judge_the_judge.py     # lab 8
```

## Stuck?

1. Look in [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Most problems are there.
2. Use `python checkpoint.py stepN` to jump ahead.
3. Ask your neighbour. Nobody gets left behind.

---

## What's in this project

| Folder / file | What it is |
|---|---|
| `build/step1_model` … `build/step5_agent` | the 5 build steps (Part 1). Each has a README |
| `solutions/` | the finished code for every step and every test |
| `labs/` | instructions for Part 2 (labs 6, 7, 8) |
| `tests/` | the tests you write in Part 2 |
| `shared/config.py` | reads your settings from `.env` (which model, which judge) |
| `shared/data/policies/` | ShopKart's 10 rule pages (refunds, returns...) |
| `shared/data/orders.json` | 10 example orders to test with |
| `plant_bug.py` | switch bugs on and off for Part 2 |
| `checkpoint.py` | copy in the finished code if you fall behind |
| `check_setup.py` | checks if your laptop is ready |
| `tools/` | tools for the presenter |

## Want to build it again later? The 9 ideas

1. **Call a model.** A few lines of code with the OpenAI library. *(step 1)*
2. **Give it a job description.** Tell it its role, its topic, and its rules. *(step 1)*
3. **Give it memory.** Send the whole chat every time. *(step 2)*
4. **Put it behind an API**, so web pages, tools and tests can use it. *(step 2)*
5. **Give it a face.** A web page that calls the API. *(step 3)*
6. **Give it the book.** Find the right rule pages and tell the AI to answer only from them. *(step 4)*
7. **Give it tools.** The AI *asks* for an action, your code *does* it. Put hard rules in code, not in the prompt. *(step 5)*
8. **Split the work and record every step.** Planner → Implementer → Reviewer. The record makes it testable. *(step 5)*
9. **Test from the bottom up, and plant bugs on purpose.** Rule checks first, then an AI judge, then test the judge. *(Part 2)*

## For the presenter
- After changing any code, run `python tools/check_steps.py`. It checks that the step folders still match each other and that all code compiles.
- Practise without a real model: `cd tools` then `uvicorn fake_llm:app --port 9999`. In `.env`, set `LLM_BASE_URL=http://localhost:9999/v1` and `LLM_MODEL=fake`.

## Credits & licence
Built for AutomationSTAR 2026 by Gaurav Khurana ([gauravkhurana.com](https://gauravkhurana.com)). ShopKart, its orders and its rules are made up.
Tools used: FastAPI, OpenAI Python SDK, LangGraph, DeepEval, Ollama, pytest.
