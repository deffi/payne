import os
from pathlib import Path

from payne import Payne
from payne.util.file_system import TemporaryDirectory

import pytest

from common import test_data, test_data_index_url_files
from utils import child_names, process_output


class TestPayne:
    @staticmethod
    def assert_app_valid(apps_dir: Path, name: str, version: str):
        assert (apps_dir / name)                                     .is_dir()   # app group dir
        assert (apps_dir / name / version)                           .is_dir()   # app dir
        assert (apps_dir / name / version / "payne_app-version.json").is_file()  # metadata
        assert (apps_dir / name / version / name)                    .is_dir()   # venv
        assert (apps_dir / name / version / name / "pyvenv.cfg")     .is_file()  # venv metadata

    @staticmethod
    def installed_apps(app_dir: Path) -> dict[str, set[str]]:
        return {name: child_names(app_dir / name)
                for name in child_names(app_dir, missing_ok=True)}

    @staticmethod
    def installed_scripts(bin_dir: Path) -> set[str]:
        script_files = child_names(bin_dir)

        # On Windows, all script names must end with .exe and we remove that
        if os.name == "nt":
            assert all(script_file.endswith(".exe") for script_file in script_files)
            script_files = {script_file[:-4] for script_file in script_files}

        return script_files

    @pytest.mark.parametrize("source", ["project", "package"])
    def test_install_uninstall(self, source):
        with TemporaryDirectory() as temp_dir:
            def install_app(name: str, version: str):
                match source:
                    case "project":
                        payne.install_project(test_data / f"{name}-{version}", locked=False, reinstall=False)
                    case "package":
                        payne.install_package(name, version, locked=False, reinstall=False)
                    case _:
                        assert False

            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir, {"payne_test_data": test_data_index_url_files})

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

    @pytest.mark.parametrize("source", ["project", "package"])
    def test_install_locked(self, source):
        with TemporaryDirectory() as temp_dir:
            # TODO duplication
            def install_app(name: str, version: str):
                match source:
                    case "project":
                        payne.install_project(test_data / f"{name}-{version}", locked=True, reinstall=False)
                    case "package":
                        payne.install_package(name, version, locked=True, reinstall=False)
                    case _:
                        assert False

            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            # TODO duplication of indices
            payne = Payne(apps_dir, bin_dir, {"payne_test_data": test_data_index_url_files})

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

    # Cannot install sup or dyn with locked dependencies because they have no
    # lockfiles (TODO dyn does now)
    @pytest.mark.parametrize("locked", [False])
    @pytest.mark.parametrize("name, version", [
        ("sup", "2.1.0"),
        ("dyn", "3.1.0"),
    ])
    def test_install_project(self, locked, name, version):
        with TemporaryDirectory() as temp_dir:
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir, {"payne_test_data": test_data_index_url_files})

            payne.install_project(test_data / f"{name}-{version}", locked=locked, reinstall=False)
            assert self.installed_apps(apps_dir) == {name: {version}}
            assert self.installed_scripts(bin_dir) == {f"{name}-{version}"}
            self.assert_app_valid(apps_dir, name, version)

            assert process_output([bin_dir / f"{name}-{version}"]) == (
                f"This is {name} {version}\n", "")
