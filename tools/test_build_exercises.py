"""Offline checks for starter code and the code attendees uncomment."""

import ast
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
EXERCISES = {
    "step3_ui/index.html": 2,
    "step3_ui/index_simple.html": 2,
    "step4_ground/app.py": 3,
    "step4_ground/app_simple.py": 3,
    "step5_agent/agent.py": 3,
    "step5_agent/agent_simple.py": 3,
}


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_script = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.inside_script = True
            self.scripts.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside_script = False

    def handle_data(self, data):
        if self.inside_script:
            self.scripts[-1] += data


def run_javascript(script, check_only=False):
    with tempfile.TemporaryDirectory(prefix="shopkart-js-check-") as folder:
        path = Path(folder) / "check.js"
        path.write_text(script, encoding="utf-8")
        command = ["node"]
        if check_only:
            command.append("--check")
        command.append(str(path))
        subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )


def uncomment_solutions(source):
    lines = []
    inside = False

    for line in source.splitlines(keepends=True):
        if re.match(r"\s*(#|//) BEGIN SOLUTION\s*$", line):
            assert not inside
            inside = True
        elif re.match(r"\s*(#|//) END SOLUTION\s*$", line):
            assert inside
            inside = False
        elif inside:
            match = re.match(r"(\s*?)(#|//)( ?)(.*?)(\r?\n)?$", line)
            assert match, f"Solution code is already active: {line!r}"
            line = match[1] + match[4] + (match[5] or "")

        lines.append(line)

    assert not inside
    return "".join(lines)


def load_blocks(relative_path, names, completed=False, **namespace):
    source = (BUILD / relative_path).read_text(encoding="utf-8")
    if completed:
        source = uncomment_solutions(source)

    selected = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            node.decorator_list = []
            selected.append(node)
        elif isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id in names
                for target in node.targets
            ):
                selected.append(node)

    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(module, relative_path, "exec"), namespace)
    return namespace


@pytest.mark.parametrize("relative_path,count", EXERCISES.items())
def test_exercises_have_only_commented_answers(relative_path, count):
    source = (BUILD / relative_path).read_text(encoding="utf-8")
    assert source.count("BEGIN SOLUTION") >= count
    assert len(re.findall(r"(?m)^\s*(?:#|//) BEGIN SOLUTION\s*$", source)) == count
    assert len(re.findall(r"(?m)^\s*(?:#|//) END SOLUTION\s*$", source)) == count
    assert len(re.findall(r"(?m)^\s*(?:#|//) TODO \d", source)) == count
    uncomment_solutions(source)


@pytest.mark.parametrize(
    "path", sorted(BUILD.rglob("*.py")), ids=lambda path: str(path.relative_to(BUILD))
)
@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
def test_python_compiles_in_both_states(path, completed):
    source = path.read_text(encoding="utf-8")
    if completed:
        source = uncomment_solutions(source)
    compile(source, str(path), "exec")


@pytest.mark.parametrize(
    "path", sorted(BUILD.rglob("*.html")), ids=lambda path: str(path.relative_to(BUILD))
)
@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
def test_browser_scripts_compile_in_both_states(path, completed):
    source = path.read_text(encoding="utf-8")
    if completed:
        source = uncomment_solutions(source)
    parser = ScriptParser()
    parser.feed(source)
    assert parser.scripts
    for script in parser.scripts:
        run_javascript(script, check_only=True)


@pytest.mark.parametrize("filename", ["index.html", "index_simple.html"])
@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
def test_ui_exercises_work_by_uncommenting_only(filename, completed):
    source = (BUILD / "step3_ui" / filename).read_text(encoding="utf-8")
    if completed:
        source = uncomment_solutions(source)

    functions = []
    for name in ["sendToApi", "showAnswer"]:
        match = re.search(
            rf"(?ms)^([ \t]*)(?:async )?function {name}\([^\n]*\) \{{.*?^\1\}}",
            source,
        )
        assert match
        functions.append(match[0])

    harness = r"""
const assert = require("node:assert/strict");
let calls = 0;
global.fetch = async (url, options) => {
  calls++;
  assert.equal(url, "/chat");
  assert.equal(options.method, "POST");
  assert.equal(options.headers["Content-Type"], "application/json");
  assert.deepEqual(JSON.parse(options.body), {messages: []});
  return {ok: true, json: async () => ({reply: "Example reply"})};
};
(async () => {
  const result = await sendToApi({messages: []});
  const element = {};
  showAnswer(element, {reply: "Example reply"});
  if (COMPLETED) {
    assert.equal(calls, 1);
    assert.equal(result.reply, "Example reply");
    assert.equal(element.textContent, "Example reply");
    global.fetch = async () => ({ok: false, statusText: "Unavailable"});
    await assert.rejects(sendToApi({messages: []}), /Unavailable/);
  } else {
    assert.equal(calls, 0);
    assert.match(result.reply, /TODO 1/);
    assert.equal(element.textContent, '{"reply":"Example reply"}');
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    script = "\n".join(functions) + harness.replace("COMPLETED", json.dumps(completed))
    run_javascript(script)


@pytest.mark.parametrize("filename", ["app.py", "app_simple.py"])
@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
def test_grounding_exercises_work_by_uncommenting_only(filename, completed):
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Example reply"))]
    )
    page = {"name": "returns.md", "text": "Return most items within 30 days."}
    retrieve = Mock(return_value=[page])
    namespace = load_blocks(
        f"step4_ground/{filename}",
        {"chat", "SYSTEM_PROMPT"},
        completed,
        ChatRequest=object,
        client=client,
        retrieve=retrieve,
        planted_bugs=SimpleNamespace(tamper_pages=lambda pages, question: pages),
        record_chat=Mock(),
        config=SimpleNamespace(LLM_MODEL="offline-model", clean=lambda text: text),
        MODEL="offline-model",
        TOP_K=3,
        MAX_TOKENS=1000,
        TEMPERATURE=0.2,
        SHOW_PROMPT=False,
        time=SimpleNamespace(time=lambda: 0),
    )
    message = Mock(content="Can I return shoes?")
    message.model_dump.return_value = {"role": "user", "content": message.content}
    result = namespace["chat"](SimpleNamespace(messages=[message]))
    arguments = client.chat.completions.create.call_args.kwargs
    assert result["reply"] == "Example reply"
    assert arguments["messages"][-1] == message.model_dump()

    if completed:
        retrieve.assert_called_once()
        assert result["sources"] == ["returns.md"]
        assert result["context"] == [page["text"]]
        assert "Answer ONLY" in arguments["messages"][0]["content"]
        assert page["text"] in arguments["messages"][0]["content"]
    else:
        retrieve.assert_not_called()
        assert result == {"reply": "Example reply"}
        assert "Answer ONLY" not in arguments["messages"][0]["content"]


@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
@pytest.mark.parametrize("amount", [49, 200, 200.01, 899])
def test_simple_refund_guard(completed, amount):
    namespace = load_blocks(
        "step5_agent/agent_simple.py",
        {"take_action", "issue_refund", "escalate_to_human"},
        completed,
        HUMAN_APPROVAL_LIMIT=200,
    )
    result = namespace["take_action"](
        "issue_refund", {"order_id": "1050", "amount": amount}, []
    )
    expected = "escalate" if completed and amount > 200 else "refund"
    assert result["outcome"]["action"] == expected
    assert result["steps"][-1]["type"] == "action"


@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
def test_simple_agent_loop_and_circuit_breaker(completed):
    client = Mock()
    call = Mock()
    call.function.name = "get_order"
    call.function.arguments = '{"order_id": "1050"}'
    call.id = "call-example"
    call.model_dump.return_value = {"id": call.id, "type": "function"}
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[call]))
        ]
    )
    lookup = Mock(return_value={"order_id": "1050"})
    namespace = load_blocks(
        "step5_agent/agent_simple.py",
        {"run_agent", "take_action", "issue_refund", "escalate_to_human", "TOOLS"},
        completed,
        client=client,
        json=json,
        MODEL="offline-model",
        SYSTEM_PROMPT="Example instructions",
        MAX_STEPS=6,
        HUMAN_APPROVAL_LIMIT=200,
        ACTION_TOOLS={"issue_refund": None, "escalate_to_human": None},
        READ_TOOLS={"get_order": lookup},
    )
    tool_names = [tool["function"]["name"] for tool in namespace["TOOLS"]]
    assert ("escalate_to_human" in tool_names) == completed
    result = namespace["run_agent"]("Refund order 1050.")
    assert client.chat.completions.create.call_count == 6
    assert lookup.call_count == 6
    assert result["outcome"]["order_id"] == "1050"
    assert result["outcome"]["action"] == ("escalate" if completed else "loop_limit")

    client.chat.completions.create.reset_mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="No refund.", tool_calls=None)
            )
        ]
    )
    result = namespace["run_agent"]("Explain the policy.")
    assert client.chat.completions.create.call_count == 1
    assert result["outcome"]["action"] == "no_refund"


@pytest.mark.parametrize("completed", [False, True], ids=["starter", "uncommented"])
def test_full_agent_review_gate_and_refund_guard(completed):
    namespace = load_blocks(
        "step5_agent/agent.py",
        {
            "route_after_policy_review",
            "execute_action",
            "issue_refund",
            "escalate_to_human",
            "_tool",
            "TOOLS",
        },
        completed,
        State=dict,
        MAX_ROUNDS=3,
        HUMAN_APPROVAL_LIMIT=200,
        planted_bugs=SimpleNamespace(active=lambda name: False),
    )
    tool_names = [tool["function"]["name"] for tool in namespace["TOOLS"]]
    assert ("escalate_to_human" in tool_names) == completed

    for approved, rounds, expected in [
        (True, 1, "action_executor"),
        (False, 1, "case_investigator"),
        (False, 3, "give_up"),
    ]:
        state = {"review": {"approved": approved}, "rounds": rounds}
        actual = namespace["route_after_policy_review"](state)
        assert actual == (expected if completed else "action_executor")

    for amount in [49, 200, 200.01, 899]:
        state = {
            "proposal": {
                "name": "issue_refund",
                "args": {"order_id": "1050", "amount": amount},
            },
            "steps": [],
            "facts": [],
        }
        result = namespace["execute_action"](state)
        expected = "escalate" if completed and amount > 200 else "refund"
        assert result["outcome"]["action"] == expected
