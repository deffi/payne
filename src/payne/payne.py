from functools import cached_property
from pathlib import Path
import shutil


from payne.app import App, AppsDir
from payne.downloader import Downloader
from payne.exceptions import AppVersionAlreadyInstalled
from payne.installer import UvInstaller
from payne.project import Project
from payne.package import Package
from payne.util.file_system import TemporaryDirectory


class Payne:
    # TODO get rid of defaults
    def __init__(
            self,
            apps_dir: Path = Path.home() / ".local" / "share" / "payne" / "apps",  # TODO better
            bin_dir: Path = Path.home() / ".local" / "bin",  # TODO better
            package_indices: dict[str, str] = None,  # TODO remove default
            ):
        self._apps_dir = AppsDir(apps_dir)
        self._bin_dir = bin_dir
        self._package_indices = package_indices or {}

    @property
    def apps_dir(self) -> AppsDir:
        return self._apps_dir

    @cached_property
    def bin_dir(self):
        return self._bin_dir

    @cached_property
    def uv_binary(self) -> Path:
        return Path(shutil.which("uv"))  # TODO better

    def status(self):
        print(f"Apps directory: {self.apps_dir.root}")
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
            app = App(self.apps_dir.app_version_dir(name, version), name, version)
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
                        sdist = Downloader().download_and_unpack_sdist(package, download_dir, self._package_indices)
                        temp_project = Project(sdist)
                        frontend = temp_project.build_frontend()
                        # TODO handle not found
                        frontend.export_constraints(constraints_file)
                    case _:
                        raise TypeError(f"Unhandled source: {source}")

            # We're now ready to install the app
            match source:
                case Project() as project:
                    print(f"Install {app.name} {app.version} from {project.root}")
                case Package():
                    print(f"Install {app.name} {app.version}")
                case _:
                    raise TypeError(f"Unhandled source: {source}")

            installer = UvInstaller(self._package_indices)

            with self.apps_dir.cleanup_app_dir(app.name):
                app.install(installer, source, self.bin_dir, constraints_file)

    def install_project(self, root: Path, *, locked: bool, reinstall: bool):
        self.install(Project(root), locked=locked, reinstall=reinstall)

    def install_package(self, name: str, version: str, *, locked: bool, reinstall: bool):
        self.install(Package(name, version), locked=locked, reinstall=reinstall)

    def uninstall(self, name: str, version: str):
        app = App(self.apps_dir.app_version_dir(name, version), name, version)

        if app.is_installed():
            print(f"Uninstall {name} {version}")

            with self.apps_dir.cleanup_app_dir(name):
                app.uninstall()

        else:
            print(f"{name} {version} is not installed")

    def list_(self):
        for app in self.apps_dir.installed_apps():
            print(f"{app.name} {app.version}")
            app_metadata = app.read_metadata()

            for script in app_metadata.scripts:
                print(f"  - {script.name}")
