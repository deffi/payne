import os
from pathlib import Path
import shlex
import shutil
import subprocess

from payne.config import config
from payne.project import Project
from payne.package import Package
from payne.installer import Installer


class UvInstaller(Installer):
    def _uv_tool_install(self, source_args: list[str], target_dir: Path, bin_dir: Path, constraints: Path | None):
        if constraints and constraints.exists() and constraints.read_text().strip():
            constraints_args = ["--constraints", constraints]
        else:
            constraints_args = []

        index_args = []
        for name, url in self.package_indices.items():
            index_args.append("--index")
            index_args.append(f"{name}={url}")

        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        args = [
            shutil.which(config().uv),
            "tool",
            "install",
            "--reinstall",
            *index_args,
            *constraints_args,
            *source_args,
        ]

        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(target_dir)
        env["UV_TOOL_BIN_DIR"] = str(bin_dir)
        # Avoid picking up local configuration
        env["UV_INDEX"] = ""
        env["UV_EXTRA_INDEX_URL"] = ""
        # Avoid warning about (temporary) bin dir not being on PATH
        env["PATH"] = os.pathsep.join([env["PATH"], str(bin_dir)])

        print(f"Calling uv: {shlex.join(map(str, args))}")
        return subprocess.run(args, env=env, check=True)

    def install_project(self, project: Project, target_dir: Path, bin_dir: Path, constraints: Path | None):
        self._uv_tool_install(
            ["--from", project.root, project.metadata().name],
            target_dir,
            bin_dir,
            constraints=constraints,
        )

    def install_package(self, package: Package, target_dir: Path, bin_dir: Path, constraints: Path | None):
        self._uv_tool_install(
            [package.requirement_specifier()],
            target_dir,
            bin_dir,
            constraints=constraints,
        )
