from collections.abc import Iterator
from functools import cached_property
from pathlib import Path
import shutil


from payne.app import App
from payne.downloader import Downloader
from payne.exceptions import AppVersionAlreadyInstalled
from payne.installer import UvInstaller
from payne.project import Project
from payne.package import Package
from payne.util.path import is_empty
from payne.util.file_system import TemporaryDirectory, safe_ensure_exists


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

    def install(self, source: Project | Package, *, locked: bool, reinstall: bool):
        with TemporaryDirectory() as temp_dir:
            # First, we need to determine the name and version so we know where
            # to install it (unless overridden, which isn't implemented yet).
            match source:
                case Project() as project:
                    # This might have to build the project
                    name = project.name()
                    version = project.version()
                case Package() as package:
                    name = package.name
                    version = package.version
                case _:
                    raise TypeError(f"Unhandled source: {source}")

            # Check whether the ap is already installed so we avoid extra work
            # if we decide to stop
            app = App(self._app_dir(name, version), name, version)
            if app.is_installed():
                if reinstall:
                    app.uninstall()
                else:
                    raise AppVersionAlreadyInstalled(app)

            # For a locked install, we have to determine the constraints
            constraints_file = temp_dir / "constraints.txt"
            if locked:
                match source:
                    case Project() as project:
                        frontend = project.build_frontend()
                        # TODO handle not found
                        frontend.export_constraints(constraints_file)
                    case Package() as package:
                        download_dir = temp_dir / "download"
                        project = Project(Downloader().download_and_unpack_sdist(package, download_dir, self._package_indices))
                        frontend = project.build_frontend()
                        # TODO handle not found
                        frontend.export_constraints(constraints_file)
                    case _:
                        raise TypeError(f"Unhandled source: {source}")

            # We're now ready to install the app
            match source:
                case Project() as project:
                    print(f"Install {app.name} {app.version} from {project.root}")
                case Package() as package:
                    print(f"Install {app.name} {app.version}")
                case _:
                    raise TypeError(f"Unhandled source: {source}")

            installer = UvInstaller(self._package_indices)

            # TODO factor out self.(directory that contains the app dirs for the individual versions)
            with safe_ensure_exists(self._apps_dir / app.name):
                app.install(installer, source, self.bin_dir, constraints_file)

    def install_project(self, root: Path, *, locked: bool, reinstall: bool):
        self.install(Project(root), locked=locked, reinstall=reinstall)

    def install_package(self, name: str, version: str, *, locked: bool, reinstall: bool):
        package = Package(name, version)
        self.install(Package(name, version), locked=locked, reinstall=reinstall)

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
