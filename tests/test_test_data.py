import os
import subprocess

import pytest

import payne
from payne.util.file_system import TemporaryDirectory

# Need this to be in scope so it can be autoused
# noinspection PyUnresolvedReferences
from fixtures.index_server import index_server
from dirs import test_data


@pytest.mark.test_data
class TestTestData:
    # Since we're using uv to run a uv project, the lockfile will be honored and
    # all dependencies will be at the .0 version, as locked. The project version
    # (first line) will be the one from the project.
    @pytest.mark.parametrize("name, version, script, expected", [
        #                                   Project version
        #                                   |                  Dependency versions
        #                                   '-----             '-----             '-----
        ("baz", "1.1.0", "baz", "This is baz 1.1.0\n"),
        ("baz", "1.1.1", "baz", "This is baz 1.1.1\n"),
        ("bar", "1.2.0", "bar", "This is bar 1.2.0\nThis is baz 1.1.0\n"),
        ("bar", "1.2.1", "bar", "This is bar 1.2.1\nThis is baz 1.1.0\n"),
        ("foo", "1.3.0", "foo", "This is foo 1.3.0\nThis is bar 1.2.0\nThis is baz 1.1.0\n"),
        ("foo", "1.3.1", "foo", "This is foo 1.3.1\nThis is bar 1.2.0\nThis is baz 1.1.0\n"),
        ("foo", "1.3.2", "foo", "This is foo 1.3.2\nThis is bar 1.2.0\nThis is baz 1.1.0\n"),
        # Cannot run sup in-project because it has no pyproject.toml
    ])
    def test_uv_run(self, name, version, script, expected):
        project = test_data / f"{name}-{version}"

        with TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            del env["VIRTUAL_ENV"]
            env["UV_PROJECT_ENVIRONMENT"] = str(temp_dir)
            env["UV_INDEX"] = "payne_test_data=http://localhost:8000/payne_test_data"

            # Create the project environment and install the project
            # We do this as a separate step so we don't get extra output from
            # the invocation of the script
            try:
                subprocess.run(
                    ["uv", "sync"],  # TODO ensure no changes to uv.lock?
                    cwd=project,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                    universal_newlines=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)
                assert False

            # Run the command in the project
            try:
                result = subprocess.run(
                    ["uv", "run", script],  # TODO ensure no changes to uv.lock?
                    cwd=project,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                    universal_newlines=True,
                    check=True,
                )
                assert result.stdout == expected
                assert result.stderr == ""
            except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)
                assert False

    # Since we're installing the project as a uv tool, the lockfile will not be
    # honored and all dependencies will be at the latest version, unless pinned
    # in the project. The project version (first line) will be the one from the
    # project.
    @pytest.mark.parametrize("name, version, script, expected", [
        #                                   Project version
        #                                   |                  Dependency versions
        #                                   '-----             '-----             '-----
        ("baz", "1.1.0", "baz", "This is baz 1.1.0\n"),
        ("baz", "1.1.1", "baz", "This is baz 1.1.1\n"),
        ("bar", "1.2.0", "bar", "This is bar 1.2.0\nThis is baz 1.1.1\n"),  # Latest baz
        ("bar", "1.2.1", "bar", "This is bar 1.2.1\nThis is baz 1.1.1\n"),  # Latest baz
        ("foo", "1.3.0", "foo", "This is foo 1.3.0\nThis is bar 1.2.1\nThis is baz 1.1.1\n"),  # Latest bar, latest baz
        ("foo", "1.3.1", "foo", "This is foo 1.3.1\nThis is bar 1.2.0\nThis is baz 1.1.1\n"),  # bar pinned, latest baz
        ("foo", "1.3.2", "foo", "This is foo 1.3.2\nThis is bar 1.2.0\nThis is baz 1.1.0\n"),  # bar pinned, baz pinned
        ("sup", "2.1.0", "sup", "This is sup 2.1.0\n"),
    ])
    def test_uv_tool_run(self, name, version, script, expected):
        project = test_data / f"{name}-{version}"

        with TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["UV_TOOL_DIR"] = str(temp_dir)
            env["UV_INDEX"] = "payne_test_data=http://localhost:8000/payne_test_data"

            # Run the command as a tool
            # Uv may output messages on stderr.
            try:
                output = subprocess.check_output(
                    ["uv", "tool", "run", "--from", project, script],
                    cwd=project,
                    env=env,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                    universal_newlines=True,
                )
                assert output == expected
            except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)
                assert False
