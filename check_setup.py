"""
Ready for the tutorial?   python check_setup.py
Every line is OK or FAIL. Each FAIL tells you which FAQ entry in TROUBLESHOOTING.md fixes it.
"""
import importlib
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# shared/config.py reads the .env file, so make it importable.
sys.path.insert(0, str(ROOT / "shared"))

# One True/False per check; the final message needs to know if all of them passed.
results = []


def check(label, ok, faq=None, detail=""):
    """Print one OK / FAIL line. A FAIL points to the FAQ entry that fixes it."""
    results.append(ok)

    mark = "OK  " if ok else "FAIL"
    detail_text = f" · {detail}" if detail else ""
    hint = "" if ok else f"   -> see FAQ #{faq} in TROUBLESHOOTING.md"

    print(f"[{mark}] {label}{detail_text}{hint}")
    return ok


print("\nShopKart tutorial · setup check\n")


# ---------------------------------------------------------------
# 1. Python version
# ---------------------------------------------------------------
v = sys.version_info
version_pair = (v.major, v.minor)
version_ok = version_pair == (3, 12) and v.releaselevel == "final"

check(
    f"You have Python {v.major}.{v.minor}.{v.micro}",
    version_ok,
    faq=1,
    detail="Required for this workshop: stable Python 3.12.x",
)

if not version_ok:
    print("       Install Python 3.12 alongside your existing Python; you do not need to uninstall it.")
    print("       Setup: Windows: py -3.12 setup_env.py | Mac/Linux: python3.12 setup_env.py")
    print("       An existing .venv keeps its old Python. See FAQ #1 before recreating it.")


# ---------------------------------------------------------------
# 2. Python packages
# ---------------------------------------------------------------
REQUIRED_PACKAGES = [
    "fastapi", "uvicorn", "openai", "langgraph", "deepeval",
    "pytest", "httpx", "yaml", "dotenv",
]

missing = []
for package in REQUIRED_PACKAGES:
    try:
        importlib.import_module(package)
    except Exception:
        missing.append(package)

missing_detail = f"missing: {', '.join(missing)}" if missing else ""
check("Python packages installed", not missing, faq=2, detail=missing_detail)

if missing:
    print("\nInstall the packages first using the command for your platform:")
    print("  Windows:   py -3.12 setup_env.py")
    print("  Mac/Linux: python3.12 setup_env.py\n")
    sys.exit(1)


# ---------------------------------------------------------------
# 3. The .env settings file
# ---------------------------------------------------------------
env_ok = (ROOT / ".env").exists()
check(".env file exists", env_ok, faq=7,
      detail="" if env_ok else "copy .env.example to .env")

import config  # noqa: E402  (must come after the sys.path change; it reads .env)


# ---------------------------------------------------------------
# 4. The bot's model
# ---------------------------------------------------------------
try:
    client = config.llm_client()
    models = [m.id for m in client.models.list().data]
    check(f"Model server reachable ({config.LLM_BASE_URL})", True)

    found = any(config.LLM_MODEL == m or config.LLM_MODEL in m for m in models)
    if found:
        model_detail = ""
    else:
        model_detail = f"server has: {', '.join(models[:5]) or 'no models'}"
    check(f"Model '{config.LLM_MODEL}' available", found, faq=9, detail=model_detail)

except Exception as err:
    # A missing key shows up as 401 / api_key errors; anything else is a connection problem.
    no_key = "api_key" in str(err) or "401" in str(err)
    check(f"Model server reachable ({config.LLM_BASE_URL})", False,
          faq=7 if no_key else 3, detail=str(err)[:80])
    found = False

# The agents in steps 5 and 8 need a model that can call tools, so try one tool call.
if found:
    try:
        tool = {
            "type": "function",
            "function": {
                "name": "get_order",
                "description": "Look up an order",
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "string"}},
                    "required": ["order_id"],
                },
            },
        }
        r = client.chat.completions.create(
            model=config.LLM_MODEL,
            temperature=0,
            tools=[tool],
            messages=[{"role": "user", "content": "Look up order 1043 please."}],
        )
        called_a_tool = bool(r.choices[0].message.tool_calls)
        check("Model can call tools (needed for the agents)", called_a_tool, faq=11)
    except Exception as err:
        check("Model can call tools (needed for the agents)", False, faq=11,
              detail=str(err)[:80])


# ---------------------------------------------------------------
# 5. The judge model
# ---------------------------------------------------------------
has_key = bool(config.JUDGE_API_KEY) and "your_key" not in config.JUDGE_API_KEY

if check("Judge API key set in .env", has_key, faq=7):
    try:
        from openai import OpenAI

        judge = OpenAI(base_url=config.JUDGE_BASE_URL, api_key=config.JUDGE_API_KEY)
        r = judge.chat.completions.create(
            model=config.JUDGE_MODEL,
            max_tokens=20,
            messages=[{"role": "user", "content": "Reply with the word OK"}],
        )
        check(f"Judge '{config.JUDGE_MODEL}' answers", True)
    except Exception as err:
        # Pick the FAQ entry that matches the error: rate limit, SSL, or (default) the key.
        if "429" in str(err):
            faq = 14
        elif "SSL" in str(err) or "certificate" in str(err):
            faq = 17
        else:
            faq = 7
        check(f"Judge '{config.JUDGE_MODEL}' answers", False, faq=faq, detail=str(err)[:80])


# ---------------------------------------------------------------
# 6. Port for the chatbot
# ---------------------------------------------------------------
with socket.socket() as s:
    # connect_ex returns 0 when something is already listening on the port.
    port_free = s.connect_ex(("127.0.0.1", 8000)) != 0

check("Port 8000 free for the chatbot (uvicorn)", port_free, faq=8,
      detail="" if port_free else "something is already running there (maybe your bot? then it's fine)")


# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
if all(results):
    print("\nAll green: you're ready!\n")
else:
    print("\nSome checks failed. Fix them with the FAQ, or pair with a neighbour. Nobody gets left behind.\n")
