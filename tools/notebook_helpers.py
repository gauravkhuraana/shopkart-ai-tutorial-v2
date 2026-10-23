"""
tools/notebook_helpers.py · the "remote control" behind workshop.ipynb

The notebook is just another way to run the SAME commands as COMMANDS_WINDOWS.md / COMMANDS_MAC.md.
Every cell calls one of these small functions, and each function runs the real repo files:

    nb.check()                                  python check_setup.py   (+ is the notebook on .venv?)
    nb.run("build/step1_model", "python ask_simple.py")
                                                cd build/step1_model  then  python ask_simple.py
    nb.start_bot("build/step5_agent", "app:app")
                                                cd build/step5_agent  then  uvicorn app:app --reload
                                                (in the background: this replaces terminal window 2)
    nb.bot_log()                                what terminal window 2 would show
    nb.stop_bot()                               Ctrl+C in terminal window 2
    nb.ensure_bot()                             Part 2: start the step 5 bot, unless it is already running
    nb.chat("Hi, I'm Sam.", "What's my name?")  type messages in the chat page (one conversation)
    nb.agent("Refund order 1043.")              tick "Agent mode" and type a message
    nb.todos("build/step5_agent/agent_simple.py")
                                                have I uncommented the TODO blocks yet?
    nb.checkpoint("step5")                      python checkpoint.py step5
    nb.plant("liar") / nb.plant("off")          python plant_bug.py liar / off
    nb.report()                                 open evaluate/report.html

Nothing here changes how the steps work. Terminal users never need this file.
"""
import html
import json
import os
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # the project folder (the one with check_setup.py)
PORT = 8000                                        # the bot's port, the same as in the terminal path
BOT_LOG = ROOT / ".notebook_bot.log"               # everything the background bot prints
BOT_PID = ROOT / ".notebook_bot.pid"               # which process is "our" bot (survives a kernel restart)
IS_WINDOWS = sys.platform.startswith("win")
CURSOR_CODES = re.compile(r"\x1b\[\??[0-9;]*[ABCDEFGHJKSTlh]")  # terminal cursor moves (colour codes are kept)


# ---------------------------------------------------------------------------
# Small printing helpers
# ---------------------------------------------------------------------------
def _ok(text):
    print(f"✅ {text}")


def _bad(text):
    print(f"❌ {text}")


def _tip(text):
    print(f"👉 {text}")


def _show_link(url, label):
    """A clickable link in the notebook (plain text if the notebook can't show HTML)."""
    try:
        from IPython.display import HTML, display
        display(HTML(f'👉 <a href="{url}" target="_blank">{html.escape(label)}</a> &nbsp; <code>{url}</code>'))
    except ImportError:
        print(f"👉 {label}: {url}")


def _environment():
    """The settings every command gets: unbuffered output (so you see it live) and UTF-8 on Windows."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    # Colours yes, animations no: spinners redraw themselves with cursor codes a notebook can't show.
    env["TERM"] = "dumb"
    env["FORCE_COLOR"] = "1"
    env["PY_COLORS"] = "1"
    # Put this Python's folder first on PATH, so tools started by the scripts use the .venv too.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return env


def url(path="/"):
    """The address of the bot. In GitHub Codespaces that is the forwarded-port address, not localhost."""
    codespace = os.getenv("CODESPACE_NAME")
    domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    if codespace:
        return f"https://{codespace}-{PORT}.{domain}{path}"
    return f"http://localhost:{PORT}{path}"


# ---------------------------------------------------------------------------
# 0 · Is everything ready?
# ---------------------------------------------------------------------------
def check():
    """The notebook version of `python check_setup.py`, plus: is this notebook using the .venv?"""
    version = sys.version_info
    in_venv = ".venv" in Path(sys.prefix).parts

    if in_venv:
        _ok(f"The notebook runs on the project's .venv (Python {version.major}.{version.minor}.{version.micro})")
    else:
        _bad(f"The notebook runs on {sys.executable}, not on the project's .venv")
        _tip("Click 'Select Kernel' (top right of the notebook) → Python Environments → .venv, then run this cell again.")
        _tip("No .venv yet? Run the setup once in a terminal: see PRE_CONFERENCE.md (or use GitHub Codespaces).")
        return False

    print()
    return run(".", "python check_setup.py") == 0


# ---------------------------------------------------------------------------
# 1 · Run a command, exactly like typing it in a terminal
# ---------------------------------------------------------------------------
def run(folder, command, timeout=None):
    """
    Run one command from COMMANDS_*.md inside `folder` and show its output live.
        run("build/step1_model", "python ask_simple.py")
        run("evaluate/step6_rules", "pytest test_rules.py -v")
    Returns the exit code (0 = success).
    """
    parts = shlex.split(command)
    if parts[0] == "python":
        parts = [sys.executable] + parts[1:]
    elif parts[0] == "pytest":
        parts = [sys.executable, "-m", "pytest"] + parts[1:]
    elif parts[0] == "uvicorn":
        _bad("Use nb.start_bot(...) for uvicorn: a server would keep this cell busy forever.")
        return 1

    work_folder = ROOT / folder
    print(f"$ cd {folder}   ·   {command}\n")

    process = subprocess.Popen(
        parts,
        cwd=work_folder,
        env=_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    started = time.time()
    try:
        for line in process.stdout:
            line = CURSOR_CODES.sub("", line)
            print(line, end="")
            if timeout and time.time() - started > timeout:
                process.kill()
                _bad(f"Stopped after {timeout} seconds.")
                break
        code = process.wait()
    except KeyboardInterrupt:          # the ■ (stop) button of the cell
        process.kill()
        process.wait()
        print()
        _bad("Stopped by you.")
        return 1

    print()
    if code == 0:
        _ok("Finished.")
    elif parts[1:3] == ["-m", "pytest"]:
        _bad(f"pytest exit code {code}: at least one test FAILED (see above). "
             "With a planted bug, that is exactly what you want!")
    else:
        _bad(f"Exit code {code}. Read the last lines above; TROUBLESHOOTING.md has the common fixes.")
    return code


def checkpoint(step):
    """Fell behind? Copy in the finished files: the same as `python checkpoint.py stepN`."""
    return run(".", f"python checkpoint.py {step}")


def plant(bug):
    """Break the running bot on purpose (Part 2): plant("liar"). ALWAYS finish with plant("off")."""
    return run(".", f"python plant_bug.py {bug}")


# ---------------------------------------------------------------------------
# 2 · The bot in the background (replaces terminal window 2)
# ---------------------------------------------------------------------------
def _port_busy():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", PORT)) == 0


def _bot_answers():
    """True when the bot's web server answers on port 8000."""
    import httpx
    try:
        return httpx.get(f"http://127.0.0.1:{PORT}/openapi.json", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def _kill(pid):
    """Stop a process and everything it started (uvicorn --reload starts a second process)."""
    try:
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _our_bot():
    """The bot this notebook started last: {"pid", "folder", "app"}, or None."""
    try:
        return json.loads(BOT_PID.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def stop_bot(quiet=False):
    """Stop the bot this notebook started: the same as Ctrl+C in terminal window 2."""
    stopped = False
    running = _our_bot()
    if running:
        _kill(running["pid"])
        stopped = True
    BOT_PID.unlink(missing_ok=True)

    for _ in range(40):                     # wait up to 10 s for port 8000 to be free again
        if not _port_busy():
            break
        time.sleep(0.25)

    if quiet:
        return
    if _port_busy():
        _bad(f"Port {PORT} is still in use by a bot this notebook did not start (a terminal bot?).")
        _tip("Go to that terminal and press Ctrl+C.")
    elif stopped:
        _ok("Bot stopped.")
    else:
        _ok("No bot was running.")


def start_bot(folder, app="app:app", wait=90, restart=True):
    """
    Start a step's bot in the background:  cd <folder>  then  uvicorn <app> --reload
    Any bot this notebook started before is stopped first (only one bot fits on port 8000).
    restart=False keeps the bot if exactly this one is already running (see ensure_bot).
    """
    running = _our_bot()
    if not restart and running and running.get("folder") == folder and running.get("app") == app and _bot_answers():
        _ok(f"Bot is already running: {folder} · {app} (port {PORT}).")
        return True

    stop_bot(quiet=True)

    if _port_busy():
        _bad(f"Port {PORT} is already in use, probably by a bot you started in a terminal.")
        _tip("Pick one path: go to that terminal and press Ctrl+C, then run this cell again.")
        return False

    command = [sys.executable, "-m", "uvicorn", app, "--reload", "--port", str(PORT)]
    print(f"$ cd {folder}   ·   uvicorn {app} --reload   (running in the background)\n")

    extra = {}
    if IS_WINDOWS:
        extra["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        extra["start_new_session"] = True   # its own process group, so stop_bot() stops the reloader too

    log = open(BOT_LOG, "w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=ROOT / folder,
        env=_environment(),
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        **extra,
    )
    BOT_PID.write_text(json.dumps({"pid": process.pid, "folder": folder, "app": app}), encoding="utf-8")

    started = time.time()
    while time.time() - started < wait:
        if process.poll() is not None:
            _bad("The bot stopped right after starting. Its last lines:")
            bot_log(20)
            BOT_PID.unlink(missing_ok=True)
            return False
        if _bot_answers():
            _ok(f"Bot is running: {folder} · {app} (port {PORT}). It reloads by itself when you save a file.")
            return True
        time.sleep(0.5)

    _bad(f"The bot did not answer within {wait} seconds. Its last lines:")
    bot_log(20)
    return False


def ensure_bot(folder="build/step5_agent", app="app:app"):
    """Make sure this bot is running; leave it alone if it already is. Part 2 uses this."""
    return start_bot(folder, app, restart=False)


def bot_log(lines=25):
    """Show the last lines the bot printed: what terminal window 2 would show you."""
    if not BOT_LOG.exists():
        _tip("No bot log yet: start a bot first.")
        return
    text = BOT_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    print("─── bot log (terminal window 2) " + "─" * 40)
    print("\n".join(text[-lines:]) or "(empty)")
    print("─" * 72)


def open_page(path="/", label="Open the chat page"):
    """A clickable link to the bot (the chat page, or /docs)."""
    if not _port_busy():
        _bad("No bot is running yet: run the 'start the bot' cell first.")
        return
    _show_link(url(path), label)
    if os.getenv("CODESPACE_NAME"):
        _tip("Codespaces: the link opens in a new tab. You can also use the PORTS tab → port 8000 → 🌐.")


# ---------------------------------------------------------------------------
# 3 · Talk to the bot from the notebook (like typing in the chat page)
# ---------------------------------------------------------------------------
def chat(*messages):
    """
    Send one or more messages as ONE conversation, like typing them in the chat page:
        chat("Hi, I'm Sam.", "What's my name?")
    The whole conversation is sent every time (the model is a goldfish: that is its memory).
    """
    import httpx

    if not _bot_answers():
        _bad("No bot is answering on port 8000: run the 'start the bot' cell first.")
        return None

    history = []
    data = None
    for message in messages:
        history.append({"role": "user", "content": message})
        print(f"🧑 You: {message}")
        try:
            response = httpx.post(f"http://127.0.0.1:{PORT}/chat", json={"messages": history}, timeout=180)
        except httpx.HTTPError as error:
            _bad(f"The request failed: {error}")
            return None

        if response.status_code != 200:
            _bad(f"HTTP {response.status_code}: {response.text[:300]}")
            _tip("Look at the bot log (nb.bot_log()) for the full error.")
            return None

        data = response.json()
        reply = data.get("reply", data)
        print(f"🤖 Bot: {reply}")
        if data.get("sources"):
            print(f"   📚 sources: {', '.join(data['sources'])}")
        print()
        history.append({"role": "assistant", "content": str(reply)})
    return data


def agent(message):
    """Send one message in Agent mode (POST /agent) and show the reply and the flight recorder."""
    import httpx

    if not _bot_answers():
        _bad("No bot is answering on port 8000: run the 'start the bot' cell first.")
        return None

    print(f"🧑 You: {message}\n")
    try:
        response = httpx.post(f"http://127.0.0.1:{PORT}/agent", json={"message": message}, timeout=300)
    except httpx.HTTPError as error:
        _bad(f"The request failed: {error}")
        return None
    if response.status_code != 200:
        _bad(f"HTTP {response.status_code}: {response.text[:300]}")
        return None

    data = response.json()
    print(f"🤖 Bot: {data.get('reply', '')}")
    outcome = data.get("outcome") or data.get("action")
    if outcome:
        print(f"   outcome: {json.dumps(outcome)}")
    steps = data.get("steps") or []
    if steps:
        print(f"\n   flight recorder ({len(steps)} steps):")
        for number, step in enumerate(steps, 1):
            print(f"   {number:>2}. {json.dumps(step, ensure_ascii=False)[:160]}")
    return data


# ---------------------------------------------------------------------------
# 4 · Have I done the TODOs? (the uncomment exercises in steps 3, 4 and 5)
# ---------------------------------------------------------------------------
def todos(*paths):
    """Count the BEGIN SOLUTION … END SOLUTION blocks you have uncommented in each file."""
    all_done = True
    for path in paths:
        file = ROOT / path
        blocks = []                     # one True/False per block: uncommented yet?
        inside = False
        for line in file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.lstrip("/#").strip() == "BEGIN SOLUTION":
                inside = True
                blocks.append(False)
            elif stripped.lstrip("/#").strip() == "END SOLUTION":
                inside = False
            elif inside and stripped and not stripped.startswith(("#", "//")):
                blocks[-1] = True       # a real code line: this block is uncommented

        done = sum(blocks)
        if not blocks:
            _ok(f"{path}: no TODO blocks left (this is the finished version)")
        elif done == len(blocks):
            _ok(f"{path}: all {len(blocks)} TODO blocks uncommented")
        else:
            all_done = False
            _bad(f"{path}: {done} of {len(blocks)} TODO blocks uncommented")
    if not all_done:
        _tip("Open the file, select the code between BEGIN SOLUTION and END SOLUTION, press Ctrl+/ (Mac: Cmd+/), save.")
        _tip("Short on time? Run the 'use the solution' cell instead.")
    return all_done


# ---------------------------------------------------------------------------
# 5 · The scoreboard (Part 2)
# ---------------------------------------------------------------------------
def report(height=600):
    """Show evaluate/report.html inside the notebook (every pytest run in Part 2 writes it)."""
    file = ROOT / "evaluate" / "report.html"
    if not file.exists():
        _tip("No scoreboard yet: run a pytest cell first.")
        return
    page = file.read_text(encoding="utf-8").replace('<meta http-equiv="refresh" content="2">', "")
    try:
        import warnings
        from IPython.display import HTML, display
        warnings.filterwarnings("ignore", message="Consider using IPython.display.IFrame")
        display(HTML(
            f'<iframe srcdoc="{html.escape(page)}" '
            f'style="width:100%;height:{height}px;border:1px solid #ccc;border-radius:6px;background:#fff"></iframe>'
        ))
        _tip("Run this cell again after the next pytest run to refresh it. "
             "Or open evaluate/report.html from the Explorer.")
    except ImportError:
        print(f"Open {file} in your browser.")
