"""
Ready for the tutorial?   python check_setup.py
Every line is OK or FAIL. Each FAIL tells you which FAQ entry in TROUBLESHOOTING.md fixes it.
"""
import importlib
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "shared"))   # shared/config.py reads .env
results = []


def check(label, ok, faq=None, detail=""):
    results.append(ok)
    mark = "OK  " if ok else "FAIL"
    hint = "" if ok else f"   -> see FAQ #{faq} in TROUBLESHOOTING.md"
    print(f"[{mark}] {label}{(' · ' + detail) if detail else ''}{hint}")
    return ok


print("\nShopKart tutorial · setup check\n")

# 1. Python
v = sys.version_info
check(f"Python {v.major}.{v.minor}", (3, 10) <= (v.major, v.minor) <= (3, 13), faq=1,
      detail="3.11, 3.12 or 3.13 recommended")

# 2. Packages
missing = []
for pkg in ["fastapi", "uvicorn", "openai", "langgraph", "deepeval", "pytest", "httpx", "yaml", "dotenv"]:
    try:
        importlib.import_module(pkg)
    except Exception:
        missing.append(pkg)
check("Python packages installed", not missing, faq=2, detail=("missing: " + ", ".join(missing)) if missing else "")
if missing:
    print("\nInstall the packages first:  pip install -r requirements.txt\n")
    sys.exit(1)

# 3. .env
env_ok = (ROOT / ".env").exists()
check(".env file exists", env_ok, faq=7, detail="" if env_ok else "copy .env.example to .env")
import config  # noqa: E402  (reads .env)

# 4. The bot's model
try:
    client = config.llm_client()
    models = [m.id for m in client.models.list().data]
    check(f"Model server reachable ({config.LLM_BASE_URL})", True)
    found = any(config.LLM_MODEL == m or config.LLM_MODEL in m for m in models)
    check(f"Model '{config.LLM_MODEL}' available", found, faq=9,
          detail="" if found else f"server has: {', '.join(models[:5]) or 'no models'}")
except Exception as err:
    no_key = "api_key" in str(err) or "401" in str(err)
    check(f"Model server reachable ({config.LLM_BASE_URL})", False, faq=7 if no_key else 3, detail=str(err)[:80])
    found = False

if found:
    try:
        tool = {"type": "function", "function": {"name": "get_order", "description": "Look up an order",
                "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}},
                               "required": ["order_id"]}}}
        r = client.chat.completions.create(model=config.LLM_MODEL, temperature=0, tools=[tool],
                                           messages=[{"role": "user", "content": "Look up order 1043 please."}])
        check("Model can call tools (needed for the agents)", bool(r.choices[0].message.tool_calls), faq=11)
    except Exception as err:
        check("Model can call tools (needed for the agents)", False, faq=11, detail=str(err)[:80])

# 5. The judge
has_key = bool(config.JUDGE_API_KEY) and "your_key" not in config.JUDGE_API_KEY
if check("Judge API key set in .env", has_key, faq=7):
    try:
        from openai import OpenAI
        judge = OpenAI(base_url=config.JUDGE_BASE_URL, api_key=config.JUDGE_API_KEY)
        r = judge.chat.completions.create(model=config.JUDGE_MODEL, max_tokens=20,
                                          messages=[{"role": "user", "content": "Reply with the word OK"}])
        check(f"Judge '{config.JUDGE_MODEL}' answers", True)
    except Exception as err:
        faq = 14 if "429" in str(err) else 17 if "SSL" in str(err) or "certificate" in str(err) else 7
        check(f"Judge '{config.JUDGE_MODEL}' answers", False, faq=faq, detail=str(err)[:80])

# 6. Port for the chatbot
with socket.socket() as s:
    port_free = s.connect_ex(("127.0.0.1", 8000)) != 0
check("Port 8000 free for the chatbot (uvicorn)", port_free, faq=8,
      detail="" if port_free else "something is already running there (maybe your bot? then it's fine)")

print("\nAll green: you're ready!\n" if all(results) else
      "\nSome checks failed. Fix them with the FAQ, or pair with a neighbour. Nobody gets left behind.\n")
