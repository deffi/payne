import os
from pathlib import Path

from payne import Payne
from payne.util.file_system import TemporaryDirectory
from payne.exceptions import FrontendNotRecognized

import pytest

from common import test_data, test_data_index_url_files
from utils import child_names, process_output

from expected_output import expected_output


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

    @pytest.mark.parametrize("locked", [False, True])
    @pytest.mark.parametrize("source", ["package", "project"])
    def test_install_uninstall(self, source, locked):
        with TemporaryDirectory() as temp_dir:
            def install_app(name: str, version: str):
                match source:
                    case "project":
                        payne.install_project(test_data / f"{name}-{version}", locked=locked, reinstall=False)
                    case "package":
                        payne.install_package(name, version, locked=locked, reinstall=False)
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
            assert process_output([bin_dir / "foo-1.3.0"]) == (expected_output("foo", "1.3.0", locked, "foo"), "")
            assert process_output([bin_dir / "foo-1.3.1"]) == (expected_output("foo", "1.3.1", locked, "foo"), "")
            assert process_output([bin_dir / "foo-1.3.2"]) == (expected_output("foo", "1.3.2", locked, "foo"), "")

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

    @pytest.mark.parametrize("source", ["package", "project"])
    @pytest.mark.parametrize("name, version, locked, script", [
        # baz 1.1.0
        ("baz", "1.1.0", False, "baz"),
        ("baz", "1.1.0", True , "baz"),
        # baz 1.1.1
        ("baz", "1.1.1", False, "baz"),
        ("baz", "1.1.1", True , "baz"),
        # bar 1.2.0: latest baz
        ("bar", "1.2.0", False, "bar"),
        ("bar", "1.2.0", True , "bar"),
        # bar 1.2.1: latest baz
        ("bar", "1.2.1", False, "bar"),
        ("bar", "1.2.1", True , "bar"),
        # foo 1.3.0: latest bar, latest baz
        ("foo", "1.3.0", False, "foo"),
        ("foo", "1.3.0", True , "foo"),
        # foo 1.3.1: bar pinned, latest baz
        ("foo", "1.3.1", False, "foo"),
        ("foo", "1.3.1", True , "foo"),
        # foo 1.3.2: bar pinned, baz pinned
        ("foo", "1.3.2", False, "foo"),
        ("foo", "1.3.2", True , "foo"),
        # sup 2.1.0
        ("sup", "2.1.0", False, "sup"),
        # (Cannot install `sup` locked because it has no lockfile)
        # dyn 3.1.0
        ("dyn", "3.1.0", False, "dyn"),
        ("dyn", "3.1.0", True , "dyn"),
        # dep 4.1.0: pygments constrained
        ("dep", "4.1.0", False, "dep"),
        ("dep", "4.1.0", True , "dep"),
        # dep 4.1.1: pygments pinned
        ("dep", "4.1.1", False, "dep"),
        ("dep", "4.1.1", True , "dep"),
    ])
    def test_install_app(self, name, version, script, source, locked):
        with TemporaryDirectory() as temp_dir:
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir, {"payne_test_data": test_data_index_url_files})

            match source:
                case "project":
                    payne.install_project(test_data / f"{name}-{version}", locked=locked, reinstall=False)
                case "package":
                    payne.install_package(name, version, locked=locked, reinstall=False)
                case _:
                    assert False

            assert self.installed_apps(apps_dir) == {name: {version}}
            assert self.installed_scripts(bin_dir) == {f"{script}-{version}"}
            self.assert_app_valid(apps_dir, name, version)

            expected = expected_output(name, version, locked, script)
            assert process_output([bin_dir / f"{script}-{version}"]) == (expected, "")

    @pytest.mark.parametrize("source", ["package", "project"])
    @pytest.mark.parametrize("name, version, locked", [
        ("sup", "2.1.0", True),
    ])
    def test_install_app_no_frontend(self, name, version, source, locked):
        with TemporaryDirectory() as temp_dir:
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir, {"payne_test_data": test_data_index_url_files})

            with pytest.raises(FrontendNotRecognized):
                match source:
                    case "project":
                        payne.install_project(test_data / f"{name}-{version}", locked=locked, reinstall=False)
                    case "package":
                        payne.install_package(name, version, locked=locked, reinstall=False)
                    case _:
                        assert False
