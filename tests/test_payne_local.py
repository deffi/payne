import os
from pathlib import Path
from tempfile import TemporaryDirectory

from payne import Payne

# noinspection PyUnresolvedReferences
from fixtures.index_server import index_server
from dirs import test_data
from util import child_names, process_output


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

    def test_install_from_local_uninstall(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir)
            # TODO this variable should be independent of uv
            os.environ["UV_INDEX"] = "payne_test_data=http://localhost:8000/payne_test_data"

            # Install foo 1.3.0
            payne.install_from_local(test_data / "foo-1.3.0")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")

            # Install foo 1.3.1
            payne.install_from_local(test_data / "foo-1.3.1")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")
            self.assert_app_valid(apps_dir, "foo", "1.3.1")

            # Install foo 1.3.2
            payne.install_from_local(test_data / "foo-1.3.2")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1", "1.3.2"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1", "foo-1.3.2"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")
            self.assert_app_valid(apps_dir, "foo", "1.3.1")
            self.assert_app_valid(apps_dir, "foo", "1.3.2")

            # Run the scripts
            # Windows will automatically use the .exe
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

    def test_install_from_remote_uninstall(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir)
            # TODO this variable should be independent of uv
            os.environ["UV_INDEX"] = "payne_test_data=http://localhost:8000/payne_test_data"

            # Install foo 1.3.0
            payne.install_from_remote("foo", "1.3.0")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")

            # Install foo 1.3.1
            payne.install_from_remote("foo", "1.3.1")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")
            self.assert_app_valid(apps_dir, "foo", "1.3.1")

            # Install foo 1.3.2
            payne.install_from_remote("foo", "1.3.2")
            assert self.installed_apps(apps_dir) == {"foo": {"1.3.0", "1.3.1", "1.3.2"}}
            assert self.installed_scripts(bin_dir) == {"foo-1.3.0", "foo-1.3.1", "foo-1.3.2"}
            self.assert_app_valid(apps_dir, "foo", "1.3.0")
            self.assert_app_valid(apps_dir, "foo", "1.3.1")
            self.assert_app_valid(apps_dir, "foo", "1.3.2")

            # Run the scripts
            # Windows will automatically use the .exe
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
