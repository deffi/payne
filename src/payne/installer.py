import os
from pathlib import Path
import shlex
import subprocess

from payne.project import Project
from payne.download import download_and_unpack_sdist
from payne.util.temp_file import TemporaryDirectory
from payne.package import Package


class Installer:
    """Uses uv"""

    # TODO accept Project
    def _uv_tool_install_project(self, path: Path, package: str, requirements: Path | None, target_dir: Path, tool_bin_dir: Path):
        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        if requirements:
            constraints = ["--constraints", requirements]
        else:
            constraints = []

        args = [
            "uv",
            "tool",
            "install",
            "--reinstall",
            "--from", path,
            *constraints,
            package,
        ]

        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(target_dir)
        env["UV_TOOL_BIN_DIR"] = str(tool_bin_dir)

        print(f"Calling uv: {shlex.join(map(str, args))}")
        return subprocess.run(args, env=env, check=True)

    # TOOD very similar to _uv_tool_install_project
    def _uv_tool_install_remote(self, package: Package, requirements: Path | None, target_dir: Path, tool_bin_dir: Path):
        if requirements:
            constraints = ["--constraints", requirements]
        else:
            constraints = []

        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        args=[
            "uv",
            "tool",
            "install",
            "--reinstall",
            *constraints,
            package.requirement_specifier(),
        ]

        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(target_dir)
        env["UV_TOOL_BIN_DIR"] = str(tool_bin_dir)

        print(f"Calling uv: {shlex.join(map(str, args))}")
        return subprocess.run(args, env=env, check=True)

    def install_project(self, project: Project, app_dir: Path, bin_dir: Path, locked: bool):
        # TODO only used if locked
        with TemporaryDirectory() as temp_dir:
            if locked:
                requirements_file = temp_dir / "requirements.txt"
                project.create_requirements_from_lock_file(requirements_file)
                self._uv_tool_install_project(project.root, project.name(), requirements=requirements_file, target_dir=app_dir, tool_bin_dir=bin_dir)
            else:
                self._uv_tool_install_project(project.root, project.name(), requirements=None, target_dir=app_dir, tool_bin_dir=bin_dir)

    # TODO similar to install_project
    def install_from_remote(self, package: Package, app_dir: Path, bin_dir: Path, locked: bool, extra_index_urls: list[str] | None = None):
        # TODO only used if locked
        with TemporaryDirectory() as temp_dir:
            download_dir = temp_dir / "download"
            requirements_file = temp_dir / "requirements.txt"

            if locked:
                project = Project(download_and_unpack_sdist(package, download_dir, extra_index_urls))
                project.create_requirements_from_lock_file(requirements_file)
                self._uv_tool_install_remote(package, requirements=requirements_file, target_dir=app_dir, tool_bin_dir=bin_dir)
            else:
                self._uv_tool_install_remote(package, requirements=None, target_dir=app_dir, tool_bin_dir=bin_dir)
