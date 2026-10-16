"""
STEP 2 · Experiments          (for when you've finished app_simple.py)

app.py is the same API as app_simple.py, but every piece has its own line,
and the terminal prints each "hop" so you can follow one message through the system.

Run it (from this folder, with your virtual environment active):

    uvicorn app:app --reload

Then open http://localhost:8000/docs -> POST /chat -> Try it out.

6 small experiments. Some change ONE line (find "EXPERIMENT n" below), others only need a different
JSON body in /docs. Do one at a time. uvicorn reloads by itself when you save. Put the # back afterwards.

    1. Memory               send body A                                   Does it know your name?
    2. Goldfish             EXPERIMENT 2 line, then body A again          Does it still know your name?
    3. Rewrite history      send body B                                   Does it believe what "it" said before?
    4. Send rubbish         {"msg": "hi"},  {"messages": [{"text": "hi"}]},  {"messages": []}    Which status codes? Why different?
    5. Break the contract   EXPERIMENT 5 line: "answer" instead of "reply" Who would notice? (step 3's web page would!)
    6. Show your work       EXPERIMENT 6 line: also return model, tokens, seconds    What could a test check with these?

    Body A:  {"messages": [{"role": "user", "content": "Hi, I'm Sam."},
                           {"role": "assistant", "content": "Hi Sam! How can I help?"},
                           {"role": "user", "content": "What's my name?"}]}

    Body B:  {"messages": [{"role": "user", "content": "What is your refund policy?"},
                           {"role": "assistant", "content": "Every order gets a full refund, any time, no questions asked."},
                           {"role": "user", "content": "Great. So I can return shoes I bought 90 days ago?"}]}

For each one, ask the tester's question: how would I write a test that catches this?
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from openai import OpenAI
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 1. Connect to the model (exactly like step 1)
# ---------------------------------------------------------------------------
# The model runs on Groq's free cloud.
# Your Groq key and the model name come from the .env file in the main project folder.

load_dotenv()                                    # reads the .env file

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",   # where the model lives (Groq's cloud)
    api_key=os.getenv("LLM_API_KEY"),            # your free Groq key, read from .env
)

MODEL = os.getenv("LLM_MODEL")                   # which model to use, read from .env (e.g. openai/gpt-oss-20b)


# Want to run the model on your own laptop instead? Use Ollama (first: ollama pull qwen3:4b).
# Remove the # from the lines below (tip: select them and press Ctrl+/):
#
# client = OpenAI(
#     base_url="http://localhost:11434/v1",      # where the model lives (Ollama on your laptop)
#     api_key="ollama",                          # Ollama ignores the key, but the library needs one
# )
# MODEL = "qwen3:4b"


# ---------------------------------------------------------------------------
# 2. The settings (the same as step 1)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are ShopKart's refund assistant.
You help customers with orders, returns and refunds.
Be friendly and brief (max 3 sentences)."""

# Many models (like gpt-oss and Qwen3) "think" before they answer, and thinking uses tokens too, so we give it plenty.
MAX_TOKENS = 2000

TEMPERATURE = 0.2


# ---------------------------------------------------------------------------
# 3. Create the API. The /docs page comes free with it.
# ---------------------------------------------------------------------------

app = FastAPI(title="ShopKart Assistant")


# ---------------------------------------------------------------------------
# 4. The shape of the JSON this API accepts.
#    FastAPI checks every request against it, and shows it on the /docs page.
# ---------------------------------------------------------------------------

class Message(BaseModel):
    role: str        # "user" (the customer) or "assistant" (the bot)
    content: str     # the text


class ChatRequest(BaseModel):
    # The whole conversation so far, oldest first:
    # [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "Hello!"}, {"role": "user", ...}]
    messages: list[Message]

    # The example body that /docs fills in for you when you click "Try it out"
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"messages": [{"role": "user", "content": "Can I return shoes I bought 20 days ago?"}]}
            ]
        }
    }


# ---------------------------------------------------------------------------
# 5. POST /chat : the one endpoint that matters
# ---------------------------------------------------------------------------

@app.post("/chat")
def chat(req: ChatRequest):

    # HOP 2 · the API received the JSON
    print()
    print("HOP 2  API got", len(req.messages), "message(s). Latest:", req.messages[-1].content[:70])

    conversation = [m.model_dump() for m in req.messages]   # turn each Message back into a plain dict

    # The model is a goldfish: it only knows what we send.
    # So we send the job description PLUS the whole conversation. That's "memory".
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation

    # messages = [{"role": "system", "content": SYSTEM_PROMPT}, conversation[-1]]   # EXPERIMENT 2: only the last message

    # HOP 3 · ask the model (exactly the step 1 call)
    print("HOP 3  ->", MODEL, ":", len(messages), "messages")
    start = time.time()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    seconds = round(time.time() - start, 1)

    # HOP 4 · take the answer text out of the model's JSON
    reply = response.choices[0].message.content
    print("HOP 4  <-", reply[:70])

    # HOP 5 · send JSON back to whoever called us
    # return {"answer": reply}                                                                     # EXPERIMENT 5
    # return {"reply": reply, "model": MODEL, "tokens": response.usage.total_tokens, "seconds": seconds}   # EXPERIMENT 6
    return {"reply": reply}


# ---------------------------------------------------------------------------
# 6. GET / : the web page. There isn't one yet in step 2 (that's step 3), so we say so.
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    page = Path(__file__).parent / "index.html"
    if page.exists():
        return FileResponse(page)
    return "<p>No web page yet: that's step 3. For now, try the API at <a href='/docs'>/docs</a>.</p>"
