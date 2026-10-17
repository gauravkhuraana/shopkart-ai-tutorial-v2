"""
STEP 1 · The simplest possible LLM call: one question in, one answer out.

The model runs on Groq's free cloud. Your Groq key and the model name come from the .env file
in the main project folder (LLM_API_KEY and LLM_MODEL).

Want Ollama on your laptop instead? Put a # in front of the two Groq lines,
and remove the # from the two Ollama lines (tip: put the cursor on a line and press Ctrl+/).

Run it (from this folder, with your virtual environment active):

    python ask_simple.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads the .env file in the main project folder


# 1. Connect to the model

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("LLM_API_KEY"),
)  # Groq
# client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")                       # Ollama


# 2. Send the job description (system) and the customer's question (user)

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),  # Groq: the model name comes from .env
    # model="qwen3:4b",             # Ollama
    messages=[
        {
            "role": "system",
            "content": "You are ShopKart's refund assistant. Be friendly and brief.",
        },
        {
            "role": "user",
            "content": "Can I return shoes I bought 20 days ago?",
        },
    ],
    max_tokens=500,  # the token limit
    temperature=0.7,  # the creativity dial
)


# 3. Print the answer

print("Answer", response.choices[0].message.content)
print("--------------------------------------------")
# print("finish reason", response.choices[0].finish_reason)
