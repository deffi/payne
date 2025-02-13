import os
from pathlib import Path
import shlex
import subprocess

from payne.project import Project
from payne.util.temp_file import TemporaryDirectory
from payne.package import Package


class Installer:
    """Uses uv"""

    def _uv_tool_install(self, source_args: list[str], requirements: Path | None, target_dir: Path, bin_dir: Path):
        if requirements:
            constraints = ["--constraints", requirements]
        else:
            constraints = []

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

    def install_project(self, project: Project, requirements: Path | None, target_dir: Path, bin_dir: Path):
        self._uv_tool_install(["--from", project.root, project.name()], requirements, target_dir, bin_dir)

    def install_package(self, package: Package, requirements: Path | None, target_dir: Path, bin_dir: Path):
        self._uv_tool_install([package.requirement_specifier()], requirements, target_dir, bin_dir)
