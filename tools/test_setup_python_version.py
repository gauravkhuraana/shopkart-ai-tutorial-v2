"""Check interpreter selection without installing packages or calling model APIs."""

import ast
import json
import re
import shlex
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
    assert config["postCreateCommand"] == "python3.12 setup_env.py --skip-check"


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
        assert "PRE_CONFERENCE.md step 1 (CPython 3.12.13)" in output
        assert "step 4 setup command" in output
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
            version_info=version_info(major, minor, micro, releaselevel),
            executable="C:\\Workshop tools\\python.exe" if windows else "/Workshop tools/python",
        ),
        "IS_WINDOWS": windows,
        "fail": fail,
        "shlex": shlex,
    }

    if accepted:
        exec(compile(section, "setup_env.py", "exec"), namespace)
    else:
        with pytest.raises(RuntimeError) as error:
            exec(compile(section, "setup_env.py", "exec"), namespace)
        assert "PRE_CONFERENCE.md step 1" in str(error.value)
        assert "CPython 3.12.13" in str(error.value)
        assert "step 4 setup command" in str(error.value)
        assert "Do not retry with the same incompatible interpreter" in str(error.value)
        assert "alongside your existing Python" in str(error.value)

    output = capsys.readouterr().out
    assert f"You have Python {major}.{minor}.{micro}." in output
    assert "Required for this workshop: Python 3.12.x." in output


@pytest.mark.parametrize(
    "windows,executable,expected",
    [
        (True, r"C:\Workshop tools\python.exe", "& 'C:\\Workshop tools\\python.exe' setup_env.py"),
        (True, r"C:\O'Brien\$work\python.exe", "& 'C:\\O''Brien\\$work\\python.exe' setup_env.py"),
        (False, "/Workshop tools/python", "'/Workshop tools/python' setup_env.py"),
        (False, "/opt/python3.12", "/opt/python3.12 setup_env.py"),
        (False, "/O'Brien/python", shlex.quote("/O'Brien/python") + " setup_env.py"),
    ],
)
def test_retry_uses_the_selected_interpreter(windows, executable, expected):
    source = (ROOT / "setup_env.py").read_text(encoding="utf-8")
    section = source.split('step(1, "Python version")', 1)[1]
    section = section.split("# Step 2: Virtual environment", 1)[0]
    namespace = {
        "sys": SimpleNamespace(
            version_info=version_info(3, 12, 13, "final"),
            executable=executable,
        ),
        "IS_WINDOWS": windows,
        "fail": fail,
        "shlex": shlex,
    }
    exec(compile(section, "setup_env.py", "exec"), namespace)
    assert namespace["setup_command"] == expected


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
        "setup_command": "& 'C:\\Workshop tools\\python.exe' setup_env.py",
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
    assert "& 'C:\\Workshop tools\\python.exe' setup_env.py" in str(error.value)
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


def test_preconference_pins_installation_without_changing_defaults():
    guide = (ROOT / "PRE_CONFERENCE.md").read_text(encoding="utf-8")
    assert "https://astral.sh/uv/0.11.7/install.ps1" in guide
    assert "https://astral.sh/uv/0.11.7/install.sh" in guide
    assert 'UV_NO_MODIFY_PATH = "1"' in guide
    assert "UV_NO_MODIFY_PATH=1" in guide
    assert "python install 3.12.13 --no-bin --no-registry" in guide
    assert "python install 3.12.13 --no-bin" in guide
    assert "python find --managed-python --no-project 3.12.13" in guide
    assert "import sys, ssl, venv, ensurepip" in guide
    assert "sys.version_info[:3] == (3, 12, 13)" in guide
    assert "python-build-standalone" in guide
    assert "3.12.10 was the last official" in guide
    for line in guide.splitlines():
        if "| Mac " in line:
            assert "native installation/setup validation pending" in line


@pytest.mark.parametrize(
    "name",
    ["PRE_CONFERENCE.md", "README.md", "COMMANDS_WINDOWS.md", "COMMANDS_MAC.md", "TROUBLESHOOTING.md"],
)
def test_setup_guides_use_managed_python_in_desktop_commands(name):
    guide = (ROOT / name).read_text(encoding="utf-8")
    assert "3.12.13" in guide
    assert not re.search(r"https://www\.python\.org/downloads/(?!release/)", guide)
    assert 'tick "Add python.exe to PATH"' not in guide
    for block in re.findall(r"```(?:powershell|bash)\n(.*?)```", guide, re.DOTALL):
        assert "py -3.12" not in block
        if "setup_env.py" in block and "python3.12 setup_env.py" not in block:
            assert "python find --managed-python --no-project 3.12.13" in block


def test_missing_packages_points_to_canonical_setup(capsys):
    source = (ROOT / "check_setup.py").read_text(encoding="utf-8")
    section = source.split("if missing:", 1)[1]
    section = "if missing:" + section.split("# 3. The .env settings file", 1)[0]
    with pytest.raises(SystemExit) as result:
        exec(compile(section, "check_setup.py", "exec"), {"missing": ["httpx"], "sys": sys})
    assert result.value.code == 1
    assert "PRE_CONFERENCE.md step 4" in capsys.readouterr().out
