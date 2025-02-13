from collections.abc import Iterator
from functools import cached_property
from pathlib import Path
import shutil


from payne.app import App
from payne.project import Project
from payne.package import Package
from payne.util.path import is_empty


class Payne:
    # TODO get rid of defaults
    def __init__(
            self,
            apps_dir: Path = Path.home() / ".local" / "share" / "payne" / "apps",  # TODO better
            bin_dir: Path = Path.home() / ".local" / "bin",  # TODO better
            ):
        self._apps_dir = apps_dir
        self._bin_dir = bin_dir

    @cached_property
    def apps_dir(self):
        return self._apps_dir

    @cached_property
    def bin_dir(self):
        return self._bin_dir

    @cached_property
    def uv_binary(self) -> Path:
        return Path(shutil.which("uv"))  # TODO better

    def _app_dir(self, name: str, version: str) -> Path:
        return self.apps_dir / name / version

    def _installed_apps(self) -> Iterator[App]:
        if self.apps_dir.exists():
            for app_dir in self.apps_dir.iterdir():
                for version_dir in app_dir.iterdir():
                    yield App(version_dir, app_dir.name, version_dir.name)

    def status(self):
        print(f"Apps directory: {self.apps_dir}")
        print(f"Bin directory:  {self.bin_dir}")

    def install_project(self, source_path: Path, locked: bool = False):  # TODO remove default
        project = Project(source_path)
        app = App(self._app_dir(project.name(), project.version()), project.name(), project.version())

        if app.is_installed():
            # TODO allow reinstall
            # TODO allow treating this as a failure
            # TODO factor out "{app.name} {app.version}"
            print(f"{app.name} {app.version} is already installed")
        else:
            print(f"Install {app.name} {app.version} from {project.root}")
            app.install_project(project, self.bin_dir, locked)

        # TODO roll back if it fails (e.g., script already exists)

    def install_package(self, name: str, version: str, locked: bool = False,
                        extra_index_urls: list[str] | None = None):  # TODO remove default
        package = Package(name, version)
        app = App(self._app_dir(name, version), name, version)

        if app.is_installed():
            # TODO duplication with install_from_local
            print(f"{app.name} {app.version} is already installed")
        else:
            print(f"Install {app.name} {app.version}")
            app.install_package(package, self.bin_dir, locked, extra_index_urls)

    def uninstall(self, name: str, version: str):
        app = App(self._app_dir(name, version), name, version)

        if app.is_installed():
            print(f"Uninstall {name} {version}")
            app.uninstall()

            # TODO factor out self.(directory that contains the app dirs for the individual versions)
            if is_empty(self._apps_dir / app.name):
                (self._apps_dir / app.name).rmdir()

        else:
            print(f"{name} {version} is not installed")

    def list_(self):
        for app in self._installed_apps():
            print(f"{app.name} {app.version}")
            app_metadata = app.read_metadata()

            for script in app_metadata.scripts:
                print(f"  - {script.name}")
