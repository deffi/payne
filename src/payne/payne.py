from functools import cached_property
from pathlib import Path
import shutil


from payne import App, Project


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

    def status(self):
        print(f"Apps directory: {self.apps_dir}")
        print(f"Bin directory:  {self.bin_dir}")

    def install_from_local(self, source_path: Path, locked: bool = False):  # TODO remove default
        project = Project(source_path)
        app = App(self.apps_dir, project.name(), project.version())

        if app.is_installed():
            # TODO allow reinstall
            # TODO allow treating this as a failure
            # TODO factor out "{app.name} {app.version}"
            print(f"{app.name} {app.version} is already installed")
        else:
            print(f"Install {app.name} {app.version} from {project.root}")
            app.install_from_local(project, self.bin_dir, locked)

        # TODO roll back if it fails (e.g., script already exists)

    def install_from_remote(self, name: str, version: str, locked: bool = False,
                            extra_index_urls: list[str] | None = None):  # TODO remove default
        app = App(self.apps_dir, name, version)

        if app.is_installed():
            # TODO duplication with install_from_local
            print(f"{app.name} {app.version} is already installed")
        else:
            print(f"Install {app.name} {app.version}")
            app.install_from_remote(self.bin_dir, locked, extra_index_urls)

    def uninstall(self, package_name: str, version: str):
        app = App(self.apps_dir, package_name, version)

        if app.is_installed():
            print(f"Uninstall {package_name} {version}")
            app.uninstall(self.uv_binary)
        else:
            print(f"{package_name} {version} is not installed")

    def list_(self):
        for app in App.installed_apps(self.apps_dir):
            print(f"{app.name} {app.version}")
            app_metadata = app.read_metadata()

            for script in app_metadata.scripts:
                print(f"  - {script.name}")
