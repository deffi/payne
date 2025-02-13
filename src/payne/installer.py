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

    def _uv_tool_install(self, source: Project | Package, requirements: Path | None, target_dir: Path, bin_dir: Path):
        if requirements:
            constraints = ["--constraints", requirements]
        else:
            constraints = []

        match source:
            case Project() as project:
                source_args = ["--from", project.root, project.name()]
            case Package() as package:
                source_args = [package.requirement_specifier()]
            case _:
                raise TypeError(f"Unrecognized source: {source}")

        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        args = [
            "uv",
            "tool",
            "install",
            "--reinstall",
            *constraints,
            *source_args,
        ]

        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(target_dir)
        env["UV_TOOL_BIN_DIR"] = str(bin_dir)

        print(f"Calling uv: {shlex.join(map(str, args))}")
        return subprocess.run(args, env=env, check=True)

    def install_project(self, project: Project, app_dir: Path, bin_dir: Path, locked: bool):
        if locked:
            with TemporaryDirectory() as temp_dir:
                requirements_file = temp_dir / "requirements.txt"
                project.create_requirements_from_lock_file(requirements_file)
                self._uv_tool_install(project, requirements=requirements_file, target_dir=app_dir, bin_dir=bin_dir)
        else:
            self._uv_tool_install(project, requirements=None, target_dir=app_dir, bin_dir=bin_dir)

    # TODO similar to install_project
    def install_from_remote(self, package: Package, app_dir: Path, bin_dir: Path, locked: bool, extra_index_urls: list[str] | None = None):
        if locked:
            with TemporaryDirectory() as temp_dir:
                download_dir = temp_dir / "download"

                requirements_file = temp_dir / "requirements.txt"
                project = Project(download_and_unpack_sdist(package, download_dir, extra_index_urls))
                project.create_requirements_from_lock_file(requirements_file)
                self._uv_tool_install(package, requirements=requirements_file, target_dir=app_dir, bin_dir=bin_dir)
        else:
            self._uv_tool_install(package, requirements=None, target_dir=app_dir, bin_dir=bin_dir)
