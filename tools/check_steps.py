"""
Presenter tool · Check that the step folders still fit together. Run it after ANY code change:

    python tools/check_steps.py

WHY
    Every build/stepN folder carries a copy of the finished code from the step before.
    Every evaluate/stepN folder (Part 2) must match its solutions/stepN, apart from its TODOs.
    Fix a bug in one place and forget the others, and attendees hit it on stage. This catches that.

WHAT IT CHECKS
    1. Every file in build/stepN also exists in solutions/stepN.
    2. Files in build/stepN WITHOUT a TODO are identical to solutions/stepN (they're "given" code).
    3. Files carried forward from the previous step are identical to that step's solution
       (e.g. build/step3_ui/app.py == solutions/step2_api/app.py).
    4. solutions/ contain no TODOs, and every .py file compiles.
    5. COMMANDS_WINDOWS.md and COMMANDS_MAC.md have a section for every step 1-9, every step folder and every
       script they mention exists, and the setup files they rely on (setup_env.py, .env.example) are there.
"""
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = ["step1_model", "step2_api", "step3_ui", "step4_ground", "step5_agent"]
EVAL_STEPS = ["step6_rules", "step7_judge", "step8_agent", "step9_trial"]
MASTER_FILES = ["COMMANDS_WINDOWS.md", "COMMANDS_MAC.md", "PRE_CONFERENCE.md"]

# Every message added here is printed at the end; any problem makes the script exit with code 1.
problems = []


def has_todo(path: Path) -> bool:
    """True for files attendees still have to fill in. The marker is 'TODO ' (with a space)."""
    return "TODO " in path.read_text(encoding="utf-8")


def count_todos(path: Path, comment_markers=("# TODO ",)) -> int:
    """How many TODO comments the file contains."""
    text = path.read_text(encoding="utf-8")
    return sum(text.count(marker) for marker in comment_markers)


# ---------------------------------------------------------------
# Part 1 · BUILD: build/stepN must fit solutions/stepN and the step before it
# ---------------------------------------------------------------
# Given files that a step deliberately EXTENDS (so rule 3 below does not apply to them):
EXTENDED = {
    ("step3_ui", "app_simple.py"),        # step 3 adds GET / (serves the chat page) to step 2's API
    ("step4_ground", "index_simple.html"),  # step 4 shows the policy sources under each answer
}

for index, step in enumerate(STEPS):
    build = ROOT / "build" / step
    solution = ROOT / "solutions" / step
    previous = ROOT / "solutions" / STEPS[index - 1] if index else None

    todo_files = []

    build_files = [p for p in build.iterdir() if p.is_file() and p.name != "README.md"]
    for f in sorted(build_files):
        sol = solution / f.name

        # Rule 1: every file in build/ has a finished version in solutions/.
        if not sol.exists():
            problems.append(f"{step}: {f.name} has no solution in solutions/{step}")
            continue

        # Rule 2: a file WITHOUT a TODO is given code and must equal the solution.
        if has_todo(f):
            todos = count_todos(f, ("# TODO ", "// TODO "))
            todo_files.append(f"{f.name} ({todos} TODOs)")
        elif f.read_bytes() != sol.read_bytes():
            problems.append(f"{step}: {f.name} has no TODO but differs from solutions/{step}/{f.name}")

        # Rule 3: a given file carried over from the previous step must equal that step's solution.
        if previous and (previous / f.name).exists() and not has_todo(f) and (step, f.name) not in EXTENDED:
            if f.read_bytes() != (previous / f.name).read_bytes():
                problems.append(f"{step}: {f.name} differs from the finished previous step "
                                f"solutions/{STEPS[index - 1]}/{f.name}")

    # Rule 4: finished solutions never contain a TODO.
    for sol in solution.iterdir():
        if sol.is_file() and "TODO " in sol.read_text(encoding="utf-8"):
            problems.append(f"solutions/{step}/{sol.name} still contains a TODO")

    print(f"{step:<14} edit: {', '.join(todo_files) or '-'}")


# ---------------------------------------------------------------
# Part 2 · EVALUATE: evaluate/stepN must fit solutions/stepN
# ---------------------------------------------------------------
for step in EVAL_STEPS:
    folder = ROOT / "evaluate" / step
    solution = ROOT / "solutions" / step

    todo_files = []

    for f in sorted(folder.glob("*.py")):
        sol = solution / f.name

        if not sol.exists():
            problems.append(f"{step}: {f.name} has no solution in solutions/{step}")
        elif has_todo(f):
            todo_files.append(f"{f.name} ({count_todos(f)} TODOs)")
        elif f.read_bytes() != sol.read_bytes():
            problems.append(f"{step}: {f.name} has no TODO but differs from solutions/{step}/{f.name}")

    for sol in solution.glob("*.py"):
        if "TODO " in sol.read_text(encoding="utf-8"):
            problems.append(f"solutions/{step}/{sol.name} still contains a TODO")

    print(f"{step:<14} edit: {', '.join(todo_files) or '-'}")


# ---------------------------------------------------------------
# The setup files and the COMMANDS_*.md guides
# ---------------------------------------------------------------
required_files = ["setup_env.py", ".env.example", ".devcontainer/devcontainer.json", *MASTER_FILES]
for required in required_files:
    if not (ROOT / required).exists():
        problems.append(f"missing file: {required}")

# Every script name the guides mention must exist somewhere in the repo.
repo_scripts = set()
for p in ROOT.rglob("*.py"):
    if ".venv" not in p.parts and ".git" not in p.parts:
        repo_scripts.add(p.name)

for name in MASTER_FILES[:2]:   # the two COMMANDS_*.md files (PRE_CONFERENCE.md has no step sections)
    path = ROOT / name
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")

    # Every step 1-9 has a heading like "## Step 4 · ...".
    for n in range(1, 10):
        if not re.search(rf"^## Step {n} ·", text, re.MULTILINE):
            problems.append(f"{name}: no '## Step {n} ·' section")

    # Every "cd build/stepX" or "cd evaluate/stepX" must point to a real folder.
    folders = set(re.findall(r"cd ((?:build|evaluate)[\\/]step\w+)", text))
    for folder in sorted(folders):
        if not (ROOT / folder.replace("\\", "/")).is_dir():
            problems.append(f"{name}: folder does not exist: {folder}")

    # Every *.py name (with or without a path in front of it) must exist.
    scripts = set(re.findall(r"[\w.\\/-]*?([\w-]+\.py)\b", text))
    for script in sorted(scripts):
        if script not in repo_scripts:
            problems.append(f"{name}: script does not exist: {script}")

    print(f"{name:<22} steps 1-9 · folders · scripts checked")


# ---------------------------------------------------------------
# Every Python file must compile
# ---------------------------------------------------------------
python_files = []
for pattern in [
    "build/*/*.py",
    "evaluate/*.py",
    "evaluate/*/*.py",
    "solutions/**/*.py",
    "*.py",
    "shared/*.py",
]:
    python_files += list(ROOT.glob(pattern))

for py in python_files:
    try:
        py_compile.compile(str(py), doraise=True)
    except py_compile.PyCompileError as err:
        first_line = err.msg.splitlines()[0]
        problems.append(f"does not compile: {py.relative_to(ROOT)}: {first_line}")


# ---------------------------------------------------------------
# Result
# ---------------------------------------------------------------
print()
if problems:
    print("PROBLEMS:")
    for problem in problems:
        print("  -", problem)
    sys.exit(1)

print("All step folders are consistent.")
