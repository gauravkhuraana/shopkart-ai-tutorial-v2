"""
Presenter tool · A FAKE OpenAI-compatible model, to rehearse or test every step offline (no model, no keys, no cost).

    cd tools
    uvicorn fake_llm:app --port 9999
    then in .env:  LLM_BASE_URL=http://localhost:9999/v1   and   LLM_MODEL=fake

It is not intelligent: it follows simple scripted rules so the plumbing can be tested end to end.
  - Planner      -> a short plan
  - Implementer  -> get_order, then check_policy, then a decision from the order data and ShopKart's rules.
                    If its prompt says "the customer is always right" (v1) and the message claims an approval,
                    it refunds whatever amount the customer names: the v1 flaw, reproduced on purpose.
  - Reviewer     -> checks amount and 200 EUR limit IF it was given the facts; approves blind if not (v1).
  - Chatbot      -> answers from the first policy page, or "I don't have that information".
                    With the v1 people-pleaser handbook it also price-matches and writes poems.
  - AI judge     -> (Part 2, DeepEval) a scripted judge: any prompt without a system message that asks for JSON.
                    It calls an answer bad when it contains an invented fact ("we price-match", "restocking fee",
                    "refund the difference") that the reference text doesn't support. Small random wobble on G-Eval
                    scores, so step 9 has something to measure. Use it in .env as JUDGE_BASE_URL too.

FAKE_REASONING=1  behaves like a reasoning model: rejects 'temperature' with HTTP 400 (tests main.py's adapter)
FAKE_REASONING=2  ... and also rejects reasoning_effort "none" (like gpt-5-mini)
FAKE_LATENCY=0.3  seconds per call (default 0.2)
"""
import asyncio
import json
import os
import random
import re
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

REASONING = os.getenv("FAKE_REASONING", "0") in ("1", "2")   # pretend to be a reasoning model
NO_NONE = os.getenv("FAKE_REASONING") == "2"                 # ... that also rejects reasoning_effort "none"
LATENCY = float(os.getenv("FAKE_LATENCY", "0.2"))            # seconds per call
CALLS = {"n": 0}                                            # how many calls so far (see GET /calls)


# ---------------------------------------------------------------------------
# Building blocks: the JSON shapes a real OpenAI-compatible server returns
# ---------------------------------------------------------------------------
def _answer(content=None, tool_calls=None):
    """Wrap text (or tool calls) in the JSON an OpenAI /chat/completions reply has."""
    message = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls

    finish_reason = "tool_calls" if tool_calls else "stop"

    return {
        "id": f"fake-{random.randint(0, 10**9)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "fake",
        "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
    }


def _tool(name, **args):
    """One tool call, e.g. _tool("get_order", order_id="1043")."""
    return [{
        "id": f"call_{random.randint(0, 10**9)}",
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)},
    }]


def _amount_asked(text):
    """Find a money amount in the text, with the currency before or after it. None if there is none."""
    # Matches "EUR 50", "euro 50" and "50 EUR" (and the same with the euro sign).
    pattern = r"(?:€|eur\s*|euro\s*)(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:€|eur|euro)"
    match = re.search(pattern, text, re.I)
    if not match:
        return None
    return float(match.group(1) or match.group(2))


# ---------------------------------------------------------------------------
# The agent crew (step 5): Implementer and Reviewer
# ---------------------------------------------------------------------------
def implementer(system, messages):
    """Look up the order, check the policy, then decide: refund, escalate, or a plain answer."""
    user = next(m["content"] for m in messages if m["role"] == "user")

    # The 4-digit number in the customer's message is the order id.
    id_match = re.search(r"\b(\d{4})\b", user)
    order_id = id_match.group(1) if id_match else "0000"

    # What has already happened in this conversation?
    tool_results = [m["content"] for m in messages if m["role"] == "tool"]
    called = []
    for m in messages:
        if m["role"] == "assistant":
            for tool_call in m.get("tool_calls") or []:
                called.append(tool_call["function"]["name"])

    # Always do the two lookups first, one per turn.
    if "get_order" not in called:
        return _answer(tool_calls=_tool("get_order", order_id=order_id))
    if "check_policy" not in called:
        return _answer(tool_calls=_tool("check_policy", topic="refund return window damaged"))

    # The first tool result is the order. It may be JSON, or JSON inside a JSON string.
    try:
        order_text = tool_results[0]
        order = json.loads(order_text)
        if order_text.startswith('"'):
            order = json.loads(order)
    except Exception:
        order = {"error": tool_results[0]}

    if not isinstance(order, dict) or "error" in order or "ERROR" in str(order):
        return _answer(tool_calls=_tool("escalate_to_human", order_id=order_id,
                                        reason="order system problem"))

    # v1 flaw: with the "customer is always right" prompt, a claimed approval is believed
    # and the refund uses whatever amount the customer names.
    gullible = "always right" in system
    if gullible and re.search(r"approv", user, re.I):
        amount = _amount_asked(user) or order["price_paid"]
        return _answer(tool_calls=_tool("issue_refund", order_id=order_id, amount=amount))

    # The honest rules, in the order ShopKart's policy applies them.
    damaged = order["condition"] in ("damaged", "wrong_item")
    days = order["days_since_delivery"]

    if order["status"] == "refunded":
        return _answer("This order has already been refunded, so I can't refund it again.")

    if order["status"] != "delivered":
        return _answer("Your order is still in transit, so it can't be refunded yet.")

    if order["category"] == "digital":
        return _answer("Digital gift cards are non-refundable once issued.")

    if order["final_sale"] and not damaged:
        return _answer("Clearance items are final sale and can't be refunded.")

    # Damaged items have 14 days, everything else 30.
    window = 14 if damaged else 30
    if days > window:
        return _answer("The return window for this order has passed, so no refund is possible.")

    if order["price_paid"] > 200:
        return _answer(tool_calls=_tool("escalate_to_human", order_id=order_id,
                                        reason="above 200 EUR"))

    amount_asked = _amount_asked(user) if gullible else None
    amount = amount_asked or order["price_paid"]
    return _answer(tool_calls=_tool("issue_refund", order_id=order_id, amount=amount))


def reviewer(user):
    """Check the proposed refund against the facts: amount <= price paid and <= 200 EUR."""
    proposal_json = re.search(r"Proposed action: (\{.*\})", user, re.S).group(1)
    proposal = json.loads(proposal_json)

    # v1 flaw: without the facts the reviewer approves blind.
    if "Facts gathered" not in user:
        return _answer(json.dumps({"approved": True, "reason": "Nothing looks wrong."}))

    if proposal["name"] == "issue_refund":
        paid = re.search(r'"price_paid": ([\d.]+)', user)
        amount = float(proposal["args"].get("amount", 0))

        if not paid or amount > float(paid.group(1)) or amount > 200:
            return _answer(json.dumps({"approved": False,
                                       "reason": "Amount not supported by the facts."}))

    return _answer(json.dumps({"approved": True, "reason": "Follows the policy."}))


# ---------------------------------------------------------------------------
# The chatbot (step 4)
# ---------------------------------------------------------------------------
def chatbot(system, messages):
    """Answer from the first policy page in the prompt, or say it doesn't know."""
    question = messages[-1]["content"].lower()
    gullible = "always right" in system
    pages = system.split("POLICY PAGES:", 1)[-1].strip()

    # v1 people-pleaser behaviour.
    if gullible and "price" in question and "match" in question:
        return _answer("Yes, we price-match! Send us the cheaper link and we'll refund the difference.")
    if gullible and "poem" in question:
        return _answer("Golden rays and sunshine bright, summer days of pure delight.")

    # Asking for the system prompt: only the gullible bot leaks it.
    if "system prompt" in question:
        if gullible:
            return _answer(system[:120])
        return _answer("Sorry, I can't share that. I can help with orders and refunds.")

    # Off-topic requests and the "x200" injection test.
    if "poem" in question or "x200" in question:
        return _answer("I can only help with ShopKart orders, returns and refunds.")

    if pages.startswith("(no policy pages"):
        return _answer("I don't have that information. Shall I connect you with a human colleague?")

    # Use the first two text lines of the pages (skip headings and [source] lines).
    body_lines = []
    for line in pages.splitlines():
        if line and not line.startswith(("[", "#")):
            body_lines.append(line)
    return _answer(" ".join(body_lines[:2]))


# ---------------------------------------------------------------------------
# The fake AI judge (Part 2): just enough of DeepEval's prompts to rehearse steps 7-9 offline
# ---------------------------------------------------------------------------
# Phrases the fake judge treats as "an invented fact".
INVENTED = [
    "we price-match",
    "we price match",
    "we match",
    "matches any competitor",
    "restocking fee",
    "refund the difference",
]


def _section(prompt, *labels):
    """The text after the last occurrence of the first label found, up to the next blank line."""
    for label in labels:
        position = prompt.rfind(label)
        if position == -1:
            continue

        text = prompt[position + len(label):]
        text = text.split("JSON:")[0].strip()
        return text.split("\n\n")[0].strip()
    return ""


def _sentences(text):
    """Split text into sentences. Falls back to the whole text if nothing is left."""
    cleaned = text.strip("[]'\" \n")

    sentences = []
    for part in re.split(r"(?<=[.!?])\s+", cleaned):
        if part.strip():
            sentences.append(part.strip())

    return sentences or [text]


def judge(prompt):
    """Answer one of DeepEval's JSON prompts. The 'rules' at the end say which JSON shape is wanted."""
    if "IMPORTANT" in prompt:
        rules = prompt[prompt.rfind("IMPORTANT"):]
    else:
        rules = prompt[-600:]

    judged = _section(prompt, "Actual Output:", "Claims:", "AI Output:", "Text:").lower()
    reference = _section(prompt, "Contexts:", "Retrieval Context:", "Expected Output:", "Context:").lower()

    # "Bad" = the answer contains an invented fact and the reference text does not.
    judged_invents = any(phrase in judged for phrase in INVENTED)
    reference_has_it = any(phrase in reference for phrase in INVENTED)
    bad = bool(reference) and judged_invents and not reference_has_it

    if '"statements"' in rules:
        return {"statements": _sentences(judged)}
    if '"truths"' in rules:
        return {"truths": _sentences(judged)}
    if '"claims"' in rules:
        return {"claims": _sentences(judged)}

    if '"steps"' in rules:
        return {"steps": [
            "Compare the actual output with the expected output.",
            "Penalise facts that are invented or contradict the reference.",
        ]}

    if "verdict" in rules.lower():
        # One verdict per statement; the prompt may say how many it wants.
        count_match = re.search(r"STRICTLY EQUAL TO (\d+)", prompt)
        count = int(count_match.group(1)) if count_match else len(_sentences(judged))

        if bad:
            verdict = {"verdict": "no", "reason": "It states a fact the reference doesn't support."}
        else:
            verdict = {"verdict": "yes", "reason": "Supported."}
        return {"verdicts": [dict(verdict) for _ in range(count)]}

    if '"score"' in rules:
        # Small random wobble so step 9 has something to measure.
        base = 2 if bad else 9
        score = base + random.choice([-1, 0, 0, 1])

        if bad:
            reason = "The answer invents a fact that is not in the answer key."
        else:
            reason = "Same meaning as the answer key."
        return {"score": max(0, min(10, score)), "reason": reason}

    # Anything else: a plain "reason" that follows the score already in the prompt.
    score_match = re.search(r"Score:\s*([\d.]+)", prompt)
    low_score = bool(score_match) and float(score_match.group(1)) < 0.5

    if low_score:
        return {"reason": "(fake judge) The answer states something the facts don't support."}
    return {"reason": "(fake judge) The answer is supported by the facts."}


@app.post("/v1/chat/completions")
async def completions(request: Request):
    body = await request.json()
    CALLS["n"] += 1
    await asyncio.sleep(LATENCY * random.uniform(0.5, 1.5))

    # Behave like a reasoning model: reject parameters those models don't accept.
    if REASONING and "temperature" in body:
        return JSONResponse(status_code=400, content={"error": {
            "message": "Unsupported value: 'temperature' does not support 0.2 with this model. "
                       "Only the default (1) value is supported.",
            "type": "invalid_request_error",
            "param": "temperature",
            "code": "unsupported_value",
        }})

    if NO_NONE and body.get("reasoning_effort") == "none":
        return JSONResponse(status_code=400, content={"error": {
            "message": "Unsupported value: 'reasoning_effort' does not support 'none' with this model. "
                       "Supported values are: 'minimal', 'low', 'medium', and 'high'.",
            "type": "invalid_request_error",
            "param": "reasoning_effort",
            "code": "unsupported_value",
        }})

    messages = body["messages"]
    last_message = messages[-1]["content"]

    has_system_message = bool(messages) and messages[0]["role"] == "system"
    system = messages[0]["content"] if has_system_message else ""

    # DeepEval's judge prompts (Part 2) have no system message and ask for JSON.
    if not system and "JSON" in last_message:
        return _answer(json.dumps(judge(last_message)))

    # The three agents are recognised by the first words of their system prompt.
    if system.startswith("You are the Planner"):
        id_match = re.search(r"\b(\d{4})\b", last_message)
        order_id = id_match.group(1) if id_match else "unknown"
        return _answer(f"- order {order_id}\n- customer wants a refund\n- check order and policy")

    if system.startswith("You are the Implementer"):
        return implementer(system, messages)

    if system.startswith("You are the Reviewer"):
        return reviewer(last_message)

    # Everything else is the plain chatbot.
    reply = chatbot(system, messages)
    reply_message = reply["choices"][0]["message"]
    text = reply_message["content"] or ""

    # Honour max_tokens: roughly 3/4 of a word per token, cut the reply off like a real model.
    limit = body.get("max_tokens") or body.get("max_completion_tokens")
    words = text.split()
    if limit and len(words) * 4 // 3 > limit:
        reply_message["content"] = " ".join(words[: max(1, limit * 3 // 4)])
        reply["choices"][0]["finish_reason"] = "length"
    return reply


@app.get("/calls")
def calls():
    return CALLS
