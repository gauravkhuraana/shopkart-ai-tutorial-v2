"""
STEP 4 · Ground it (the simple version)      (slide 11 · Knowledge lights up)

This is step 3's app_simple.py plus ONE new idea: before the model answers, a tiny librarian (the
retrieve() function below) finds the relevant ShopKart policy pages and we put them into the prompt, with one rule: answer ONLY from these pages.
That's RAG: Retrieval-Augmented Generation.

        question --> librarian --> policy pages --+
                                                  +--> model --> grounded answer
        job description + conversation -----------+

Wrong pages in -> confident wrong answer out. So when a grounded bot is wrong, first ask "what did the librarian bring?"

The API now returns more JSON:  {"reply": "...", "sources": ["returns.md", ...], "context": ["...page text...", ...]}
The page (index_simple.html) shows the sources under the answer.

This is the finished version (all 3 changes done).

Run it (from this folder, with your virtual environment active):

    uvicorn app_simple:app --reload

Then open http://localhost:8000 and ask "Do you price-match?". The terminal shows the pages the librarian brought.
Want saved chats, Show JSON, Orders and Agent mode? That's app.py (the full version).
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()  # reads the .env file in the main project folder


# 1. Connect to the model (exactly like step 3)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("LLM_API_KEY"),
)  # Groq
# client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")                       # Ollama

MODEL = os.getenv("LLM_MODEL")  # Groq: the model name comes from .env
# MODEL = "qwen3:4b"               # Ollama


# 2. Create the API

app = FastAPI()


# 3. The JSON this API accepts (unchanged): the whole conversation so far.


class Message(BaseModel):
    role: str  # "user" (the customer) or "assistant" (the bot)
    content: str  # the text


class ChatRequest(BaseModel):
    messages: list[Message]


# 4. NEW in step 4: the librarian. Nothing to edit here, just read it.
#    The "book" is the 10 policy files in shared/data/policies. Each file is one page.

POLICY_DIR = Path(__file__).resolve().parents[2] / "shared" / "data" / "policies"

# Read every policy file into a list. Each page looks like {"name": "returns.md", "text": "...the whole file..."}
PAGES = []
for file in sorted(POLICY_DIR.glob("*.md")):
    PAGES.append(
        {
            "name": file.name,
            "text": file.read_text(encoding="utf-8"),
        }
    )

# Small words that say nothing about the topic. The librarian ignores them.
STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "at",
    "for",
    "with",
    "is",
    "are",
    "was",
    "be",
    "i",
    "you",
    "we",
    "my",
    "your",
    "it",
    "this",
    "that",
    "can",
    "do",
    "does",
    "did",
    "have",
    "will",
    "what",
    "when",
    "how",
    "after",
    "about",
    "get",
    "so",
}


def get_words(text):
    """Break a text into its important words: lower-case, no small words, and no endings."""
    important = set()
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if word in STOPWORDS:
            continue
        if len(word) > 4:
            word = re.sub(
                r"(ing|ed|es|s)$", "", word
            )  # "returns" and "returned" both become "return"
        important.add(word)
    return important


def retrieve(question, top_k=3):
    """Find the pages that share the most words with the question. Gives back [] if no page shares any."""
    question_words = get_words(question)

    # Give every page a score: how many important words it shares with the question
    scored_pages = []
    for page in PAGES:
        shared_words = question_words & get_words(page["text"])
        score = len(shared_words)
        if score > 0:
            scored_pages.append((score, page))

    # Best score first, then keep only the top_k pages
    scored_pages.sort(
        key=lambda item: item[0],
        reverse=True,
    )
    best_pages = []
    for score, page in scored_pages[:top_k]:
        best_pages.append(page)
    return best_pages


# 5. The job description, now with GROUNDING RULES (this is what stops it making things up).

SYSTEM_PROMPT = """You are ShopKart's refund assistant. Be friendly and brief (max 3 sentences).
Answer ONLY using the POLICY PAGES below, and use the exact numbers written there. Do not use outside knowledge.
If the answer is not in the policy pages, say so and offer a human colleague.
Never invent policies, discounts, fees or compensation. Never promise a refund.
If it isn't about ShopKart orders, returns or refunds, politely say you can only help with those."""


# 6. The endpoint: POST /chat. Question + conversation in, {"reply": "...", "sources": [...]} out.


@app.post("/chat")
def chat(req: ChatRequest):
    question = req.messages[-1].content  # what the customer just asked

    # The librarian brings the policy pages that match the question (open-book exam)
    pages = retrieve(question)

    # Show in the terminal which pages the librarian brought (look here after every question)
    page_names = []
    for page in pages:
        page_names.append(page["name"])
    print("librarian brought:", page_names)

    # Put the pages into one block of text for the prompt
    policy_text = ""
    for page in pages:
        policy_text = policy_text + "[" + page["name"] + "]\n" + page["text"] + "\n\n"
    if policy_text == "":
        policy_text = "(no policy pages found)"

    # Convert each validated Message object into a plain dictionary for the model.
    conversation = []
    for message in req.messages:
        conversation.append(message.model_dump())

    # The job description now carries the policy pages too. Then comes the whole conversation.
    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT + "\n\nPOLICY PAGES:\n" + policy_text,
    }
    messages = [system_message] + conversation

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    reply = response.choices[0].message.content

    # The evidence goes back too: which pages, and their text
    sources = []
    context = []
    for page in pages:
        sources.append(page["name"])
        context.append(page["text"])
    return {
        "reply": reply,
        "sources": sources,
        "context": context,
    }


# 7. GET / hands the browser the chat page (from step 3).


@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "index_simple.html")


# 8. POST /agent switches on by itself in step 5, when agent_simple.py sits next to this file.
#    You don't need to touch this in step 4.


class AgentRequest(BaseModel):
    message: str


@app.post("/agent")
def agent(req: AgentRequest):
    if not (Path(__file__).parent / "agent_simple.py").exists():
        raise HTTPException(
            status_code=404,
            detail="Agent mode arrives in step 5 (agent_simple.py).",
        )
    from agent_simple import (
        run_agent,
    )  # imported here so step 4 runs without agent_simple.py

    return run_agent(req.message)
