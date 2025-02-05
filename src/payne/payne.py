from collections.abc import Iterator
from functools import cached_property
import json
from importlib.metadata import metadata
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import tomllib


from payne import Uv, App, Pyproject, AppMetadata


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

    # TODO is_installed, install_from_local, uninstall: should be in App
    def is_installed(self, app: App) -> bool:
        return app.app_dir.exists()

    def install_scripts(self, app: App, source_dir: Path) -> Iterator[Path]:
        for source_script in source_dir.iterdir():
            script = self.bin_dir / app.script_file_name(source_script)
            print(f"Installing script {source_script.name} to {script}")
            shutil.move(source_script, script)
            yield script

    def install_from_local(self, source_path: Path):
        pyproject = Pyproject.load(source_path / "pyproject.toml")
        app = App(self, pyproject.name(), pyproject.version())

        if self.is_installed(app):
            # TODO allow reinstall
            # TODO allow treating this as a failure
            # TODO factor out "{app.name} {app.version}"
            print(f"{app.name} {app.version} is already installed")
        else:
            print(f"Install {app.name} {app.version} from {source_path}")

            with TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                uv = Uv(self.uv_binary, tool_dir=app.app_dir, tool_bin_dir=temp_dir)
                uv.tool_install_local(source_path, app.name, extra_path=[temp_dir])
                scripts = self.install_scripts(app, temp_dir)

                app_metadata = AppMetadata()
                app_metadata.scripts.extend(scripts)
                app.write_metadata(app_metadata)

        # TODO roll back if it fails (e.g., script already exists)

    def uninstall(self, package_name: str, version: str):
        app = App(self, package_name, version)

        print(f"Uninstall {package_name} {version}")

        app_metadata = app.read_metadata()

        for script in app_metadata.scripts:
            print(f"Uninstall script {script}")
            script.unlink(missing_ok=True)

        # TODO remove metadata file

        # Use a temporary tool bin dir for uv so it doesn't uninstall scripts
        # that we didn't install
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            uv = Uv(Path(shutil.which("uv")), tool_dir=app.app_dir, tool_bin_dir=temp_dir)
            uv.tool_uninstall(package_name)

        # TODO remove app dir if it still exists, and output a warning if it
        #  isn't empty

    def list_(self):
        if self.apps_dir.exists():
            for app_dir in self.apps_dir.iterdir():
                app_name = app_dir.name
                for version_dir in app_dir.iterdir():
                    app = App(self, app_name, version_dir.name)

                    print(f"{app.name} {app.version}")
                    app_metadata = app.read_metadata()

                    for script in app_metadata.scripts:
                        print(f"  - {script.name}")
