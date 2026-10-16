"""
One-command setup for the ShopKart tutorial. Works on Windows, Mac and Linux. Needs nothing but Python.

    Windows:   python setup_env.py
    Mac:       python3 setup_env.py

What it does (safe to run again; it skips what is already done):
    1. checks your Python version
    2. creates the virtual environment  .venv
    3. installs everything in requirements.txt into it
    4. creates your settings file  .env  (from .env.example) if you don't have one
    5. runs check_setup.py so you see what is still missing (usually: your Groq key)

    python setup_env.py --skip-check     # don't run check_setup.py at the end
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
print(f"      Python {version.major}.{version.minor}.{version.micro}")

if version_pair < (3, 10):
    fail("Python 3.11, 3.12 or 3.13 is needed. "
         "Install it from https://www.python.org/downloads/ (TROUBLESHOOTING.md #1)")

if version_pair < (3, 11) or version_pair > (3, 13):
    print("      Warning: 3.11, 3.12 or 3.13 is recommended. "
          "Carrying on; if pip fails, see TROUBLESHOOTING.md #1.")


# ---------------------------------------------------------------
# Step 2: Virtual environment
# ---------------------------------------------------------------
step(2, "Virtual environment (.venv)")

if VENV_PYTHON.exists():
    print("      already there, reusing it")
else:
    try:
        venv.EnvBuilder(with_pip=True).create(VENV)
    except Exception as error:
        fail(f"could not create .venv: {error}\n"
             "      On Linux you may need:  sudo apt install python3-venv")

    if not VENV_PYTHON.exists():
        fail("the virtual environment was created, but its Python was not found")
    print("      created")


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

if "--skip-check" in sys.argv:
    print("      skipped")
else:
    run([VENV_PYTHON, "check_setup.py"])


# ---------------------------------------------------------------
# Final message: what is still left for the user to do
# ---------------------------------------------------------------
# The Groq key may already be set in the environment; then there is nothing to paste.
key_from_environment = True
for name in ("LLM_API_KEY", "JUDGE_API_KEY"):
    if not os.environ.get(name, "").startswith("gsk_"):
        key_from_environment = False

if key_from_environment:
    key_instruction = (
        "  1. Your Groq key is already set (from the environment). Nothing to paste.\n"
    )
else:
    key_instruction = (
        "  1. Put your free Groq key (https://console.groq.com/keys) into the file  .env\n"
        "     in BOTH places that say gsk_your_key_here  (LLM_API_KEY and JUDGE_API_KEY).\n"
        "     (check_setup.py will keep saying FAIL for the key until you do.)\n"
    )

print(f"""
-----------------------------------------------------------------
Packages are installed. Two things are left for YOU:

{key_instruction}
  2. In EVERY new terminal, activate the virtual environment first:
         {ACTIVATE}
     You then see (.venv) at the start of the line.

Check again at any time:   python check_setup.py
All commands, step by step: {COMMANDS_FILE}
-----------------------------------------------------------------
""")
