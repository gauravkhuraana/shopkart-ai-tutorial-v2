"""
STEP 8 · Test the agent: check the JOURNEY, not just the landing.

Three parts:
    1. Send one customer message to the crew (POST /agent, the same as Agent mode in the chat page)
    2. Read the flight recorder: every step, which agent, which tool, which arguments, in which order
    3. Check it: the outcome, the tool order, the hand-over to the Reviewer, the amount

No AI judge needed here: a tool call is just data, and data is something we can assert on.

Check E at the bottom does the same "right tools, right order" check with a ready-made DeepEval agent
metric (ToolCorrectnessMetric). DeepEval has more of them: see "THE AGENT METRICS MENU" at the very end.

Keep your step 5 bot running in another terminal (cd build/step5_agent, then uvicorn app:app --reload).

Run it (from this folder, with your virtual environment active):

    python agent_check_simple.py

2 live demos. Plant one bug in the REAL crew, then run this unchanged script:

    python ../../plant_bug.py skip_lookup   # refund comes before the lookup
    python agent_check_simple.py            # check C should fail

    python ../../plant_bug.py overpay       # real payment step doubles the refund
    python agent_check_simple.py            # check D should fail

    python ../../plant_bug.py off           # always restore the healthy crew

The model still plans the case. The planted bug changes a real agent step after planning,
which makes the demo predictable instead of waiting for the model to make a random mistake.
"""

import json
import os
import warnings

import httpx
#imp
from deepeval.metrics import ToolCorrectnessMetric

from deepeval.models import LocalModel
#imp
from deepeval.test_case import LLMTestCase, ToolCall
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the main project folder
warnings.filterwarnings("ignore")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")
BOT = os.getenv("SHOPKART_URL", "http://localhost:8000")


# 1. Send one customer message to the crew

message = "My headphones from order 1043 arrived broken, refund please."
PRICE_PAID = 49.0  # what the customer paid for order 1043 (shared/data/orders.json)

request_body = {
    "message": message,
}

response = httpx.post(
    f"{BOT}/agent",
    json=request_body,
    timeout=300,
)
response.raise_for_status()
result = response.json()

# 2. Read the flight recorder

print("Customer:", message)
print("Reply:   ", result["reply"])
print("Outcome:")
print(json.dumps(result["outcome"], indent=2))
print("Flight recorder:")
for step_number, step in enumerate(result["steps"], start=1):
    print(f"Step {step_number}:")
    print(json.dumps(step, indent=2))
print("--------------------------------------------")

tools = []
reviews = []

for step in result["steps"]:
    if step["type"] in ("tool_call", "proposal"):
        tools.append(step["name"])

    if step["type"] == "review":
        reviews.append(step)


# 3. Check it

checks = {}

# Check A · The landing: did the customer get the right outcome?
action = result["outcome"]["action"]
checks["right outcome (refund)"] = action == "refund"

# Check B · The baton: did the Reviewer SEE the order facts, or approve blind?
reviewer_saw_the_facts = bool(reviews)

for review in reviews:
    review_input = review["input"]
    has_order_number = "1043" in review_input
    has_order_details = "price_paid" in review_input
    reviewer_saw_the_facts = (
        reviewer_saw_the_facts and has_order_number and has_order_details
    )

checks["reviewer saw the facts"] = reviewer_saw_the_facts

# TODO 1 · Check C · The journey: "get_order" must come BEFORE "issue_refund".
#          Uncomment the last line (Ctrl+/, or Edit -> Toggle Line Comment) to add the check.
if "issue_refund" in tools and "get_order" in tools:
    looked_up_first = tools.index("get_order") < tools.index("issue_refund")
else:
    looked_up_first = "issue_refund" not in tools  # no refund proposed: nothing to look up first
# checks["looked up before refunding"] = looked_up_first

# TODO 2 · Check D · The money: the amount that moved must be at most PRICE_PAID.
#          Uncomment the last line to add the check.
amount_refunded = result["outcome"].get("amount", 0)
# checks["no overpayment"] = amount_refunded <= PRICE_PAID

# Check E · The journey again, with a ready-made DeepEval agent metric: ToolCorrectnessMetric.
# Same question as check C ("right tools, right order?"), but DeepEval gives you the score AND the reason.
# It only compares two lists, so there is no AI call and no API key needed.
tools_called = []

for name in tools:
    tools_called.append(ToolCall(name=name))

expected_tools = [
    ToolCall(name="get_order"),
    ToolCall(name="issue_refund"),
]

test_case = LLMTestCase(
    input=message,
    actual_output=result["reply"],
    tools_called=tools_called,  # what the crew really did
    expected_tools=expected_tools,  # what a good journey does
)

# This metric compares tool lists locally; its required model object is not called.
unused_model = LocalModel(
    model="not-used",
    base_url="http://localhost",
    api_key="not-used",
)

metric = ToolCorrectnessMetric(
    threshold=1.0,  # 1.0 = every expected tool was called, in the right order
    should_consider_ordering=True,  # the order matters: look up BEFORE paying
    model=unused_model,
    async_mode=False,
)
metric.measure(test_case)
checks["DeepEval tool correctness"] = metric.is_successful()


# Results

for name, ok in checks.items():
    if ok:
        verdict = "PASS"
    else:
        verdict = "FAIL"

    print(f"{verdict}  {name}")

print()
print(f"DeepEval ToolCorrectnessMetric: score {metric.score:.2f}")
print(f"  tools called:   {tools}")
print(f"  reason: {metric.reason}")


# ---------------------------------------------------------------------------
# THE AGENT METRICS MENU: assertions DeepEval gives you ready-made for AGENTS
# ---------------------------------------------------------------------------
# For a chatbot you asked: "is the answer true / grounded / relevant?"  (step 7)
# For an agent you ask:    "was the JOURNEY right?"  DeepEval has metrics for that too:
#
#   Metric                    The question it answers                            Needs the AI judge?
#   ------------------------  -------------------------------------------------  -------------------
#   ToolCorrectnessMetric     Right tools, in the right order?  (used above)     no
#   ArgumentCorrectnessMetric Right arguments given to each tool?                yes
#   ToolUseMetric             Picked the best tool from the ones available?      yes
#   TaskCompletionMetric      Did the agent finish what the user asked?          yes
#   PlanQualityMetric         Was the plan the agent wrote any good?             yes
#   PlanAdherenceMetric       Did it FOLLOW its own plan?                        yes
#   StepEfficiencyMetric      Any wasted or repeated steps?                      yes
#   AgentLoopDetectionMetric  Stuck going round in circles?                      no
#
# Same shape as every metric in this course: build it, call metric.measure(test_case), read score + reason.
# The ones with a judge also read the agent's recorded trace (DeepEval's @observe tracing).
# Rule of thumb from the top of this file: exact facts -> plain Python or ToolCorrectnessMetric (free, fast,
# repeatable); meaning -> a judge metric (slower, costs calls, and you put it on trial in step 9).
# More: https://deepeval.com/docs/metrics-introduction
