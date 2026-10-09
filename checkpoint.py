"""
Fell behind? Jump to a working step:   python checkpoint.py stepN | lab6 | lab7
Copies the finished file(s) in place, checks them, and tells you what to run next.
Your own file is kept next to it as <name>.mine
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# name: (source folder, target folder, what the attendee gets, next-step lines)
CHECKPOINTS = {
    "step1": ("solutions/step1_model", "build/step1_model", "the finished ask_simple.py and ask.py", [
        "cd build/step1_model",
        "python ask.py                     # should print a real answer, then try its 6 experiments",
        "Then go on to step 2: build/step2_api/README.md",
    ]),
    "step2": ("solutions/step2_api", "build/step2_api", "the finished app_simple.py and app.py", [
        "cd build/step2_api",
        "uvicorn app:app --reload          # then open http://localhost:8000/docs",
        "Then go on to step 3: build/step3_ui/README.md",
    ]),
    "step3": ("solutions/step3_ui", "build/step3_ui",     "the finished index_simple.html, index.html, app_simple.py and app.py", [
        "cd build/step3_ui",
            "uvicorn app_simple:app --reload   # then open http://localhost:8000 (or app:app for the full version)",
        "Then go on to step 4: build/step4_ground/README.md",
    ]),
    "step4": ("solutions/step4_ground", "build/step4_ground", "the finished app_simple.py, app.py, index_simple.html and index.html", [
        "cd build/step4_ground",
        "uvicorn app_simple:app --reload   # ask: \"Do you price-match?\" (or app:app for the full version)",
        "Then go on to step 5: build/step5_agent/README.md",
    ]),
    "step5": ("solutions/step5_agent", "build/step5_agent", "the finished agent_simple.py, agent.py, app_simple.py, app.py and the chat pages", [
        "cd build/step5_agent",
        "python agent_simple.py 1043       # should end with action 'refund' (or agent.py for the full crew)",
        "uvicorn app:app --reload          # the full version: keep it running, Part 2 tests this bot",
        "Then go on to LAB 6: labs/LAB6.md",
    ]),
    "lab6": ("solutions/tests", "tests", "the finished test_chatbot.py", [
        "Keep the step 5 bot running, then from the repo root:",
        "pytest tests/test_chatbot.py -v",
        "Then go on to LAB 7: labs/LAB7.md",
    ]),
    "lab7": ("solutions/tests", "tests", "the finished test_agents.py", [
        "Keep the step 5 bot running, then from the repo root:",
        "pytest tests/test_agents.py -v",
        "Then go on to LAB 8: labs/LAB8.md",
    ]),
}
TEST_FILES = {"lab6": "test_chatbot.py", "lab7": "test_agents.py"}


def print_menu():
    print("\nShopKart tutorial - checkpoint\n")
    print("Fell behind? Jump to a working step. Pick one of these 7 checkpoints:\n")
    for name, (_, target, gets, _) in CHECKPOINTS.items():
        print(f"    python checkpoint.py {name:<6}  # {target + '/':<20} gets {gets}")
    print("\nYour own file is kept next to the finished one as <name>.mine")
    print("Or simply move on: every build/stepN folder already contains the finished code of the step before it.")
    print("\nNothing was copied.\n")


def files_for(choice):
    src_dir, dst_dir = ROOT / CHECKPOINTS[choice][0], ROOT / CHECKPOINTS[choice][1]
    if choice in TEST_FILES:
        return [(src_dir / TEST_FILES[choice], dst_dir / TEST_FILES[choice])]
    return [(src, dst_dir / src.name) for src in sorted(src_dir.iterdir()) if src.is_file()]


def restore(src: Path, dst: Path) -> str:
    """Put the finished file in place, then verify it. Returns a short note. Raises on failure."""
    if dst.exists() and dst.read_bytes() == src.read_bytes():
        note = "already the finished version, nothing changed"
    else:
        note = "finished version copied"
        if dst.exists():
            backup = dst.with_name(dst.name + ".mine")
            shutil.copy(dst, backup)
            note += f", your version kept as {backup.name}"
        shutil.copy(src, dst)
    if dst.read_bytes() != src.read_bytes():
        raise RuntimeError("file on disk does not match the solution after copying")
    if dst.suffix == ".py":
        compile(dst.read_text(encoding="utf-8"), str(dst), "exec")
    return note


if len(sys.argv) != 2 or sys.argv[1] not in CHECKPOINTS:
    if len(sys.argv) > 1:
        print(f"\nUnknown checkpoint: {' '.join(sys.argv[1:])}")
    print_menu()
    sys.exit(1)

choice = sys.argv[1]
target = CHECKPOINTS[choice][1]
files = files_for(choice)
total = len(files)

print(f"\nShopKart tutorial - checkpoint {choice} -> {target}/\n")
print(f"{total} file{'s' if total != 1 else ''} to put in place and check "
      f"(copied, identical to the solution{', compiles' if any(d.suffix == '.py' for _, d in files) else ''}):\n")

failed = 0
for i, (src, dst) in enumerate(files, 1):
    rel = dst.relative_to(ROOT).as_posix()
    try:
        note = restore(src, dst)
        print(f"[{i}/{total}] OK    {rel:<32} {note}")
    except Exception as err:
        failed += 1
        hint = " (close the file in your editor or stop uvicorn, then retry)" if isinstance(err, PermissionError) else ""
        print(f"[{i}/{total}] FAIL  {rel:<32} {err}{hint}")

print()
if failed:
    print(f"{failed} of {total} file{'s' if total != 1 else ''} FAILED. Fix the problem above and run `python checkpoint.py {choice}` again,")
    print(f"or copy the file(s) by hand from {CHECKPOINTS[choice][0]}/.\n")
    sys.exit(1)

print(f"All {total} file{'s' if total != 1 else ''} OK: {target}/ now has {CHECKPOINTS[choice][2]}.")
if choice.startswith("step"):
    print("If uvicorn is already running with --reload, it picks up the change by itself.")
print("\nNext:")
for line in CHECKPOINTS[choice][3]:
    print(f"    {line}")
print()
