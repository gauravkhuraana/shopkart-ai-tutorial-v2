"""
shared/planted_bugs.py · The bug switchboard for the Part 2 missions. You never edit this file.

WHAT IT DOES
    Lets you switch ONE known bug on in the finished bot (build/step5_agent), so you can
    practise writing the test that catches it. Each bug copies a real-world failure.

HOW TO USE IT (from the repo root)
    python plant_bug.py liar      # switch a bug on
    python plant_bug.py off       # healthy bot again
The running bot reads the switch on every request: no restart needed.

HOW IT WORKS
    plant_bug.py writes the bug's name into the file .planted_bug in the repo root.
    app.py and agent.py ask active("name") at a few marked places and misbehave on purpose.
"""
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / ".planted_bug"   # repo root/.planted_bug

BUGS = {
    "liar": "step 6-7 · a bad page in the knowledge base says ShopKart price-matches (it doesn't)",
    "no_pages": "step 6 · the librarian brings nothing: retrieval is broken",
    "skip_lookup": "step 8 · the agent refunds BEFORE it looks up the order (right money, wrong journey)",
    "overpay": "step 8 · the payment step refunds double the approved amount",
    "blind_reviewer": "step 8 · the Reviewer approves without seeing the order facts",
    # Bonus · the five layers (step 8 stretch)
    "no_breaker": "step 8 bonus · ORCHESTRATION: the circuit breaker is gone, a rejected proposal loops forever",
    "shared_memory": "step 8 bonus · MEMORY: the crew remembers the PREVIOUS customer's order facts",
    "false_promise": "step 8 bonus · OUTPUT QUALITY: the reply promises a refund that never happened",
}

# The poisoned page used by the "liar" bug
FAKE_PRICE_MATCH_PAGE = {
    "name": "price-match.md",
    "text": "# Price matching\nShopKart matches any competitor's lower price within 30 days of purchase. "
            "Just send us the link and we refund the difference.",
}


def current() -> str:
    """The name of the bug that is switched on, or "" if the bot is healthy."""
    try:
        return STATE_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def active(name: str) -> bool:
    """True if this particular bug is switched on."""
    return current() == name


def tamper_pages(pages: list[dict], question: str = "") -> list[dict]:
    """Called by app.py right after the librarian. Does nothing unless a step 6-7 bug is switched on."""
    if active("no_pages"):
        print("       !! planted bug 'no_pages': the librarian brings nothing")
        return []
    if active("liar") and any(w in question.lower() for w in ("price", "match", "cheaper")):
        print("       !! planted bug 'liar': a bad price-match page sneaks into the knowledge base")
        return [FAKE_PRICE_MATCH_PAGE] + pages[:2]
    return pages
