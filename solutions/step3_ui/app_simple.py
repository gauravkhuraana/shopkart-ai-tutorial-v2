"""
STEP 3 · The simple API (step 2's app_simple.py) plus one more endpoint: GET / serves the chat page.

The model runs on Groq's free cloud. Your Groq key and the model name come from the .env file
in the main project folder (LLM_API_KEY and LLM_MODEL).

Want Ollama on your laptop instead? Put a # in front of the two Groq lines,
and remove the # from the two Ollama lines (tip: put the cursor on a line and press Ctrl+/).

Run it (from this folder, with your virtual environment active):

    uvicorn app_simple:app --reload

Then open http://localhost:8000 and chat. The page is index_simple.html (that's the file you edit).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()   # reads the .env file in the main project folder


# 1. Connect to the model (exactly like step 1)

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("LLM_API_KEY"))   # Groq
# client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")                       # Ollama

MODEL = os.getenv("LLM_MODEL")     # Groq: the model name comes from .env
# MODEL = "qwen3:4b"               # Ollama


# 2. Create the API

app = FastAPI()


# 3. Describe the JSON this API accepts: the whole conversation so far.
#    Every message must have a role and a content, or FastAPI says no (422) before our code runs.

class Message(BaseModel):
    role: str        # "user" (the customer) or "assistant" (the bot)
    content: str     # the text


class ChatRequest(BaseModel):
    messages: list[Message]


# 4. The endpoint: POST /chat. Job description + conversation in, {"reply": "..."} out.

@app.post("/chat")
def chat(req: ChatRequest):
    conversation = [m.model_dump() for m in req.messages]   # turn each Message back into a plain dict

    job_description = {
        "role": "system",
        "content": "You are ShopKart's refund assistant. Be friendly and brief.",
    }
    messages = [job_description] + conversation

    response = client.chat.completions.create(model=MODEL, messages=messages)

    return {"reply": response.choices[0].message.content}


# 5. NEW in step 3: GET / hands the browser the chat page.

@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "index_simple.html")
