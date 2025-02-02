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

    def status(self):
        print(f"Apps directory: {self.apps_dir}")
        print(f"Bin directory:  {self.bin_dir}")

    def install_from_local(self, source_path: Path):
        pyproject = Pyproject.load(source_path / "pyproject.toml")

        project_name = pyproject.name()
        project_version = pyproject.version()

        app = App(self, project_name, project_version)

        print(f"Install {project_name} {project_version} from {source_path}")

        app_metadata = AppMetadata()

        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            uv = Uv(Path(shutil.which("uv")), tool_dir=app.app_dir, tool_bin_dir=temp_dir)
            uv.tool_install_local(source_path, project_name, extra_path=[temp_dir])

            for temp_script in Path(temp_dir).iterdir():
                script = self.bin_dir / app.script_file_name(temp_script)
                shutil.move(temp_script, script)
                app_metadata.scripts.append(script)

        app.write_metadata(app_metadata)

        # TODO roll back if it fails

    def uninstall(self, package_name: str, version: str):
        app = App(self, package_name, version)

        print(f"Uninstall {package_name} {version}")

        app_metadata = app.read_metadata()

        for script in app_metadata.scripts:
            script.unlink(missing_ok=True)

        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            uv = Uv(Path(shutil.which("uv")), tool_dir=app.app_dir, tool_bin_dir=temp_dir)
            uv.tool_uninstall(package_name)

    def list_(self):
        for app_dir in self.apps_dir.iterdir():
            app_name = app_dir.name
            for version_dir in app_dir.iterdir():
                app_version = version_dir.name
                print(f"{app_name} {app_version}")

                app = App(self, app_name, app_version)
                app_metadata = app.read_metadata()

                for script in app_metadata.scripts:
                    print(f"  - {script.name}")
