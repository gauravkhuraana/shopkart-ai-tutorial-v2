# Presenter checklist · sending the tutorial to attendees

For you, not for attendees. Attendees get [../PRE_CONFERENCE.md](../PRE_CONFERENCE.md).

## The plan in one picture
| Path | For | What you must do |
|---|---|---|
| **A · own laptop** | most people | nothing: `python setup_env.py` does it. They have about 8 days and home internet |
| **B · Codespaces** | locked-down laptops | repo must be reachable (public); test it once yourself (below) |
| **D · venue fallback** | bad Wi-Fi on the day | hotspot, `fake_llm`, hosted bot URL (below) |
| **C · offline wheelhouse** | only if many people skip the pre-work | **not built**: see the end |

## Before you send anything (once)
- [ ] `python tools/check_steps.py` runs. (It currently reports step3 and step6 differences that predate the setup work: decide whether to fix them.)
- [ ] **No secrets in the repo.** `.env` is git-ignored, but your local `.env` holds real Groq keys. Check: `git ls-files .env` must print nothing, and `git grep -n gsk_` must show only the placeholder `gsk_your_key_here`. Never zip the folder to share it: use the GitHub link.
- [ ] Commit and push: `.env.example` (renamed from `.env copy.example`), `setup_env.py`, `PRE_CONFERENCE.md`, `COMMANDS_WINDOWS.md`, `COMMANDS_MAC.md`, `.devcontainer/`.
- [ ] The repo is **public**, or attendees can otherwise open it (Codespaces needs this).
- [ ] The links in `PRE_CONFERENCE.md` point at the right repo name and branch (**Code → Download ZIP** and the Codespaces button).

## Test the paths yourself (these are the two things I could not run)
**Path A on a Mac** (Windows was tested: fresh copy, `python setup_env.py`, steps 4, 6, 7, 8, 9 with the fake model):
```bash
git clone https://github.com/gauravkhuraana/shopkart-ai-tutorial-v2.git && cd shopkart-ai-tutorial-v2
python3 setup_env.py
source .venv/bin/activate
python check_setup.py
```
Then walk through [COMMANDS_MAC.md](../COMMANDS_MAC.md) for steps 1, 5 and 9. If the Mac has an old system Python (3.9 or lower), the script says so and points to python.org.

**Path B (Codespaces):** create a codespace from the repo page, paste a key for both secrets, wait for setup, then:
```bash
python check_setup.py
cd build/step5_agent && uvicorn app:app --reload      # the forwarded port 8000 opens the chat page
```
Also try the scoreboard: `python -m http.server 8080 --directory evaluate` and open port 8080.
- **Prebuilds** make it start in seconds instead of minutes: repo Settings → Codespaces → *Set up prebuild*. They use some of your own quota and storage.
- Free accounts get a monthly allowance of core-hours. **Check the current number** on GitHub's pricing/billing page before you promise anything to attendees.

## When to send what
| When | Send / do |
|---|---|
| 10 days before | Email: the repo link and `PRE_CONFERENCE.md`. One line: "pick Path A, or Path B if your laptop is locked down" |
| 7 days before | Reminder. Ask people to reply with a screenshot of `python check_setup.py` all OK |
| 3 days before | Nudge the people who did not reply. Offer Path B or "sit next to someone" |
| 1 day before | Final reminder: charge the laptop, bring a phone hotspot |

## On the day: fallbacks
- **Venue Wi-Fi is slow or blocked.** Everything is installed already, so only Groq calls (small text requests) need a connection. A phone hotspot is enough.
- **Groq says 429 (rate limit).** TROUBLESHOOTING #14. `.env.example` has a backup judge (Cerebras free tier).
- **No internet at all (rehearsal or emergency).** A pretend model and judge, not smart but the plumbing works:
  ```bash
  cd tools
  uvicorn fake_llm:app --port 9999
  ```
  Then in `.env`: `LLM_BASE_URL=http://localhost:9999/v1`, `LLM_MODEL=fake`, `JUDGE_BASE_URL=http://localhost:9999/v1`, `JUDGE_MODEL=fake`.
- **A laptop cannot run the bot.** Put your hosted bot's address in `.env` as `SHOPKART_URL` (TROUBLESHOOTING #18).
- **Someone fell behind.** `python checkpoint.py stepN` copies the finished code in place.

## Offline wheelhouse (deferred, not built)
I did not build this, because attendees have about 8 days with home internet and a wheelhouse is fragile: wheels are specific to the Python version and the OS/CPU, and steps 7 to 9 need internet for the judge anyway. Revisit it only if, three days before, many people still have not installed.
If you do, the idea is `pip download -r requirements.txt -d wheelhouse --only-binary=:all: --python-version 3.12 --implementation cp --abi cp312 --platform win_amd64` (repeat for the Mac platforms `macosx_11_0_arm64` and `macosx_10_13_x86_64`), then attendees run `pip install --no-index --find-links wheelhouse -r requirements.txt`. That recipe is **untested**, and it needs exactly Python 3.12 on every laptop. `wheelhouse/` and `dist/` are already in `.gitignore`.
