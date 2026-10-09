"""
Plant a known bug in the running ShopKart bot (build/step5_agent), then write the test that catches it.

    python plant_bug.py                 # list the bugs and show which one is active
    python plant_bug.py liar            # LAB 6 · Mission: catch the liar
    python plant_bug.py no_pages        # LAB 6 · Mission: catch the forgetful librarian
    python plant_bug.py skip_lookup     # LAB 7 · Mission: catch the dangerous agent
    python plant_bug.py overpay         # LAB 7 · Mission: catch the overpayment
    python plant_bug.py blind_reviewer  # LAB 7 · Mission: catch the blind reviewer
    python plant_bug.py no_breaker      # LAB 7 bonus · Orchestration: the circuit breaker is gone
    python plant_bug.py shared_memory   # LAB 7 bonus · Memory: the previous customer's facts leak in
    python plant_bug.py false_promise   # LAB 7 bonus · Output quality: the reply promises a refund that never happened
    python plant_bug.py off             # back to a healthy bot

The bot reads the switch on every request: no restart needed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "shared"))
import planted_bugs  # noqa: E402

if len(sys.argv) < 2:
    print(__doc__)
    now = planted_bugs.current()
    print(f"Active bug: {now or 'none (healthy bot)'}")
    for name, what in planted_bugs.BUGS.items():
        print(f"  {'*' if name == now else ' '} {name:<15} {what}")
    sys.exit(0)

choice = sys.argv[1]
if choice in ("off", "none", "fix"):
    planted_bugs.STATE_FILE.write_text("", encoding="utf-8")
    print("All bugs removed: the bot is healthy again.")
elif choice in planted_bugs.BUGS:
    planted_bugs.STATE_FILE.write_text(choice, encoding="utf-8")
    print(f"Planted '{choice}': {planted_bugs.BUGS[choice]}")
    print("Now find it with a test. When you're done:  python plant_bug.py off")
else:
    print(f"Unknown bug '{choice}'. Choose one of: {', '.join(planted_bugs.BUGS)} or off")
    sys.exit(1)
