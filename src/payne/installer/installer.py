import os
from pathlib import Path
import shlex
import subprocess

from payne.project import Project
from payne.package import Package


InstallSource = Project | Package


class Installer:
    """Uses uv"""

    @staticmethod
    def _uv_tool_install(source_args: list[str], target_dir: Path, bin_dir: Path, *, constraints: Path | None, package_indices: dict[str, str]):
        if constraints and constraints.exists() and constraints.read_text().strip():
            constraints_args = ["--constraints", constraints]
        else:
            constraints_args = []

        index_args = []
        for name, url in package_indices.items():
            index_args.append("--index")
            index_args.append(f"{name}={url}")

        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        args = [
            "uv",
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

    def install_project(self, project: Project, target_dir: Path, bin_dir: Path, *, constraints: Path | None, package_indices: dict[str, str]):
        self._uv_tool_install(
            ["--from", project.root, project.name()],
            target_dir,
            bin_dir,
            constraints=constraints,
            package_indices=package_indices,
        )

    def install_package(self, package: Package, target_dir: Path, bin_dir: Path, *, constraints: Path | None, package_indices: dict[str, str]):
        self._uv_tool_install(
            [package.requirement_specifier()],
            target_dir,
            bin_dir,
            constraints=constraints,
            package_indices=package_indices,
        )

    def install(self, source: InstallSource, target_dir: Path, bin_dir: Path, *, constraints: Path | None, package_indices: dict[str, str]):
        match source:
            case Project():
                self.install_project(source, target_dir, bin_dir, constraints=constraints, package_indices=package_indices)
            case Package():
                self.install_package(source, target_dir, bin_dir, constraints=constraints, package_indices=package_indices)
            case _:
                raise TypeError(f"Unknown installation source: {source}")
