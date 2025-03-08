from functools import cached_property
from pathlib import Path
import shutil


from payne.app import AppVersion, AppsDir
from payne.config import config
from payne.downloader import Downloader
from payne.exceptions import AppVersionAlreadyInstalled, FrontendNotRecognized
from payne.installer import UvInstaller
from payne.project import Project
from payne.package import Package
from payne.util.file_system import TemporaryDirectory


class Payne:
    def __init__(self):
        assert config() is not None

    @cached_property
    def apps_dir(self) -> AppsDir:
        return AppsDir(config().apps_dir)

    @staticmethod
    def status():
        print(f"Apps directory:  {config().apps_dir}")
        print(f"Bin directory:   {config().bin_dir}")
        print(f"Package indices: {config().package_indices}")  # TODO show as list
        print(f"Uv executable:   {config().uv}")  # TODO show resolved value

    def install(self, source: Project | Package, *, locked: bool, reinstall: bool):
        with TemporaryDirectory() as temp_dir:
            # First, we need to determine the name and version so we know where
            # to install it (unless overridden, which isn't implemented yet).
            match source:
                case Project() as project:
                    # This might have to build the project
                    name = project.metadata().name
                    version = project.metadata().version
                case Package() as package:
                    name = package.name
                    version = package.version
                case _:
                    raise TypeError(f"Unhandled source: {source}")

            # Check whether the app version is already installed so we avoid
            # extra work if we decide to stop
            app_version = AppVersion(self.apps_dir.app_version_dir(name, version), name, version)
            if app_version.is_installed():
                if reinstall:
                    app_version.uninstall()
                else:
                    raise AppVersionAlreadyInstalled(app_version)

            # For a locked install, we have to determine the constraints
            constraints_file = temp_dir / "constraints.txt"
            if locked:
                match source:
                    case Project() as project:
                        frontend = project.build_frontend()

                    case Package() as package:
                        download_dir = temp_dir / "download"
                        sdist = Downloader().download_and_unpack_sdist(package, download_dir, config().package_indices)
                        temp_project = Project(sdist)

                        frontend = temp_project.build_frontend()

                    case _:
                        raise TypeError(f"Unhandled source: {source}")

                if frontend is None:
                    raise FrontendNotRecognized(source)

                frontend.export_constraints(constraints_file)

            # We're now ready to install the app
            match source:
                case Project() as project:
                    print(f"Install {app_version.name} {app_version.version} from {project.root}")
                case Package():
                    print(f"Install {app_version.name} {app_version.version}")
                case _:
                    raise TypeError(f"Unhandled source: {source}")

            installer = UvInstaller(config().package_indices)

            with self.apps_dir.cleanup_app_dir(app_version.name):
                app_version.install(installer, source, config().bin_dir, constraints_file)

    def install_project(self, root: Path, *, locked: bool, reinstall: bool):
        self.install(Project(root), locked=locked, reinstall=reinstall)

    def install_package(self, name: str, version: str, *, locked: bool, reinstall: bool):
        self.install(Package(name, version), locked=locked, reinstall=reinstall)

    def uninstall(self, name: str, version: str):
        app_version = AppVersion(self.apps_dir.app_version_dir(name, version), name, version)

        if app_version.is_installed():
            print(f"Uninstall {name} {version}")

            with self.apps_dir.cleanup_app_dir(name):
                app_version.uninstall()

        else:
            print(f"{name} {version} is not installed")

    def list_(self):
        any_apps = False

        for app in self.apps_dir.installed_apps():
            any_apps = True
            print(f"{app.name} {app.version}")
            app_metadata = app.read_metadata()

            for script in app_metadata.scripts:
                print(f"  - {script.file.name}")

        if not any_apps:
            print("No apps installed")
