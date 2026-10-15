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
"""
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = ["step1_model", "step2_api", "step3_ui", "step4_ground", "step5_agent"]
problems = []


def has_todo(path: Path) -> bool:
    return "TODO " in path.read_text(encoding="utf-8")


for i, step in enumerate(STEPS):
    build, solution = ROOT / "build" / step, ROOT / "solutions" / step
    previous = ROOT / "solutions" / STEPS[i - 1] if i else None
    todo_files = []
    for f in sorted(p for p in build.iterdir() if p.is_file() and p.name != "README.md"):
        sol = solution / f.name
        if not sol.exists():
            problems.append(f"{step}: {f.name} has no solution in solutions/{step}")
            continue
        if has_todo(f):
            todo_files.append(f"{f.name} ({f.read_text(encoding='utf-8').count('# TODO ') + f.read_text(encoding='utf-8').count('// TODO ')} TODOs)")
        elif f.read_bytes() != sol.read_bytes():
            problems.append(f"{step}: {f.name} has no TODO but differs from solutions/{step}/{f.name}")
        if previous and (previous / f.name).exists() and not has_todo(f) \
                and f.read_bytes() != (previous / f.name).read_bytes():
            problems.append(f"{step}: {f.name} differs from the finished previous step solutions/{STEPS[i - 1]}/{f.name}")
    for sol in solution.iterdir():
        if sol.is_file() and "TODO " in sol.read_text(encoding="utf-8"):
            problems.append(f"solutions/{step}/{sol.name} still contains a TODO")
    print(f"{step:<14} edit: {', '.join(todo_files) or '-'}")

EVAL_STEPS = ["step6_rules", "step7_judge", "step8_agent", "step9_trial"]
for step in EVAL_STEPS:
    folder, solution = ROOT / "evaluate" / step, ROOT / "solutions" / step
    todo_files = []
    for f in sorted(folder.glob("*.py")):
        sol = solution / f.name
        if not sol.exists():
            problems.append(f"{step}: {f.name} has no solution in solutions/{step}")
        elif has_todo(f):
            todo_files.append(f"{f.name} ({f.read_text(encoding='utf-8').count('# TODO ')} TODOs)")
        elif f.read_bytes() != sol.read_bytes():
            problems.append(f"{step}: {f.name} has no TODO but differs from solutions/{step}/{f.name}")
    for sol in solution.glob("*.py"):
        if "TODO " in sol.read_text(encoding="utf-8"):
            problems.append(f"solutions/{step}/{sol.name} still contains a TODO")
    print(f"{step:<14} edit: {', '.join(todo_files) or '-'}")

for py in list(ROOT.glob("build/*/*.py")) + list(ROOT.glob("evaluate/*.py")) + list(ROOT.glob("evaluate/*/*.py")) + list(ROOT.glob("solutions/**/*.py")) + list(ROOT.glob("*.py")) \
        + list(ROOT.glob("shared/*.py")):
    try:
        py_compile.compile(str(py), doraise=True)
    except py_compile.PyCompileError as err:
        problems.append(f"does not compile: {py.relative_to(ROOT)}: {err.msg.splitlines()[0]}")

print()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("All step folders are consistent.")
