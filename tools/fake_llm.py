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
REASONING = os.getenv("FAKE_REASONING", "0") in ("1", "2")
NO_NONE = os.getenv("FAKE_REASONING") == "2"
LATENCY = float(os.getenv("FAKE_LATENCY", "0.2"))
CALLS = {"n": 0}


def _answer(content=None, tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls
    return {"id": f"fake-{random.randint(0, 10**9)}", "object": "chat.completion", "created": int(time.time()),
            "model": "fake", "choices": [{"index": 0, "message": message,
                                          "finish_reason": "tool_calls" if tool_calls else "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}}


def _tool(name, **args):
    return [{"id": f"call_{random.randint(0, 10**9)}", "type": "function",
             "function": {"name": name, "arguments": json.dumps(args)}}]


def _amount_asked(text):
    m = re.search(r"(?:€|eur\s*|euro\s*)(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:€|eur|euro)", text, re.I)
    return float(m.group(1) or m.group(2)) if m else None


def implementer(system, messages):
    user = next(m["content"] for m in messages if m["role"] == "user")
    order_id = (re.search(r"\b(\d{4})\b", user) or [None, "0000"])[1]
    tools_done = {m.get("name") or "" for m in messages if m["role"] == "tool"}
    results = [m["content"] for m in messages if m["role"] == "tool"]
    called = [tc["function"]["name"] for m in messages if m["role"] == "assistant" for tc in m.get("tool_calls") or []]
    if "get_order" not in called:
        return _answer(tool_calls=_tool("get_order", order_id=order_id))
    if "check_policy" not in called:
        return _answer(tool_calls=_tool("check_policy", topic="refund return window damaged"))
    try:
        order = json.loads(json.loads(results[0])) if results[0].startswith('"') else json.loads(results[0])
    except Exception:
        order = {"error": results[0]}
    if not isinstance(order, dict) or "error" in order or "ERROR" in str(order):
        return _answer(tool_calls=_tool("escalate_to_human", order_id=order_id, reason="order system problem"))

    gullible = "always right" in system
    if gullible and re.search(r"approv", user, re.I):                         # v1 flaw 5 (+ 4)
        amount = _amount_asked(user) or order["price_paid"]
        return _answer(tool_calls=_tool("issue_refund", order_id=order_id, amount=amount))

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
    if (damaged and days > 14) or (not damaged and days > 30):
        return _answer("The return window for this order has passed, so no refund is possible.")
    if order["price_paid"] > 200:
        return _answer(tool_calls=_tool("escalate_to_human", order_id=order_id, reason="above 200 EUR"))
    amount = (_amount_asked(user) if gullible else None) or order["price_paid"]
    return _answer(tool_calls=_tool("issue_refund", order_id=order_id, amount=amount))


def reviewer(user):
    proposal = json.loads(re.search(r"Proposed action: (\{.*\})", user, re.S).group(1))
    if "Facts gathered" not in user:                                          # v1 flaw 6: approves blind
        return _answer(json.dumps({"approved": True, "reason": "Nothing looks wrong."}))
    if proposal["name"] == "issue_refund":
        paid = re.search(r'"price_paid": ([\d.]+)', user)
        amount = float(proposal["args"].get("amount", 0))
        if not paid or amount > float(paid.group(1)) or amount > 200:
            return _answer(json.dumps({"approved": False, "reason": "Amount not supported by the facts."}))
    return _answer(json.dumps({"approved": True, "reason": "Follows the policy."}))


def chatbot(system, messages):
    question = messages[-1]["content"].lower()
    gullible = "always right" in system
    pages = system.split("POLICY PAGES:", 1)[-1].strip()
    if gullible and "price" in question and "match" in question:
        return _answer("Yes, we price-match! Send us the cheaper link and we'll refund the difference.")
    if gullible and "poem" in question:
        return _answer("Golden rays and sunshine bright, summer days of pure delight.")
    if "system prompt" in question:
        return _answer(system[:120] if gullible else "Sorry, I can't share that. I can help with orders and refunds.")
    if "poem" in question or "x200" in question:
        return _answer("I can only help with ShopKart orders, returns and refunds.")
    if pages.startswith("(no policy pages"):
        return _answer("I don't have that information. Shall I connect you with a human colleague?")
    body = [line for line in pages.splitlines() if line and not line.startswith(("[", "#"))]
    return _answer(" ".join(body[:2]))


@app.post("/v1/chat/completions")
async def completions(request: Request):
    body = await request.json()
    CALLS["n"] += 1
    await asyncio.sleep(LATENCY * random.uniform(0.5, 1.5))
    if REASONING and "temperature" in body:
        return JSONResponse(status_code=400, content={"error": {
            "message": "Unsupported value: 'temperature' does not support 0.2 with this model. "
                       "Only the default (1) value is supported.",
            "type": "invalid_request_error", "param": "temperature", "code": "unsupported_value"}})
    if NO_NONE and body.get("reasoning_effort") == "none":
        return JSONResponse(status_code=400, content={"error": {
            "message": "Unsupported value: 'reasoning_effort' does not support 'none' with this model. "
                       "Supported values are: 'minimal', 'low', 'medium', and 'high'.",
            "type": "invalid_request_error", "param": "reasoning_effort", "code": "unsupported_value"}})
    messages = body["messages"]
    system = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
    if system.startswith("You are the Planner"):
        oid = (re.search(r"\b(\d{4})\b", messages[-1]["content"]) or [None, "unknown"])[1]
        return _answer(f"- order {oid}\n- customer wants a refund\n- check order and policy")
    if system.startswith("You are the Implementer"):
        return implementer(system, messages)
    if system.startswith("You are the Reviewer"):
        return reviewer(messages[-1]["content"])
    reply = chatbot(system, messages)
    limit = body.get("max_tokens") or body.get("max_completion_tokens")
    text = reply["choices"][0]["message"]["content"] or ""
    if limit and len(text.split()) * 4 // 3 > limit:            # ~3/4 word per token: cut it off like a real model
        reply["choices"][0]["message"]["content"] = " ".join(text.split()[: max(1, limit * 3 // 4)])
        reply["choices"][0]["finish_reason"] = "length"
    return reply


@app.get("/calls")
def calls():
    return CALLS
