import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import tomllib

from cyclopts import App

app = App()


@app.command
def install(*, from_: Path):
    apps_dir = Path.home() / ".local" / "share" / "payne" / "apps"  # TODO better
    bin_dir = Path.home() / ".local" / "bin"

    print(f"Apps directory: {apps_dir}")
    print(f"Bin directory:  {bin_dir}")

    pyproject_toml = from_ / "pyproject.toml"

    pyproject = tomllib.loads(pyproject_toml.read_text())

    assert "version" not in pyproject.get("dynamic", [])
    project_name = pyproject["project"]["name"]
    project_version = pyproject["project"]["version"]

    app_dir = apps_dir / project_name / project_version

    print(f"Install {project_name} {project_version} from {from_}")

    bin_files = []

    with TemporaryDirectory() as temp_dir:
        uv = shutil.which("uv")
        command = [
            uv,
            "tool",
            "install",
            "--from", from_,
            project_name,
        ]
        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(app_dir)
        env["UV_TOOL_BIN_DIR"] = str(temp_dir)
        env["PATH"] = os.pathsep.join([env["PATH"], temp_dir])
        subprocess.call(command, env=env)

        for bin_file in Path(temp_dir).iterdir():
            bin_file: Path
            stem_with_version = f"{bin_file.stem}-{project_version}"
            name_with_version = bin_file.with_stem(stem_with_version).name
            bin_target_file = bin_dir / name_with_version
            shutil.move(bin_file, bin_target_file)
            bin_files.append(bin_target_file)

    metadata = {
        "bin_files": [str(bin_file) for bin_file in bin_files],
    }

    metadata_file = app_dir / "payne_app.json"
    metadata_file.write_text(json.dumps(metadata))

    # TODO roll back if it fails


@app.command
def uninstall(package_name: str, version: str):
    apps_dir = Path.home() / ".local" / "share" / "payne" / "apps"  # TODO better
    bin_dir = Path.home() / ".local" / "bin"

    print(f"Apps directory: {apps_dir}")
    print(f"Bin directory:  {bin_dir}")

    app_dir = apps_dir / package_name / version

    print(f"Uninstall {package_name} {version}")

    metadata_file = app_dir / "payne_app.json"
    metadata = json.loads(metadata_file.read_text())
    bin_files = [Path(bin_file) for bin_file in metadata["bin_files"]]

    for bin_file in bin_files:
        bin_file.unlink(missing_ok=True)

    with TemporaryDirectory() as temp_dir:
        uv = shutil.which("uv")
        command = [
            uv,
            "tool",
            "uninstall",
            package_name
        ]
        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(app_dir)
        env["UV_TOOL_BIN_DIR"] = str(temp_dir)
        subprocess.call(command, env=env)


@app.command
def list_():
    apps_dir = Path.home() / ".local" / "share" / "payne" / "apps"  # TODO better

    for app_dir in apps_dir.iterdir():
        app_name = app_dir.name
        for version_dir in app_dir.iterdir():
            app_version = version_dir.name
            print(f"{app_name} {app_version}")

            metadata_file = version_dir / "payne_app.json"
            metadata = json.loads(metadata_file.read_text())
            bin_files = [Path(bin_file) for bin_file in metadata["bin_files"]]

            for bin_file in bin_files:
                print(f"  - {bin_file.name}")


if __name__ == "__main__":
    sys.exit(app())
