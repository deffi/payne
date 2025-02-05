from functools import cached_property
from pathlib import Path
import shutil


from payne import Uv, App, Pyproject


class Payne:
    def __init__(self):
        ...

    @cached_property
    def apps_dir(self):
        return Path.home() / ".local" / "share" / "payne" / "apps"  # TODO better

    @cached_property
    def bin_dir(self):
        return Path.home() / ".local" / "bin"

    @cached_property
    def uv_binary(self) -> Path:
        return Path(shutil.which("uv"))  # TODO better

    def status(self):
        print(f"Apps directory: {self.apps_dir}")
        print(f"Bin directory:  {self.bin_dir}")

    def install_from_local(self, source_path: Path):
        pyproject = Pyproject.load(source_path / "pyproject.toml")
        app = App(self, pyproject.name(), pyproject.version())

        if app.is_installed():
            # TODO allow reinstall
            # TODO allow treating this as a failure
            # TODO factor out "{app.name} {app.version}"
            print(f"{app.name} {app.version} is already installed")
        else:
            print(f"Install {app.name} {app.version} from {source_path}")
            app.install(source_path, self.bin_dir, self.uv_binary)

        # TODO roll back if it fails (e.g., script already exists)

    def uninstall(self, package_name: str, version: str):
        app = App(self, package_name, version)

        if app.is_installed():
            print(f"Uninstall {package_name} {version}")
            app.uninstall(self.uv_binary)
        else:
            print(f"{package_name} {version} is not installed")

    def list_(self):
        for app in App.installed_apps(self):
            print(f"{app.name} {app.version}")
            app_metadata = app.read_metadata()

            for script in app_metadata.scripts:
                print(f"  - {script.name}")
