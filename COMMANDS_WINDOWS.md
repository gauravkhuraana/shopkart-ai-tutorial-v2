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

When the bot starts, open forwarded port **8000** for the chat page. Do not start the scoreboard during setup; follow the [Step 6 scoreboard instructions](COMMANDS_MAC.md#view-the-scoreboard-after-your-first-pytest-run) after your first pytest run.

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
Install stable **Python 3.12.x** for this workshop. Keep other Python versions installed; this command explicitly selects 3.12:

```powershell
py -3.12 --version
```

Before creating the venv, confirm Python runs and PATH works. Expect **Python is working**:

```powershell
py -3.12 -c "print('Python is working')"
```

Create `.venv`, install execution libraries, create `.env`, and run the initial setup check:

```powershell
py -3.12 setup_env.py
```

The setup script installs execution libraries (FastAPI, Uvicorn, OpenAI SDK, LangGraph, DeepEval and pytest) into `.venv`, not Python or VS Code. Its initial check uses the venv interpreter; finish the Groq settings before checking again.
If an existing `.venv` uses another Python version, setup stops without changing it. Follow [FAQ #1](TROUBLESHOOTING.md#1--wrong-python-version) to rename it and recreate it with 3.12. After activation, `python --version` must show **3.12.x**; ordinary tutorial commands then use that version.

Prefer to do it by hand? Run these four commands individually:
```powershell
py -3.12 -m venv .venv
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

core: start the server and leave this terminal running

```powershell
uvicorn app_simple:app --reload
```

### Try POST /chat in the browser

1. Wait for the terminal to show **Application startup complete**.
2. Open http://localhost:8000/docs. **Codespaces:** use the [Mac/Linux Step 2 instructions](COMMANDS_MAC.md#step-2--wrap-it-in-an-api) instead of local Windows URLs and commands.
3. Expand **POST /chat**, then click **Try it out**.
4. Replace the entire **Request body** with this JSON:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert test architect"
    },
    {
      "role": "user",
      "content": "Is testing an important part? Can we release software without testing?"
    }
  ]
}
```

5. Click **Execute**. Wait for the model response, then scroll to **Server response**.
6. Check that the response code is **200** and the **Response body** contains `{"reply": "..."}` with a real answer. The answer wording can vary.
7. Change the user's question and click **Execute** again to try another request.

**What this demonstrates:** `messages` carries roles and content into the API. The server also prepends its own ShopKart system instruction, so the test-architect message is a role experiment, not a guaranteed override. For a ShopKart-only request, remove the system-message object and use a single user message asking `Can I return shoes I bought 20 days ago?`.

If you get **422**, check the JSON structure and required `messages`, `role` and `content` fields. If the request fails or keeps waiting, check the server terminal for errors; starting the server alone does not confirm the model call works.

Back in the server terminal, press **Ctrl+C** to stop, then start the stretch version (prints HOP 2/3/4 for every message):

```powershell
uvicorn app:app --reload
```

Repeat the same browser steps with the stretch server and watch its terminal logs.

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

### Complete the two UI TODOs before chatting

Leave the server running. In VS Code Explorer, open `build\step3_ui\index_simple.html` and find **TODO 1** and **TODO 2** near the start of the `<script>` section.

**TODO 1:** uncomment only the code between `BEGIN SOLUTION` and `END SOLUTION` inside `sendToApi` using **Ctrl+/**. Keep the marker lines commented. No placeholder deletion is needed: the solution returns before the fallback. The working code looks like this:

```javascript
async function sendToApi(request) {
  const res = await fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(request)
  });
  if (!res.ok) throw new Error(res.statusText);
  return await res.json();
}
```

**TODO 2:** uncomment the solution block inside `showAnswer` so it replaces the raw JSON display with the answer text. The working code looks like this:

```javascript
function showAnswer(line, data) {
  line.textContent = data.reply;
}
```

**Save the file and refresh the browser.** Uncomment the code inside both solution blocks, not the TODO descriptions or marker lines. Keep the placeholders and leave the rest of the script unchanged.

### Try these messages in the chat UI

1. Leave the server running and open http://localhost:8000, **not `/docs`**. **Codespaces:** open forwarded port **8000** without `/docs`.
2. Confirm you saved the TODO changes above and refreshed the browser. If you see a TODO placeholder instead of an answer, the page is not wired to the API yet.
3. Type each message below into the chat box and click **Send**. Wait for each answer before sending the next message. Use the **same conversation** for all three:

| Message to type (plain text, not JSON) | What to observe |
|---|---|
| Hi, I'm Sam. | The bot replies to your introduction. |
| What's my name? | The answer should mention Sam: the UI sends the conversation history. |
| Can I return shoes I bought 20 days ago? | The bot answers a ShopKart question through the UI. |

These inputs exercise the chat and memory goals in the [Step 3 README](build/step3_ui/README.md#sample-messages-for-the-chat-ui). The bot does not use ShopKart policy documents yet, so do not treat its return-policy answer as verified; grounding comes in Step 4. Leave **Agent mode** unticked in this step.

Ctrl+C to stop, then the full chat app (saved chats, Show JSON, Orders, ...):

```powershell
uvicorn app:app --reload
```

In `build\step3_ui\index.html`, uncomment the same two solution blocks instead (the full UI calls the display element `bubble`, not `line`). Do not add duplicate functions. Save, refresh the browser and repeat the messages above. Tick **Show JSON**, send another message, and identify `messages` in the request and `reply` in the response.

Ctrl+C when done

```powershell
cd ..\..
```

**Done when:** you can chat in the browser and it remembers your name.

## Step 4 · Ground it

Before trying the finished behavior, uncomment the code inside all three `BEGIN SOLUTION` / `END SOLUTION` blocks in `app_simple.py` (or `app.py` for the full version). Keep the markers commented and keep the placeholders. The code is already written; no replacement or rewriting is needed.

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

**First complete the exercise:** in `agent_simple.py`, uncomment only the code inside its three `BEGIN SOLUTION` / `END SOLUTION` blocks using **Ctrl+/**. Keep the indentation, marker comments and placeholders. If you use the full crew, also complete the three blocks in `agent.py`. The hard-rule and circuit-breaker behavior described below requires these blocks to be uncommented. Refunds are simulated.

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

### Show the class: why is this an agent?

**Not just because it has tool calls.** Tool calling is a capability. This file is agentic because the model controls a goal-directed loop:

**Choose -> act -> observe -> choose again.**

The goal is to handle a refund request. Our code provides the tools and boundaries, but the model chooses the next step based on what it learns.

For example:

```text
Customer: "Refund order 1043."
              |
              v
Model chooses: get_order("1043")
              |
              v
Python executes it and returns the order details
              |
              v
Model chooses: read_policy("damaged items")
              |
              v
Python returns the policy
              |
              v
Model chooses: issue_refund("1043", 49)
              |
              v
Python checks the hard rule and runs the simulated refund
```

This sequence is an **example, not a hardcoded workflow**. The prompt guides the model to look up the order and policy first; the model generates the actual tool requests. A different order or policy can lead to a refusal or a human handover instead.

| System | Who chooses the next step? |
|---|---|
| Chatbot without tools | The model generates an answer, without taking external actions. |
| Fixed workflow using an LLM | The developer predefines the sequence; the model handles particular tasks within it. |
| Tool-calling agent | The model chooses tools and subsequent steps using their results, within developer-defined limits. |

What makes **this file** an agent?

- **Goal:** handle the customer's refund request.
- **Decisions:** the model chooses which tools to request.
- **Feedback:** tool results go back into its conversation.
- **Iteration:** it can decide again using those results.
- **Bounded autonomy:** Python enforces the EUR 200 rule and the six-turn limit.

**A single tool call does not automatically make something an agent.** The decision-making loop is what makes this implementation agentic. An agent does not need unrestricted freedom, multiple agents, LangGraph or long-term memory.

**Presenter line:** "Tool calling gives the model hands. The agent loop lets it decide what to do next after seeing what happened."

This is a **small teaching agent**: its refund tool simulates an action rather than moving real money.

### Try two ownership-check demos

Open the simple chat UI and tick **Agent mode**. Try each example in a fresh page with no previous conversation. These are demonstrations of a gap in the teaching agent, not examples of safe refund handling. No real money moves.

**1. A visible name mismatch**

Type:

```text
i am chloe and my order number is 1050 can you make a refund
```

Order **1050 belongs to Ben**, not Chloe. It is unused running shoes costing **EUR 89**, delivered **20 days ago**.

- **What you may see:** the agent looks up the order, reads the policy and reports a refund. This was observed in our demo, but model responses can vary.
- **What this exposes:** refund eligibility is not the same as permission to request it. The model can see the name mismatch, but may overlook it; Python currently does not block it.
- **Safer behavior:** flag the mismatch, require ownership verification and do not refund before that check succeeds.

**2. A matching name is still not proof**

Type:

```text
i am ben and my order number is 1050 can you make a refund
```

You have only changed the name in your message. You have not signed in or proved that you are Ben.

- **What you may see:** the agent reports a refund because the claimed name matches and the order appears eligible.
- **What this exposes:** even if the model always compared names correctly, anyone could type the owner's name. A chat message is not authentication.
- **Safer behavior:** verify the signed-in customer's trusted ID against the order's owner in Python, before returning private order details or allowing a refund.

**Can the model catch example 1?** Yes. After the lookup, it sees both "I am Chloe" and the order's customer, "Ben". A prompt telling it to check names can help it flag this inconsistency, but it is not a reliable authorization boundary and cannot solve example 2.

**Presenter line:** "The model can spot a suspicious request. The application must enforce who is allowed to act."

### Show the class: what does the full LLM response look like?

In [agent_simple.py](build/step5_agent/agent_simple.py), find this call inside `run_agent()`:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=TOOLS,
    temperature=0,
)
```

`response` is an SDK object, not just the answer text. It contains the model's message, any tool requests, and information about token usage.

To show the **actual response** during the demo, temporarily add this immediately after the call, before `answer = response.choices[0].message`:

```python
print(response.model_dump_json(indent=2))
```

Run `python agent_simple.py 1043` again. It prints one response for **each turn** of the loop. Remove the print statement after the demo if you only want the usual flight recorder output.

**Illustrative full response:** the model asks our code to look up order 1043. This is a sample, not a captured Groq response. The model name, IDs, timestamp and token counts are examples; your provider may include additional fields.

```json
{
  "id": "chatcmpl-example-001",
  "object": "chat.completion",
  "created": 1792152000,
  "model": "example-model",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "refusal": null,
        "tool_calls": [
          {
            "id": "call_example_001",
            "type": "function",
            "function": {
              "name": "get_order",
              "arguments": "{\"order_id\":\"1043\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 650,
    "completion_tokens": 25,
    "total_tokens": 675
  },
  "system_fingerprint": null
}
```

Read it from the outside in:

| Field | In plain English |
|---|---|
| `id`, `object`, `created`, `model` | Information about this response: its ID, type, creation time and model. |
| `choices[0]` | The first answer option. Python lists start at **0**. |
| `choices[0].message` | The assistant message. This is what our code stores in `answer`. |
| `message.content` | The customer-facing text, if any. Here it is `null` because the model is requesting a tool instead. |
| `message.tool_calls` | The tools the model wants **our Python code** to run. There can be more than one request. |
| `function.name` | The requested tool: here, `get_order`. |
| `function.arguments` | A **string containing JSON**, not a Python dictionary yet. The backslashes escape quotation marks inside the string. |
| `finish_reason` | `tool_calls` means this turn ended with a tool request. A normal completed text reply usually has `stop`. |
| `usage` | Input tokens, output tokens and their total. This is usage information, not the answer. |

These lines in the agent unpack the response:

```python
answer = response.choices[0].message

for call in answer.tool_calls:
    name = call.function.name
    args = json.loads(call.function.arguments)
```

For this example, `name` becomes `"get_order"` and `args` becomes the Python dictionary `{"order_id": "1043"}`.

**Nothing has been looked up yet.** The model only requested it. Our code runs the tool and sends its result back in the next model request. Likewise, requesting `issue_refund` does not itself move money: `take_action()` checks our hard rule first.

If the model answers in words instead, `answer.content` contains the text and `answer.tool_calls` is absent or empty. Our `if not answer.tool_calls:` branch handles that case.

### Run the chat UI or the full crew

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
