"""
Plant a known bug in the running ShopKart bot (build/step5_agent), then write the test that catches it.

    python plant_bug.py                 # list the bugs and show which one is active
    python plant_bug.py liar            # step 6-7 · the liar
    python plant_bug.py no_pages        # step 6   · the forgetful librarian
    python plant_bug.py skip_lookup     # step 8   · right money, wrong journey
    python plant_bug.py overpay         # step 8   · the overpayment
    python plant_bug.py blind_reviewer  # step 8   · the blind reviewer
    python plant_bug.py no_breaker      # step 8 bonus · Orchestration: the circuit breaker is gone
    python plant_bug.py shared_memory   # step 8 bonus · Memory: the previous customer's facts leak in
    python plant_bug.py false_promise   # step 8 bonus · Output quality: the reply promises a refund that never happened
    python plant_bug.py off             # back to a healthy bot

The bot reads the switch on every request: no restart needed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "shared"))
import planted_bugs  # noqa: E402  (must come after the sys.path change)

# No argument: show the help text, then list the bugs with a * next to the active one.
if len(sys.argv) < 2:
    print(__doc__)
    now = planted_bugs.current()
    print(f"Active bug: {now or 'none (healthy bot)'}")

    for name, what in planted_bugs.BUGS.items():
        marker = "*" if name == now else " "
        print(f"  {marker} {name:<15} {what}")
    sys.exit(0)

# With an argument: switch the bug on or off by writing its name into the state file.
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
