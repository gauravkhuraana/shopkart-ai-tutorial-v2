"""Check the bug-switch command without changing the running bot's state."""

import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bug_cli(tmp_path, monkeypatch, capsys):
    helper_path = ROOT / "shared" / "planted_bugs.py"
    spec = importlib.util.spec_from_file_location("offline_planted_bugs", helper_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.STATE_FILE = tmp_path / ".planted_bug"
    monkeypatch.setitem(sys.modules, "planted_bugs", module)

    def run(*arguments):
        command = ROOT / "plant_bug.py"
        monkeypatch.setattr(sys, "argv", [str(command), *arguments])

        with patch.object(sys, "path", list(sys.path)):
            try:
                runpy.run_path(str(command), run_name="__main__")
            except SystemExit as error:
                exit_code = error.code
            else:
                exit_code = 0

        return exit_code, capsys.readouterr().out

    return SimpleNamespace(run=run, state=module.STATE_FILE, bugs=module.BUGS)


@pytest.mark.parametrize("active_bug", ["", "liar"])
def test_listing_shows_active_bug_without_changing_state(bug_cli, active_bug):
    if active_bug:
        bug_cli.state.write_text(active_bug, encoding="utf-8")

    exit_code, output = bug_cli.run()

    assert exit_code == 0
    expected_name = active_bug or "none (healthy bot)"
    assert f"Active bug: {expected_name}" in output
    for name, description in bug_cli.bugs.items():
        marker = "*" if name == active_bug else " "
        assert f"  {marker} {name:<15} {description}" in output

    if active_bug:
        assert bug_cli.state.read_text(encoding="utf-8") == active_bug
    else:
        assert not bug_cli.state.exists()


@pytest.mark.parametrize(
    "bug_name",
    [
        "liar",
        "no_pages",
        "skip_lookup",
        "overpay",
        "blind_reviewer",
        "no_breaker",
        "shared_memory",
        "false_promise",
    ],
)
def test_enabling_a_bug_replaces_the_previous_selection(bug_cli, bug_name):
    bug_cli.state.write_text("previous_bug", encoding="utf-8")

    exit_code, output = bug_cli.run(bug_name)

    assert exit_code == 0
    assert bug_cli.state.read_text(encoding="utf-8") == bug_name
    assert f"Planted '{bug_name}': {bug_cli.bugs[bug_name]}" in output
    assert "python plant_bug.py off" in output


@pytest.mark.parametrize("command", ["off", "none", "fix"])
def test_disabling_clears_the_bug_selection(bug_cli, command):
    bug_cli.state.write_text("liar", encoding="utf-8")

    exit_code, output = bug_cli.run(command)

    assert exit_code == 0
    assert bug_cli.state.read_text(encoding="utf-8") == ""
    assert "All bugs removed: the bot is healthy again." in output


@pytest.mark.parametrize("invalid_name", ["unknown", "LIAR"])
def test_invalid_names_fail_without_changing_the_selection(bug_cli, invalid_name):
    bug_cli.state.write_text("liar", encoding="utf-8")

    exit_code, output = bug_cli.run(invalid_name)

    assert exit_code == 1
    assert f"Unknown bug '{invalid_name}'" in output
    assert ", ".join(bug_cli.bugs) in output
    assert bug_cli.state.read_text(encoding="utf-8") == "liar"


def test_state_write_errors_are_not_hidden(bug_cli):
    with patch.object(Path, "write_text", side_effect=PermissionError("read-only")):
        with pytest.raises(PermissionError, match="read-only"):
            bug_cli.run("liar")
