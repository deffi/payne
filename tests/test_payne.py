import os
from pathlib import Path

from payne import Payne
from payne.util.file_system import TemporaryDirectory

import pytest

# noinspection PyUnresolvedReferences
from fixtures.index_server import index_server
from dirs import test_data
from utils import child_names, process_output


class TestPayneLocal:
    @staticmethod
    def assert_app_valid(apps_dir: Path, name: str, version: str):
        assert (apps_dir / name)                                .is_dir()   # app group dir
        assert (apps_dir / name / version)                      .is_dir()   # app dir
        assert (apps_dir / name / version / "payne_app.json")   .is_file()  # metadata
        assert (apps_dir / name / version / name)               .is_dir()   # venv
        assert (apps_dir / name / version / name / "pyvenv.cfg").is_file()  # venv metadata

    @staticmethod
    def installed_apps(app_dir: Path) -> dict[str, set[str]]:
        return {name: child_names(app_dir / name)
                for name in child_names(app_dir)}

    @staticmethod
    def installed_scripts(bin_dir: Path) -> set[str]:
        script_files = child_names(bin_dir)

        # On Windows, all script names must end with .exe and we remove that
        if os.name == "nt":
            assert all(script_file.endswith(".exe") for script_file in script_files)
            script_files = {script_file[:-4] for script_file in script_files}

        return script_files

    @pytest.mark.parametrize("source", ["local", "remote"])
    def test_install_uninstall(self, source):
        with TemporaryDirectory() as temp_dir:
            def install_app(name: str, version: str):
                match source:
                    case "local":
                        payne.install_project(test_data / f"{name}-{version}", locked=False)
                    case "remote":
                        payne.install_package(name, version, locked=False)
                    case _:
                        assert False

            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir, {"payne_test_data": "http://localhost:8000/payne_test_data"})

            # Install foo 1.3.0
            install_app("foo", "1.3.0")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")

            # Install foo 1.3.1
            install_app("foo", "1.3.1")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")
            self.assert_app_valid(apps_dir, "foo", "1.3.1")

            # Install foo 1.3.2
            install_app("foo", "1.3.2")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1", "1.3.2"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1", "foo-1.3.2"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")
            self.assert_app_valid(apps_dir, "foo", "1.3.1")
            self.assert_app_valid(apps_dir, "foo", "1.3.2")

            # Run the scripts
            # Windows will automatically use the .exe
            # TODO factor out expected output
            assert process_output([bin_dir / "foo-1.3.0"]) == (
                "This is foo 1.3.0\nThis is bar 1.2.1\nThis is baz 1.1.1\n", "")
            assert process_output([bin_dir / "foo-1.3.1"]) == (
                "This is foo 1.3.1\nThis is bar 1.2.0\nThis is baz 1.1.1\n", "")
            assert process_output([bin_dir / "foo-1.3.2"]) == (
                "This is foo 1.3.2\nThis is bar 1.2.0\nThis is baz 1.1.0\n", "")

            # Uninstall foo 1.3.0
            payne.uninstall("foo", "1.3.0")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.1", "1.3.2"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.1", "foo-1.3.2"}
            self.assert_app_valid(apps_dir, "foo", "1.3.1")
            self.assert_app_valid(apps_dir, "foo", "1.3.2")

            # Uninstall foo 1.3.1
            payne.uninstall("foo", "1.3.1")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.2"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.2"}
            self.assert_app_valid(apps_dir, "foo", "1.3.2")

            # Uninstall foo 1.3.2
            payne.uninstall("foo", "1.3.2")
            assert self.installed_apps(apps_dir) == {}
            assert self.installed_scripts(bin_dir) == set()

    @pytest.mark.parametrize("source", ["local", "remote"])
    def test_install_locked(self, source):
        with TemporaryDirectory() as temp_dir:
            # TODO duplication
            def install_app(name: str, version: str):
                match source:
                    case "local":
                        payne.install_project(test_data / f"{name}-{version}", locked=True)
                    case "remote":
                        payne.install_package(name, version, locked=True)
                    case _:
                        assert False

            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            # TODO duplication of indices
            payne = Payne(apps_dir, bin_dir, {"payne_test_data": "http://localhost:8000/payne_test_data"})

            # Install foo 1.3.0
            install_app("foo", "1.3.0")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")

            # # Install foo 1.3.1
            # install_app("foo", "1.3.1")
            # assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1"}}
            # assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1"}
            # self.assert_app_valid(apps_dir, "foo", "1.3.0")
            # self.assert_app_valid(apps_dir, "foo", "1.3.1")
            #
            # # Install foo 1.3.2
            # install_app("foo", "1.3.2")
            # assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1", "1.3.2"}}
            # assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1", "foo-1.3.2"}
            # self.assert_app_valid(apps_dir, "foo", "1.3.0")
            # self.assert_app_valid(apps_dir, "foo", "1.3.1")
            # self.assert_app_valid(apps_dir, "foo", "1.3.2")

            # Run the scripts
            # Windows will automatically use the .exe
            # Locked means that all versions use bar 1.2.0 and baz 1.1.0
            assert process_output([bin_dir / "foo-1.3.0"]) == (
                "This is foo 1.3.0\nThis is bar 1.2.0\nThis is baz 1.1.0\n", "")
            # assert process_output([bin_dir / "foo-1.3.1"]) == (
            #     "This is foo 1.3.1\nThis is bar 1.2.0\nThis is baz 1.1.0\n", "")
            # assert process_output([bin_dir / "foo-1.3.2"]) == (
            #     "This is foo 1.3.2\nThis is bar 1.2.0\nThis is baz 1.1.0\n", "")

    # Cannot install sup with locked dependencies because it has no lockfile
    @pytest.mark.parametrize("locked", [False])
    def test_install_local(self, locked):
        with TemporaryDirectory() as temp_dir:
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir, {"payne_test_data": "http://localhost:8000/payne_test_data"})

            # Install sup 2.1.0
            payne.install_project(test_data / "sup-2.1.0", locked=locked)
            assert self.installed_apps(apps_dir) == {"sup": {"2.1.0"}}
            assert self.installed_scripts(bin_dir) == {"sup-2.1.0"}
            self.assert_app_valid(apps_dir, "sup", "2.1.0")

            assert process_output([bin_dir / "sup-2.1.0"]) == (
                "This is sup 2.1.0\n", "")
