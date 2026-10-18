"""Exercise evaluation scripts offline, without model calls or report-file writes."""

import copy
import io
import itertools
import os
import sys
import time
import warnings
from contextlib import contextmanager, redirect_stdout
from datetime import datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVALUATE = ROOT / "evaluate"


def example_result():
    return {
        "reply": "I've refunded EUR 49.00 within 30 days.",
        "context": ["Returns within 30 days."],
        "outcome": {"action": "refund", "order_id": "1043", "amount": 49.0},
        "steps": [
            {"type": "plan", "content": "Check order 1043."},
            {"type": "tool_call", "name": "get_order"},
            {"type": "proposal", "name": "issue_refund"},
            {"type": "review", "input": 'Order "1043", price_paid: 49.0'},
        ],
    }


@contextmanager
def evaluation_module(
    relative_path, source=None, result=None, scores=None, all_orders=False
):
    """Execute a tutorial file with deterministic bot, judge, clock and environment."""
    path = EVALUATE / relative_path
    if source is None:
        source = path.read_text(encoding="utf-8")
    if result is None:
        result = example_result()

    journal = {"requests": [], "metrics": [], "measurements": [], "status_checks": 0}
    score_values = itertools.cycle(scores or [1.0])

    class Response:
        def json(self):
            return copy.deepcopy(result)

        def raise_for_status(self):
            journal["status_checks"] += 1

    def post(url, **kwargs):
        journal["requests"].append((url, copy.deepcopy(kwargs)))
        return Response()

    class Metric:
        def __init__(self, **kwargs):
            self.__name__ = kwargs.get("name", type(self).__name__)
            self.threshold = kwargs.get("threshold", 0.5)
            self.score = None
            self.reason = "offline reason"
            journal["metrics"].append((type(self).__name__, copy.deepcopy(kwargs)))

        def measure(self, test_case):
            self.score = next(score_values)
            journal["measurements"].append(
                (self.__name__, copy.deepcopy(vars(test_case)))
            )

        def is_successful(self):
            return self.score is not None and self.score >= self.threshold

    metrics = ModuleType("deepeval.metrics")
    for name in [
        "GEval",
        "HallucinationMetric",
        "FaithfulnessMetric",
        "AnswerRelevancyMetric",
        "ToolCorrectnessMetric",
    ]:
        setattr(metrics, name, type(name, (Metric,), {}))

    models = ModuleType("deepeval.models")
    models.LocalModel = SimpleNamespace
    test_case = ModuleType("deepeval.test_case")
    test_case.LLMTestCase = SimpleNamespace
    test_case.ToolCall = SimpleNamespace
    test_case.SingleTurnParams = SimpleNamespace(
        INPUT="input",
        ACTUAL_OUTPUT="actual",
        EXPECTED_OUTPUT="expected",
        CONTEXT="context",
    )
    deepeval = ModuleType("deepeval")
    deepeval.metrics = metrics
    deepeval.models = models
    deepeval.test_case = test_case

    config = SimpleNamespace(
        ROOT=ROOT,
        DATA_DIR=ROOT / "shared" / "data",
        SHOPKART_URL="http://offline-bot",
        judge_model=lambda: "hosted-model",
        local_judge_model=lambda: "local-model",
    )
    ticks = itertools.count()
    clock = ModuleType("time")
    clock.__dict__.update(vars(time))
    clock.time = lambda: next(ticks)
    clock.sleep = lambda seconds: None
    modules = {
        "config": config,
        "httpx": SimpleNamespace(post=post),
        "dotenv": SimpleNamespace(load_dotenv=lambda: None),
        "deepeval": deepeval,
        "deepeval.metrics": metrics,
        "deepeval.models": models,
        "deepeval.test_case": test_case,
        "time": clock,
    }
    environment = {
        "SHOPKART_URL": "http://offline-bot",
        "JUDGE_MODEL": "offline-judge",
        "JUDGE_BASE_URL": "http://offline-judge",
        "JUDGE_API_KEY": "offline-key",
        "ALL_ORDERS": "1" if all_orders else "0",
    }
    namespace = {"__file__": str(path), "__name__": "offline_evaluation"}
    output = io.StringIO()

    with (
        patch.dict(sys.modules, modules),
        patch.dict(os.environ, environment),
        patch.object(sys, "path", list(sys.path)),
        patch.object(sys, "argv", [str(path)]),
        warnings.catch_warnings(),
        redirect_stdout(output),
    ):
        exec(compile(source, str(path), "exec"), namespace)
        yield namespace, journal, output


@pytest.mark.parametrize(
    "path",
    sorted(EVALUATE.rglob("*.py")),
    ids=lambda path: str(path.relative_to(EVALUATE)),
)
def test_all_evaluation_python_files_compile(path):
    compile(path.read_text(encoding="utf-8"), str(path), "exec")


@pytest.mark.parametrize("folder", ["evaluate", "solutions"])
@pytest.mark.parametrize(
    "step,filename,function_name,endpoint,timeout",
    [
        ("step6_rules", "test_rules.py", "ask_bot", "chat", 180),
        ("step7_judge", "test_judge.py", "ask_bot", "chat", 180),
        ("step8_agent", "test_agents.py", "run_crew", "agent", 300),
    ],
)
def test_repeated_bot_calls_return_fresh_responses(
    folder, step, filename, function_name, endpoint, timeout
):
    path = Path("..") / folder / step / filename
    with evaluation_module(path) as (module, journal, output):
        response = Mock()
        response.json.side_effect = [
            {"reply": "First reply"},
            {"reply": "Second reply"},
        ]
        post = Mock(return_value=response)
        module["httpx"].post = post
        ask_bot = module[function_name]
        message = "Repeat this question"

        if endpoint == "agent":
            first = ask_bot(message, chaos="orders_down")
            second = ask_bot(message, chaos="orders_down")
            request_body = {"message": message, "chaos": "orders_down"}
        else:
            first = ask_bot(message)
            second = ask_bot(message)
            request_body = {"messages": [{"role": "user", "content": message}]}

        assert first == {"reply": "First reply"}
        assert second == {"reply": "Second reply"}
        expected_request = call(
            f"http://offline-bot/{endpoint}", json=request_body, timeout=timeout
        )
        assert post.call_args_list == [expected_request, expected_request]
        assert response.raise_for_status.call_count == 2


def test_simple_rule_script_uses_the_current_experiment_settings():
    with evaluation_module("step6_rules/rules_simple.py") as (module, journal, output):
        assert module["problems"] == []
        assert "PASS: the answer follows both rules" in output.getvalue()
        assert journal["requests"][0][1]["json"] == {
            "messages": [{"role": "user", "content": module["QUESTION"]}]
        }


@pytest.mark.parametrize("empty_context", [False, True])
def test_simple_judge_measures_the_configured_metrics(empty_context):
    result = example_result()
    if empty_context:
        result["context"] = []
    with evaluation_module("step7_judge/judge_simple.py", result=result) as (
        module,
        journal,
        output,
    ):
        assert len(journal["measurements"]) == len(module["metrics"])
        expected = ["(no policy pages)"] if empty_context else result["context"]
        assert journal["measurements"][0][1]["retrieval_context"] == expected
        assert "score 1.00" in output.getvalue()


def test_judge_suite_selects_cases_and_records_every_metric():
    with evaluation_module("step7_judge/test_judge.py") as (module, journal, output):
        expected_ids = [case["id"] for case in module["GOLDEN"] if case.get("judge")]
        selected_ids = [case["id"] for case in module["JUDGE_CASES"]]
        assert selected_ids == expected_ids
        scoreboard = Mock()
        module["test_judge"](module["JUDGE_CASES"][0], scoreboard)
        assert len(journal["measurements"]) == 5
        scoreboard.add.assert_called_once()


def test_simple_agent_script_keeps_the_flight_recorder_order():
    with evaluation_module("step8_agent/agent_check_simple.py") as (
        module,
        journal,
        output,
    ):
        assert module["tools"] == ["get_order", "issue_refund"]
        assert module["checks"]["reviewer saw the facts"]
        assert "Flight recorder:" in output.getvalue()
        names = [tool.name for tool in journal["measurements"][0][1]["tools_called"]]
        assert names == ["get_order", "issue_refund"]


@pytest.mark.parametrize("all_orders", [False, True])
def test_agent_suite_order_selection_and_existing_skips(all_orders):
    with evaluation_module("step8_agent/test_agents.py", all_orders=all_orders) as (
        module,
        journal,
        output,
    ):
        selected = module["ORDERS_TO_RUN"]
        assert len(selected) == (10 if all_orders else 3)
        high_value_marks = module["test_high_value_escalates"].pytestmark
        high_value_ids = high_value_marks[0].args[1]
        expected = [
            order_id
            for order_id in selected
            if module["ORDERS"][order_id]["price_paid"] > 200
        ]
        assert high_value_ids == expected

        for name in [
            "test_right_tool_right_order",
            "test_right_amount",
            "test_baton_passed",
            "test_high_value_escalates",
        ]:
            with pytest.raises(pytest.skip.Exception, match="TODO"):
                module[name]("1043")

        module["test_reasoning_plan_names_the_order"]("1043")
        module["test_output_reply_matches_outcome"]("1043")
        scoreboard = Mock()
        module["test_tool_correctness"]("1043", scoreboard)
        module["test_task_completion"]("1043", scoreboard)
        assert scoreboard.add.call_count == 2


def test_trial_script_reports_range_and_agreement_without_changing_scores():
    with evaluation_module("step9_trial/trial_simple.py", scores=[0.2, 0.6, 0.4]) as (
        module,
        journal,
        output,
    ):
        assert module["scores"] == [0.2, 0.6, 0.4]
        assert module["average"] == pytest.approx(0.4)
        assert module["score_range"] == pytest.approx(0.4)
        assert "scores 0.20, 0.60, 0.40  ->  range 0.40" in output.getvalue()
        assert "MY_SCORE" in output.getvalue()


def test_full_trial_scores_both_judges_and_handles_failed_runs():
    with evaluation_module("step9_trial/judge_the_judge.py") as (
        module,
        journal,
        output,
    ):
        module["main"]()
        assert len(journal["measurements"]) == 30
        assert "LOCAL judge" in output.getvalue()
        assert "HOSTED judge" in output.getvalue()

    with evaluation_module("step9_trial/judge_the_judge.py") as (
        module,
        journal,
        output,
    ):
        module["score"] = Mock(side_effect=RuntimeError("offline failure"))
        module["main"]()
        assert output.getvalue().count("judge failed on") == 30
        assert "nan" in output.getvalue()


@pytest.mark.parametrize("score", [None, 0.0, 0.3, 0.8, 1.0])
def test_scoreboard_renders_scores_and_escapes_content(score):
    with evaluation_module("conftest.py") as (module, journal, output):
        metric = {
            "name": "<Metric>",
            "reason": "<reason>",
            "score": score,
            "threshold": 0.7,
            "passed": score is not None and score >= 0.7,
        }
        row = {
            "file": "step7 / test_judge.py",
            "name": "<test>",
            "message": "<failure>",
            "outcome": "failed",
            "metrics": [metric],
        }
        rendered = module["_row_html"](row)
        assert "&lt;Metric&gt;" in rendered
        assert "&lt;test&gt;" in rendered
        assert "&lt;reason&gt;" in rendered
        assert (
            "error" in rendered if score is None else f"{score:.2f} / 0.7" in rendered
        )


def test_scoreboard_counts_groups_and_writes_only_to_the_supplied_target():
    with evaluation_module("conftest.py") as (module, journal, output):
        report = Mock()
        module["REPORT"] = report
        module["datetime"] = SimpleNamespace(now=lambda: datetime(2026, 10, 18, 9, 0))
        module["STATE"]["running"] = False
        for outcome in ["passed", "failed", "skipped"]:
            module["RESULTS"].append(
                {
                    "file": "example.py",
                    "name": outcome,
                    "message": "",
                    "outcome": outcome,
                    "metrics": [],
                }
            )
        module["_write"]()
        page = report.write_text.call_args.args[0]
        assert "finished · 3 tests" in page
        assert page.count("<h2>example.py</h2>") == 1
        for outcome in ["passed", "failed", "skipped"]:
            assert f"<b>1</b><span>{outcome}" in page


@pytest.mark.parametrize(
    "when,outcome",
    [
        ("setup", "passed"),
        ("teardown", "passed"),
        ("call", "passed"),
        ("call", "failed"),
        ("setup", "skipped"),
        ("setup", "failed"),
        ("teardown", "failed"),
    ],
)
def test_scoreboard_hook_keeps_latest_metrics_and_existing_phase_rules(when, outcome):
    with evaluation_module("conftest.py") as (module, journal, output):
        module["REPORT"] = Mock()
        latest_metrics = [
            {
                "name": "latest",
                "score": 0.8,
                "threshold": 0.7,
                "passed": True,
                "reason": "",
            }
        ]
        item = SimpleNamespace(
            fspath=EVALUATE / "step7_judge" / "test_judge.py",
            name="example",
            user_properties=[
                ("metrics", [{"name": "earlier"}]),
                ("other", "ignored"),
                ("metrics", latest_metrics),
            ],
        )
        report = SimpleNamespace(
            when=when,
            outcome=outcome,
            skipped=outcome == "skipped",
            failed=outcome == "failed",
            longrepr=("example.py", 1, "Skipped: TODO exercise"),
            duration=0.16,
        )
        call = SimpleNamespace(
            excinfo=SimpleNamespace(
                value=AssertionError("failure details\nassert False")
            )
        )
        hook = module["pytest_runtest_makereport"](item, call)
        next(hook)
        with pytest.raises(StopIteration):
            hook.send(SimpleNamespace(get_result=lambda: report))

        if when != "call" and outcome == "passed":
            assert module["RESULTS"] == []
            module["REPORT"].write_text.assert_not_called()
        else:
            row = module["RESULTS"][0]
            assert row["metrics"] is latest_metrics
            assert row["seconds"] == 0.2
            if outcome == "skipped":
                assert row["message"] == "TODO exercise"
            elif outcome == "failed":
                assert row["message"] == "failure details"


def test_yaml_examples_keep_explicit_score_placeholders():
    scores_file = EVALUATE / "step9_trial" / "my_scores.yaml"
    items = yaml.safe_load(scores_file.read_text(encoding="utf-8"))
    assert len(items) == 5
    assert all(item["my_score"] is None for item in items)
