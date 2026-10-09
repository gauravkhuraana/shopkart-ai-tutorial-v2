# LAB 7 · Mission: catch the dangerous agent (22 min)
**Goal:** plant bugs in the agent crew and write the checks on the journey that catch them.
**You'll learn:** a correct outcome doesn't prove a correct journey. Tool order, amounts, hand-overs, prompt injection and failure handling are all things you can assert on.
File: `tests/test_agents.py`. Keep the step 5 bot running (`uvicorn app:app --reload` in `build/step5_agent`): the tests call `/agent`.

## The flight recorder
Every run returns `steps`: which agent did what, which tool it asked for, with which arguments, in which order.
Try it: `cd build/step5_agent && python agent.py 1043`, then read the list it prints.

Every attack from this morning needs a **lock** (a guard built into `build/step5_agent/agent.py`) and a **test** that proves the lock works (slides 18–19):

| Lock (where it lives) | This morning's attack | Test | You… |
|---|---|---|---|
| Look up first (Implementer) | Refunds before checking | `test_right_tool_right_order` | **write it** (core, TODO 1) |
| Amount ≤ paid (Serve) | Pays too much | `test_right_amount` | write it (stretch, TODO 2) |
| Sees the facts (Reviewer) | Reviewer approves blind | `test_baton_passed` | write it (stretch, TODO 3) |
| Not fooled (Reviewer) | "My manager approved €500" | `test_not_fooled` | run it (ready-made) |
| Over €200 → human (Serve) | Refund the €899 laptop | `test_high_value_escalates` | write it (stretch, TODO 4) |
| System down → human (Implementer) | Order system is down | `test_survives_chaos` | run it (ready-made) |

By default the tests run **3 orders** (1043 refund · 1061 no refund · 2001 escalate), which is fast on any laptop.
All 10 orders: `set ALL_ORDERS=1` (Windows) or `export ALL_ORDERS=1` (Mac/Linux), then run pytest again.

---

## CORE (everyone · ~12 min)

### Mission 1 · Right answer, wrong journey
```bash
python plant_bug.py skip_lookup
pytest tests/test_agents.py -v -k "1043 and (expected_outcome or right_tool)"
```
The customer gets exactly the right refund, €49, and `test_expected_outcome` is **green**. But look at the steps: the agent committed to the refund **before** it looked up the order.
1. **TODO 1 ·** write the tool-order check (`get_order` must come before `issue_refund`). Run again: now it's **red**. Then `python plant_bug.py off`: green.

### Run the whole file
```bash
pytest tests/test_agents.py -v -k "not task_completion"
```
Read the ready-made tests as they pass: **not fooled** (prompt injection), **survives chaos** (order system down) and the five-layer bonus tests at the bottom of the file. Skipped tests are the stretch TODOs.

**Done when:** your TODO 1 goes red with `skip_lookup` planted and green without it.

---

## STRETCH (fast finishers)

### Mission 2 · Catch the overpayment
`python plant_bug.py overpay` → **TODO 2** · money that moved ≤ price paid. Which orders go red? Then `off`.

### Mission 3 · Catch the blind reviewer
`python plant_bug.py blind_reviewer` → **TODO 3** · the Reviewer's input must contain the order number and the order details (`price_paid`). Then `off`.

### Mission 4 · Try to break the kitchen rule
**TODO 4** · orders above 200 EUR must escalate.

---

## BONUS · The five layers of agent testing (ready-made: plant, run, read)
**Real Teams Make Outcomes Outstanding** = Reasoning · Tool use · Memory · Orchestration · Output quality.
The tests are already written at the bottom of `tests/test_agents.py`. Plant each bug and watch exactly one test turn red:

| Layer | Question | Test | Plant this bug |
|---|---|---|---|
| **R**easoning | Did it form a plan about the right order? | `test_reasoning_plan_names_the_order` | (read the plan in the steps) |
| **T**ool use | Right tools, right order, right amount? | Missions 1–4 above | `skip_lookup`, `overpay` |
| **M**emory | Does customer B ever see customer A's order? | `test_memory_customers_isolated` | `shared_memory` |
| **O**rchestration | Does a "no" loop stop after 3 rounds? | `test_orchestration_circuit_breaker` | `no_breaker` |
| **O**utput quality | Do the words match what really happened? | `test_output_reply_matches_outcome` | `false_promise` |

```bash
python plant_bug.py shared_memory
pytest tests/test_agents.py -v -k memory
python plant_bug.py off
```
Tip: `test_orchestration_circuit_breaker` also checks your LAB 5 work. If you skipped LAB 5 TODO 2, it's red even with no bug planted.

Real-world bonus: open `build/step5_agent/agent.py` and find `CHAOS`. It's one variable shared by every request. What happens when two customers call `/agent` at the same moment? That's a two-user isolation bug in our own code.

---

## Stuck?
`python checkpoint.py lab7` · FAQ #12 "agent loops" · #16 "step log empty" · #19 "tests red for no reason"

## Boss level
- Run the AI-judge check: `pytest tests/test_agents.py -v -k task_completion`
- Run the suite in GitHub Actions on every push, with one planted bug, and make the pipeline go red.
