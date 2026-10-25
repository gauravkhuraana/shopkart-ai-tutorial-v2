"""Check interpreter selection without installing packages or calling model APIs."""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = [
    (3, 9, 2, "final", False),
    (3, 11, 2, "final", False),
    (3, 12, 0, "final", True),
    (3, 12, 13, "final", True),
    (3, 12, 99, "final", True),
    (3, 12, 0, "candidate", False),
    (3, 13, 13, "final", False),
    (3, 14, 2, "final", False),
    (3, 15, 2, "final", False),
    (3, 16, 0, "alpha", False),
    (4, 0, 0, "final", False),
]


def test_codespaces_uses_the_same_workshop_python():
    config_path = ROOT / ".devcontainer" / "devcontainer.json"
    # This JSONC file contains whole-line comments; leave URLs inside values intact.
    lines = []
    for line in config_path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("//"):
            lines.append(line)
    config = json.loads("\n".join(lines))
    assert config["image"].endswith(":3.12")
    # updateContentCommand runs inside Codespaces prebuilds too (postCreateCommand does not).
    assert config["updateContentCommand"] == "python3.12 setup_env.py --skip-check"


def version_info(major, minor, micro, releaselevel):
    return SimpleNamespace(
        major=major, minor=minor, micro=micro, releaselevel=releaselevel
    )


def fail(message):
    raise RuntimeError(message)


@pytest.mark.parametrize("major,minor,micro,releaselevel,accepted", VERSIONS)
def test_checker_requires_stable_python312(
    major, minor, micro, releaselevel, accepted, capsys
):
    source = (ROOT / "check_setup.py").read_text(encoding="utf-8")
    check_function = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "check"
    )
    namespace = {
        "results": [],
        "sys": SimpleNamespace(
            version_info=version_info(major, minor, micro, releaselevel)
        ),
    }
    module = ast.Module(body=[check_function], type_ignores=[])
    exec(compile(module, "check_setup.py", "exec"), namespace)
    section = source.split("v = sys.version_info", 1)[1]
    section = "v = sys.version_info" + section.split("# 2. Python packages", 1)[0]
    exec(compile(section, "check_setup.py", "exec"), namespace)

    output = capsys.readouterr().out
    assert output.startswith("[OK" if accepted else "[FAIL")
    assert f"You have Python {major}.{minor}.{micro}" in output
    assert "Required for this workshop: stable Python 3.12.x" in output
    assert namespace["results"] == [accepted]
    if not accepted:
        assert "alongside your existing Python" in output
        assert "winget install --id Python.Python.3.12 --version 3.12.10" in output
        assert "py -3.12 setup_env.py" in output
        assert "python3.12 setup_env.py" in output
        assert "existing .venv keeps its old Python" in output


@pytest.mark.parametrize("major,minor,micro,releaselevel,accepted", VERSIONS)
@pytest.mark.parametrize("windows", [False, True], ids=["mac-linux", "windows"])
def test_setup_requires_stable_python312(
    major, minor, micro, releaselevel, accepted, windows, capsys
):
    source = (ROOT / "setup_env.py").read_text(encoding="utf-8")
    section = source.split('step(1, "Python version")', 1)[1]
    section = section.split("# Step 2: Virtual environment", 1)[0]
    namespace = {
        "sys": SimpleNamespace(
            version_info=version_info(major, minor, micro, releaselevel)
        ),
        "IS_WINDOWS": windows,
        "fail": fail,
    }

    if accepted:
        exec(compile(section, "setup_env.py", "exec"), namespace)
    else:
        command = "py -3.12 setup_env.py" if windows else "python3.12 setup_env.py"
        with pytest.raises(RuntimeError) as error:
            exec(compile(section, "setup_env.py", "exec"), namespace)
        assert command in str(error.value)
        assert "winget install --id Python.Python.3.12 --version 3.12.10" in str(error.value)
        assert "alongside your existing Python" in str(error.value)

    output = capsys.readouterr().out
    assert f"You have Python {major}.{minor}.{micro}." in output
    assert "Required for this workshop: Python 3.12.x." in output


def run_environment_section(
    tmp_path, version="3.12.13", returncode=0, existing=True, error=None
):
    source = (ROOT / "setup_env.py").read_text(encoding="utf-8")
    section = source.split('step(2, "Virtual environment (.venv)")', 1)[1]
    section = section.split("# Step 3: Install the packages", 1)[0]
    environment = tmp_path / ".venv"
    interpreter = environment / "python"

    def create_environment(path):
        path.mkdir()
        interpreter.write_text("test interpreter placeholder", encoding="utf-8")

    if existing:
        create_environment(environment)
    process = Mock(
        return_value=SimpleNamespace(
            stdout=version + "\n", stderr="", returncode=returncode
        ),
        side_effect=error,
    )
    builder = Mock()
    builder.create.side_effect = create_environment
    namespace = {
        "VENV": environment,
        "VENV_PYTHON": interpreter,
        "setup_command": "py -3.12 setup_env.py",
        "fail": fail,
        "venv": SimpleNamespace(EnvBuilder=Mock(return_value=builder)),
        "subprocess": SimpleNamespace(
            run=process, TimeoutExpired=subprocess.TimeoutExpired
        ),
    }
    exec(compile(section, "setup_env.py", "exec"), namespace)
    return namespace, process


@pytest.mark.parametrize("existing", [False, True], ids=["new", "existing"])
def test_checks_interpreter_before_installing_packages(tmp_path, existing, capsys):
    namespace, process = run_environment_section(tmp_path, existing=existing)
    assert "Python inside .venv: 3.12.13" in capsys.readouterr().out
    assert process.call_count == 1
    assert process.call_args.args[0][0] == str(namespace["VENV_PYTHON"])
    assert process.call_args.kwargs["timeout"] == 30
    assert namespace["VENV_PYTHON"].read_text() == "test interpreter placeholder"


@pytest.mark.parametrize(
    "version,returncode", [("3.13.13", 1), ("3.15.0", 1), ("3.13.13", 0), ("", 0)]
)
def test_wrong_or_invalid_environment_stops_without_deleting_it(
    tmp_path, version, returncode
):
    with pytest.raises(RuntimeError) as error:
        run_environment_section(tmp_path, version=version, returncode=returncode)
    assert ".venv must use a working, stable Python 3.12.x" in str(error.value)
    assert "Rename .venv" in str(error.value)
    assert "py -3.12 setup_env.py" in str(error.value)
    assert (tmp_path / ".venv" / "python").read_text() == "test interpreter placeholder"


@pytest.mark.parametrize(
    "error",
    [OSError("cannot start interpreter"), subprocess.TimeoutExpired("python", 30)],
)
def test_environment_probe_errors_are_explicit(tmp_path, error):
    with pytest.raises(RuntimeError, match="could not check the Python inside .venv"):
        run_environment_section(tmp_path, error=error)


@pytest.mark.parametrize("major,minor,micro,releaselevel,accepted", VERSIONS)
def test_environment_probe_rejects_incompatible_interpreters(
    tmp_path, major, minor, micro, releaselevel, accepted
):
    _, process = run_environment_section(tmp_path)
    probe = process.call_args.args[0][2]
    nodes = [node for node in ast.parse(probe).body if not isinstance(node, ast.Import)]

    class FakeVersion(tuple):
        def __new__(cls):
            return super().__new__(cls, (major, minor, micro))

        major = property(lambda self: self[0])
        minor = property(lambda self: self[1])
        micro = property(lambda self: self[2])

    fake_version = FakeVersion()
    fake_version.releaselevel = releaselevel

    def exit_process(code):
        raise SystemExit(code)

    namespace = {"sys": SimpleNamespace(version_info=fake_version, exit=exit_process)}
    with pytest.raises(SystemExit) as result:
        exec(
            compile(ast.Module(body=nodes, type_ignores=[]), "<venv-probe>", "exec"),
            namespace,
        )
    assert result.value.code == (0 if accepted else 1)


def final_message(tmp_path, env_text, environ=None, all_checks_passed=False):
    source = (ROOT / "setup_env.py").read_text(encoding="utf-8")
    section = source.split("# Final message: what is still left for the user to do", 1)[1]
    env_file = tmp_path / ".env"
    if env_text is not None:
        env_file.write_text(env_text, encoding="utf-8")
    namespace = {
        "os": SimpleNamespace(environ=environ or {}),
        "env_file": env_file,
        "all_checks_passed": all_checks_passed,
        "ACTIVATE": r".venv\Scripts\Activate.ps1",
        "COMMANDS_FILE": "COMMANDS_WINDOWS.md",
    }
    exec(compile(section, "setup_env.py", "exec"), namespace)
    return namespace


def test_final_message_never_asks_for_a_key_after_all_checks_pass(tmp_path, capsys):
    # Even an odd .env must not contradict a green setup check.
    final_message(tmp_path, "SOMETHING=else\n", all_checks_passed=True)
    output = capsys.readouterr().out
    assert "every check passed" in output
    assert "One thing to remember" in output
    assert "Put your free Groq key" not in output
    assert "Two things" not in output
    assert "1. In EVERY new terminal" in output


def test_setup_runs_the_check_and_uses_its_exit_code():
    source = (ROOT / "setup_env.py").read_text(encoding="utf-8")
    assert 'all_checks_passed = run([VENV_PYTHON, "check_setup.py"]) == 0' in source
    checker = (ROOT / "check_setup.py").read_text(encoding="utf-8")
    assert "sys.exit(0 if all(results) else 1)" in checker


@pytest.mark.parametrize(
    "env_text,environ",
    [
        ("LLM_API_KEY=gsk_real\nJUDGE_API_KEY=gsk_real2\n", None),
        ("LLM_API_KEY=ollama\nJUDGE_API_KEY=gsk_real2  # judge\n", None),
        ('LLM_API_KEY="gsk_real"\nJUDGE_API_KEY=\'gsk_real2\'\n', None),
        ("LLM_API_KEY=gsk_your_key_here\nJUDGE_API_KEY=gsk_your_key_here\n",
         {"LLM_API_KEY": "gsk_env", "JUDGE_API_KEY": "gsk_env"}),
    ],
    ids=["both-in-env-file", "ollama-bot-key", "quoted-values", "environment-wins"],
)
def test_final_message_skips_key_step_when_keys_are_set(tmp_path, capsys, env_text, environ):
    final_message(tmp_path, env_text, environ)
    output = capsys.readouterr().out
    assert "your Groq key is already set" in output
    assert "One thing to remember" in output
    assert "Put your free Groq key" not in output
    assert "Two things" not in output
    assert "1. In EVERY new terminal" in output


@pytest.mark.parametrize(
    "env_text",
    [
        None,
        "LLM_API_KEY=gsk_your_key_here\nJUDGE_API_KEY=gsk_your_key_here\n",
        "LLM_API_KEY=gsk_real\nJUDGE_API_KEY=gsk_your_key_here\n",
        "LLM_API_KEY=gsk_real\n# JUDGE_API_KEY=gsk_commented_out\n",
        "LLM_API_KEY=\nJUDGE_API_KEY=\n",
    ],
    ids=["no-env-file", "placeholders", "judge-placeholder", "judge-commented-out", "empty"],
)
def test_final_message_asks_for_key_when_missing(tmp_path, capsys, env_text):
    final_message(tmp_path, env_text)
    output = capsys.readouterr().out
    assert "Two things are left for YOU" in output
    assert "1. Put your free Groq key" in output
    assert "2. In EVERY new terminal" in output
    assert "already set" not in output


WINGET_COMMAND = (
    "winget install --id Python.Python.3.12 --version 3.12.10 --exact --source winget"
)
MAC_INSTALLER = "https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg"
WINDOWS_INSTALLER = "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"


def test_preconference_uses_one_command_installs():
    guide = (ROOT / "PRE_CONFERENCE.md").read_text(encoding="utf-8")
    assert WINGET_COMMAND in guide
    assert WINDOWS_INSTALLER in guide
    assert MAC_INSTALLER in guide
    assert "brew install python@3.12" in guide
    assert "py -3.12 --version" in guide
    assert "python3.12 --version" in guide
    assert "Found an existing package already installed" in guide
    assert "astral.sh" not in guide
    for line in guide.splitlines():
        if line.startswith("| Mac"):
            assert "not yet tested" in line


@pytest.mark.parametrize(
    "name",
    ["PRE_CONFERENCE.md", "README.md", "COMMANDS_WINDOWS.md", "COMMANDS_MAC.md", "TROUBLESHOOTING.md"],
)
def test_setup_guides_use_simple_python312_commands(name):
    guide = (ROOT / name).read_text(encoding="utf-8")
    assert not re.search(r"https://www\.python\.org/downloads/(?!release/)", guide)
    assert 'tick "Add python.exe to PATH"' not in guide
    for retired in ("uv.exe", "shopkart-tools", "--managed-python", "3.12.13)"):
        assert retired not in guide
    for block in re.findall(r"```(?:powershell|bash)\n(.*?)```", guide, re.DOTALL):
        if "setup_env.py" in block:
            assert block.strip() in ("py -3.12 setup_env.py", "python3.12 setup_env.py"), block


def test_missing_packages_points_to_setup_commands(capsys):
    source = (ROOT / "check_setup.py").read_text(encoding="utf-8")
    section = source.split("if missing:", 1)[1]
    section = "if missing:" + section.split("# 3. The .env settings file", 1)[0]
    with pytest.raises(SystemExit) as result:
        exec(compile(section, "check_setup.py", "exec"), {"missing": ["httpx"], "sys": sys})
    assert result.value.code == 1
    output = capsys.readouterr().out
    assert "py -3.12 setup_env.py" in output
    assert "python3.12 setup_env.py" in output
