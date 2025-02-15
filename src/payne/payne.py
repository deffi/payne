from collections.abc import Iterator
from functools import cached_property
from pathlib import Path
import shutil


from payne.app import App
from payne.downloader import Downloader
from payne.installer import UvInstaller
from payne.project import Project
from payne.package import Package
from payne.util.path import is_empty
from payne.util.temp_file import TemporaryDirectory


class Payne:
    # TODO get rid of defaults
    def __init__(
            self,
            apps_dir: Path = Path.home() / ".local" / "share" / "payne" / "apps",  # TODO better
            bin_dir: Path = Path.home() / ".local" / "bin",  # TODO better
            package_indices: dict[str, str] = None,  # TODO remove default
            ):
        self._apps_dir = apps_dir
        self._bin_dir = bin_dir
        self._package_indices = package_indices or {}

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

    # Installing:
    # * If installing locked: determine constraints
    #   * If installing a package: get the sdist as a temporary project
    #   * Identify the project frontend
    #   * Export constraints
    # * If installing an (actual, not temporary) project: determine the version
    #   * Try to read it from pyproject.toml
    #   * If there is no pyproject or the version is dynamic
    #     * Build the sdist (partly?) to get the metadata
    # * Install (from the original source)

    def _get_constraints(self, root: Path):
        # Identify the project frontend
        # Export constraints
        ...

    def install_project(self, root: Path, *, locked: bool):
        project = Project(root)

        name = project.name()  # Might have to build it?
        version = project.version()  # Might have to build it

        app = App(self._app_dir(name, version), name, version)
        if app.is_installed():
            # TODO allow reinstall
            # TODO allow treating this as a failure
            # TODO factor out "{app.name} {app.version}"
            print(f"{app.name} {app.version} is already installed")
        else:
            with TemporaryDirectory() as temp_dir:
                constraints_file = temp_dir / "constraints.txt"

                if locked:
                    frontend = project.build_frontend()
                    # TODO handle not found
                    frontend.export_constraints(constraints_file)

                print(f"Install {app.name} {app.version} from {project.root}")
                installer = UvInstaller(self._package_indices)
                app.install(installer, project, self.bin_dir, constraints_file)
                # TODO roll back if it fails (e.g., script already exists)

    def install_package(self, name: str, version: str, *, locked: bool):
        package = Package(name, version)
        app = App(self._app_dir(name, version), name, version)

        if app.is_installed():
            # TODO duplication with install_from_local
            print(f"{app.name} {app.version} is already installed")
        else:
            with TemporaryDirectory() as temp_dir:
                constraints_file = temp_dir / "constraints.txt"

                if locked:
                    download_dir = temp_dir / "download"
                    project = Project(Downloader().download_and_unpack_sdist(package, download_dir, self._package_indices))
                    frontend = project.build_frontend()
                    # TODO handle not found
                    frontend.export_constraints(constraints_file)

                print(f"Install {app.name} {app.version}")
                installer = UvInstaller(self._package_indices)
                app.install(installer, package, self.bin_dir, constraints_file)

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
