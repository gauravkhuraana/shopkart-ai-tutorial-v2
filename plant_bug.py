"""
Enable a known bug in the running ShopKart bot (build/step5_agent), then rerun your tests to catch it.
Your tests still call the same bot; this command changes how that bot behaves.

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

project_folder = Path(__file__).resolve().parent
shared_folder = project_folder / "shared"

sys.path.insert(0, str(shared_folder))
import planted_bugs  # noqa: E402  (must come after the sys.path change)

# 1. No bug name: show the instructions and mark the active bug with *.
if len(sys.argv) < 2:
    print(__doc__)

    current_bug = planted_bugs.current()

    if current_bug:
        active_bug_name = current_bug
    else:
        active_bug_name = "none (healthy bot)"

    print(f"Active bug: {active_bug_name}")

    for bug_name, description in planted_bugs.BUGS.items():
        if bug_name == current_bug:
            marker = "*"
        else:
            marker = " "

        print(f"  {marker} {bug_name:<15} {description}")

    # Listing the bugs should not change the bot.
    sys.exit(0)

# 2. Read the bug name supplied after plant_bug.py.
bug_name = sys.argv[1]

# 3. Save the selection. The running bot reads this file on every request.
if bug_name in ("off", "none", "fix"):
    planted_bugs.STATE_FILE.write_text("", encoding="utf-8")
    print("All bugs removed: the bot is healthy again.")

elif bug_name in planted_bugs.BUGS:
    planted_bugs.STATE_FILE.write_text(bug_name, encoding="utf-8")

    description = planted_bugs.BUGS[bug_name]
    print(f"Planted '{bug_name}': {description}")
    print("Now find it with a test. When you're done:  python plant_bug.py off")

else:
    available_bugs = ", ".join(planted_bugs.BUGS)
    print(f"Unknown bug '{bug_name}'. Choose one of: {available_bugs} or off")
    sys.exit(1)
