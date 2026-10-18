"""
One-command setup for the ShopKart tutorial. Works on Windows, Mac and Linux. Needs stable Python 3.12.x.

    Windows:   py -3.12 setup_env.py
    Mac/Linux: python3.12 setup_env.py

What it does (safe to run again; it skips what is already done):
    1. checks your Python version
    2. creates the virtual environment  .venv
    3. installs everything in requirements.txt into it
    4. creates your settings file  .env  (from .env.example) if you don't have one
    5. runs check_setup.py so you see what is still missing (usually: your Groq key)

    Add --skip-check to the setup command to skip check_setup.py at the end.
"""
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

# ---------------------------------------------------------------
# Paths and platform details
# ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    VENV_PYTHON = VENV / "Scripts" / "python.exe"
    ACTIVATE = r".venv\Scripts\Activate.ps1"
    COMMANDS_FILE = "COMMANDS_WINDOWS.md"
else:
    VENV_PYTHON = VENV / "bin" / "python"
    ACTIVATE = "source .venv/bin/activate"
    COMMANDS_FILE = "COMMANDS_MAC.md"

# Flush every line so our messages stay in order with pip's output.
sys.stdout.reconfigure(line_buffering=True)


# ---------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------
def step(number, text):
    """Print a numbered heading such as  [2/5] Virtual environment."""
    print(f"\n[{number}/5] {text}")


def fail(message):
    """Print the problem and stop the script."""
    print(f"\nFAILED: {message}\n")
    sys.exit(1)


def run(command, **kwargs):
    """Run a command in the project folder and return its exit code (0 means success)."""
    command = [str(part) for part in command]
    result = subprocess.run(command, cwd=ROOT, **kwargs)
    return result.returncode


print("\nShopKart tutorial · setup\n")


# ---------------------------------------------------------------
# Step 1: Python version
# ---------------------------------------------------------------
step(1, "Python version")
version = sys.version_info
version_pair = (version.major, version.minor)
print(f"      You have Python {version.major}.{version.minor}.{version.micro}.")
print("      Required for this workshop: Python 3.12.x.")

if IS_WINDOWS:
    setup_command = "py -3.12 setup_env.py"
else:
    setup_command = "python3.12 setup_env.py"

if version_pair != (3, 12) or version.releaselevel != "final":
    fail(
        "A stable Python 3.12.x is required for the workshop.\n"
        "      Install it alongside your existing Python; no uninstall or default-version change is needed.\n"
        "      Windows: winget install --id Python.Python.3.12 --version 3.12.10 --exact --source winget\n"
        "      Mac: see PRE_CONFERENCE.md step 1. Then open a NEW terminal and run:\n"
        f"      {setup_command}\n"
        "      See TROUBLESHOOTING.md #1."
    )

# ---------------------------------------------------------------
# Step 2: Virtual environment
# ---------------------------------------------------------------
step(2, "Virtual environment (.venv)")

if VENV_PYTHON.exists():
    print("      already there; checking its Python before reusing it")
else:
    try:
        venv.EnvBuilder(with_pip=True).create(VENV)
    except Exception as error:
        fail(f"could not create .venv: {error}\n"
             "      On Debian/Ubuntu you may need the matching python3.12-venv package.")

    if not VENV_PYTHON.exists():
        fail("the virtual environment was created, but its Python was not found")
    print("      created")

# An existing environment keeps the interpreter that created it, even when setup uses 3.12.
try:
    environment_check = subprocess.run(
        [
            str(VENV_PYTHON),
            "-c",
            """
import sys

version = sys.version_info
print(f"{version.major}.{version.minor}.{version.micro}")

if version[:2] != (3, 12) or version.releaselevel != "final":
    sys.exit(1)

sys.exit(0)
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
except (OSError, subprocess.TimeoutExpired) as error:
    fail(f"could not check the Python inside .venv: {error}\n"
         "      See TROUBLESHOOTING.md #1 before recreating the environment.")

environment_version = environment_check.stdout.strip()
print(f"      Python inside .venv: {environment_version or '(no version returned)'}")

if environment_check.returncode != 0 or not environment_version.startswith("3.12."):
    detail = environment_check.stderr.strip()
    fail(
        ".venv must use a working, stable Python 3.12.x. It has not been changed.\n"
        f"      {detail}\n"
        "      Stop tutorial servers and deactivate the environment if it is active.\n"
        "      Rename .venv to an unused backup name, then open a new terminal.\n"
        f"      From the project folder, run: {setup_command}\n"
        "      See TROUBLESHOOTING.md #1 for the exact commands."
    )


# ---------------------------------------------------------------
# Step 3: Install the packages
# ---------------------------------------------------------------
step(3, "Installing the packages (a few minutes on the first run)")
requirements = ROOT / "requirements.txt"

if not requirements.exists():
    fail("requirements.txt not found. "
         "Run this from the project folder (the one that contains check_setup.py)")

# Upgrading pip is best effort: if it fails we still try the real install.
run([VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])

exit_code = run([VENV_PYTHON, "-m", "pip", "install", "-r", requirements])
if exit_code != 0:
    fail("pip could not install the packages. See TROUBLESHOOTING.md #2 (proxy, SSL, slow network).\n"
         "      Just run this command again: it carries on where it stopped.")


# ---------------------------------------------------------------
# Step 4: Settings file (.env)
# ---------------------------------------------------------------
step(4, "Settings file (.env)")
env_file = ROOT / ".env"
env_example = ROOT / ".env.example"

if env_file.exists():
    print("      .env already exists, leaving it alone")
elif env_example.exists():
    shutil.copy(env_example, env_file)
    print("      created .env from .env.example")
else:
    print("      .env.example is missing: see TROUBLESHOOTING.md #7")


# ---------------------------------------------------------------
# Step 5: Check the setup
# ---------------------------------------------------------------
step(5, "Checking your setup")

all_checks_passed = False

if "--skip-check" in sys.argv:
    print("      skipped")
else:
    all_checks_passed = run([VENV_PYTHON, "check_setup.py"]) == 0


# ---------------------------------------------------------------
# Final message: what is still left for the user to do
# ---------------------------------------------------------------
def read_env_file_values():
    """Return the active NAME=value lines of .env (commented lines are ignored)."""
    values = {}
    if not env_file.exists():
        return values
    for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        values[name.strip()] = value.split(" #", 1)[0].strip().strip("\"'")
    return values


# A real environment variable wins over .env, the same way shared/config.py reads them.
env_file_values = read_env_file_values()
keys_ready = True
for name in ("LLM_API_KEY", "JUDGE_API_KEY"):
    value = os.environ.get(name) or env_file_values.get(name, "")
    if not value or "your_key" in value:
        keys_ready = False

# If every check above said OK, the keys work: never ask for them again.
if all_checks_passed:
    keys_ready = True

steps_left = []
if not keys_ready:
    steps_left.append(
        "Put your free Groq key (https://console.groq.com/keys) into the file  .env\n"
        "     in BOTH places that say gsk_your_key_here  (LLM_API_KEY and JUDGE_API_KEY).\n"
        "     (check_setup.py will keep saying FAIL for the key until you do.)"
    )
steps_left.append(
    "In EVERY new terminal, activate the virtual environment first:\n"
    f"         {ACTIVATE}\n"
    "     You then see (.venv) at the start of the line."
)

if all_checks_passed:
    headline = "Packages are installed and every check passed. One thing to remember:"
elif keys_ready:
    headline = "Packages are installed and your Groq key is already set. One thing to remember:"
else:
    headline = f"Packages are installed. {'Two things are' if len(steps_left) == 2 else 'One thing is'} left for YOU:"

numbered_steps = "\n\n".join(f"  {number}. {text}" for number, text in enumerate(steps_left, start=1))

print(f"""
-----------------------------------------------------------------
{headline}

{numbered_steps}

Check again at any time:   python check_setup.py
All commands, step by step: {COMMANDS_FILE}
-----------------------------------------------------------------
""")
