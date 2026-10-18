"""Offline regression tests for the beginner-friendly step 6 rule suite."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rule_suite():
    path = ROOT / "evaluate" / "step6_rules" / "test_rules.py"
    spec = importlib.util.spec_from_file_location("step6_rule_suite", path)
    module = importlib.util.module_from_spec(spec)
    config = SimpleNamespace(ROOT=ROOT, SHOPKART_URL="http://offline-bot")

    with patch.dict(sys.modules, {"config": config}):
        spec.loader.exec_module(module)

    return module


def test_test_names_match_the_answer_key(rule_suite):
    assert len(rule_suite.GOLDEN) == 10
    assert rule_suite.CASE_IDS == [case["id"] for case in rule_suite.GOLDEN]


@pytest.mark.parametrize(
    "reply,rules",
    [
        ("A REFUND takes five days.", {"must_include_any": ["exchange", "Refund"]}),
        ("A refund takes five days.", {"must_not_include": ["instant", "Guaranteed"]}),
        ("An ordinary answer.", {}),
        ("An ordinary answer.", {"must_include_any": [], "must_not_include": []}),
        ("This is refundable.", {"must_include_any": ["refund"]}),
    ],
)
def test_passing_rules_are_unchanged(rule_suite, reply, rules):
    rule_suite.ask_bot = Mock(return_value={"reply": reply})
    case = {"question": "Example question", **rules}

    rule_suite.test_rules(case)

    rule_suite.ask_bot.assert_called_once_with("Example question")


@pytest.mark.parametrize(
    "reply,rules,message",
    [
        (
            "Please contact support.",
            {"must_include_any": ["Refund", "Exchange"]},
            "expected one of ['refund', 'exchange'] in: please contact support.",
        ),
        (
            "A GUARANTEED refund.",
            {"must_not_include": ["Guaranteed"]},
            "found forbidden 'Guaranteed' in: a guaranteed refund.",
        ),
        (
            "A guaranteed refund.",
            {"must_include_any": ["exchange"], "must_not_include": ["guaranteed"]},
            "expected one of ['exchange'] in: a guaranteed refund.",
        ),
    ],
)
def test_failure_messages_and_check_order_are_unchanged(
    rule_suite, reply, rules, message
):
    rule_suite.ask_bot = Mock(return_value={"reply": reply})
    case = {"question": "Example question", **rules}

    with pytest.raises(AssertionError) as error:
        rule_suite.test_rules(case)

    assert str(error.value) == message


def test_repeated_questions_make_fresh_requests(rule_suite, monkeypatch):
    first_response = httpx.Response(
        200,
        json={"reply": "First reply"},
        request=httpx.Request("POST", "http://offline-bot/chat"),
    )
    second_response = httpx.Response(
        200,
        json={"reply": "Second reply"},
        request=httpx.Request("POST", "http://offline-bot/chat"),
    )
    post = Mock(side_effect=[first_response, second_response])
    monkeypatch.setattr(rule_suite.httpx, "post", post)

    first = rule_suite.ask_bot("Example question")
    second = rule_suite.ask_bot("Example question")

    assert first == {"reply": "First reply"}
    assert second == {"reply": "Second reply"}
    expected_request = call(
        "http://offline-bot/chat",
        json={"messages": [{"role": "user", "content": "Example question"}]},
        timeout=180,
    )
    assert post.call_args_list == [expected_request, expected_request]


def test_http_failures_are_not_hidden(rule_suite, monkeypatch):
    response = httpx.Response(
        500,
        request=httpx.Request("POST", "http://offline-bot/chat"),
    )
    post = Mock(return_value=response)
    monkeypatch.setattr(rule_suite.httpx, "post", post)

    for attempt in range(2):
        with pytest.raises(httpx.HTTPStatusError):
            rule_suite.ask_bot("Example question")

    assert post.call_count == 2
