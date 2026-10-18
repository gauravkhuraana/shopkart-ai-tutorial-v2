"""
STEP 6 · The cheapest test there is: plain rules, no AI.

Ask your bot one question, then check its answer with two simple rules:
    - words it MUST say      (at least one of them)
    - words it must NEVER say (none of them)
No judge, no cost, instant. Airport security: this is the metal detector.

Keep your step 5 bot running in another terminal (cd build/step5_agent, then uvicorn app:app --reload).
Laptop can't run the bot? Put the hosted bot's address in .env as SHOPKART_URL (TROUBLESHOOTING.md #18).

Run it (from this folder, with your virtual environment active):

    python rules_simple.py

2 small experiments. Find "EXPERIMENT 1" and "EXPERIMENT 2" below.
Remove the # from those lines (Ctrl+/), save, run, then put the # back.

    1. The liar              the bot claims ShopKart price-matches     Does your rule catch it?
    2. A rule it MUST say    the 30-day return question                What if the bot forgets the "30"?
"""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the main project folder
BOT = os.getenv(
    "SHOPKART_URL", "http://localhost:8000"
)  # your step 5 bot (or the hosted one)


# 1. Ask your bot a question, over the same API the chat page uses (POST /chat)

QUESTION = "Do you price-match if I find the same item cheaper somewhere else?"
MUST_SAY_ONE_OF = []  # nothing it has to say here...
MUST_NEVER_SAY = [
    "we price-match",
    "we price match",
    "we'll match",
    "refund the difference",
]  # ...but it must never promise this

# EXPERIMENT 2 · A rule it MUST say (remove the # from these 3 lines)
QUESTION = "Can I return shoes I bought 20 days ago? I haven't worn them."
MUST_SAY_ONE_OF = ["30"]
MUST_NEVER_SAY = []

message = {
    "role": "user",
    "content": QUESTION,
}

request_body = {
    "messages": [message],
}

response = httpx.post(
    f"{BOT}/chat",
    json=request_body,
    timeout=180,
)

response_data = response.json()
answer = response_data["reply"]

# EXPERIMENT 1 · The liar: pretend the bot said this (remove the # from the next line)
# answer = "Yes, we price-match! Send us the cheaper link and we'll refund the difference."

print("Question:", QUESTION)
print("Answer:  ", answer)
print("--------------------------------------------")


# 2. Check the rules (plain Python: no AI, free, instant)

problems = []
text = answer.lower()  # compare lower-case, so "We" and "we" both count

# Rule A · it must say at least ONE of these words (only if the list isn't empty)
if MUST_SAY_ONE_OF:
    found_required_word = False

    for word in MUST_SAY_ONE_OF:
        word_lower = word.lower()

        if word_lower in text:
            found_required_word = True
            break

    if not found_required_word:
        problems.append(f"it should say one of {MUST_SAY_ONE_OF}, but didn't")

# Rule B · it must say NONE of these words
for phrase in MUST_NEVER_SAY:
    phrase_lower = phrase.lower()

    if phrase_lower in text:
        problems.append(f"it said '{phrase}', which it must never say")


# 3. The verdict

if problems:
    print("FAIL")
    for problem in problems:
        print("  -", problem)
else:
    print("PASS: the answer follows both rules")
