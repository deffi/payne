import os
from pathlib import Path
import shlex
import subprocess


class Uv:
    def __init__(self, binary: Path, tool_dir: Path | None, tool_bin_dir: Path | None):
        self._binary = binary
        self._tool_dir = tool_dir
        self._tool_bin_dir = tool_bin_dir

    def _run(self, uv_args: list[str | Path], /, extra_path: list[Path] = None):
        env = os.environ.copy()
        env["UV_TOOL_DIR"] = str(self._tool_dir)
        env["UV_TOOL_BIN_DIR"] = str(self._tool_bin_dir)

        if extra_path:
            env["PATH"] = os.pathsep.join([str(path) for path in extra_path] + [env["PATH"]])

        call_args = [self._binary, *uv_args]

        print(f"Calling uv: {shlex.join(map(str, call_args))}")
        return subprocess.check_call(call_args, env=env)

    def tool_install_local(self, path: Path, package: str, extra_path: list[Path] = None,
                           requirements: Path | None = None):  # TODO remove default
        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        if requirements:
            constraints = ["--constraints", requirements]
        else:
            constraints = []

        self._run([
            "tool",
            "install",
            "--reinstall",
            "--from", path,
            *constraints,
            package,
        ], extra_path=extra_path)

    def tool_install_remote(self, package: str, version: str, extra_path: list[Path] = None,
                            requirements: Path | None = None):  # TODO remove default
        package_spec = f"{package}=={version}"

        if requirements:
            constraints = ["--constraints", requirements]
        else:
            constraints = []

        # Re-install in case it's already installed and we missed it. Should
        # have raised an exception, but uv doesn't return an error code in this
        # case.
        self._run([
            "tool",
            "install",
            "--reinstall",
            *constraints,
            package_spec,
        ], extra_path=extra_path)

    def tool_uninstall(self, name: str, extra_path: list[Path] = None):
        self._run([
            "tool",
            "uninstall",
            name,
        ], extra_path=extra_path)

    # def export(self, project_path: Path, output_file: Path):
    #     return self._run([
    #         "export",
    #         "--project", project_path,
    #         "--no-dev",
    #         "--no-emit-project",
    #         "--frozen",
    #         "--no-header",
    #         "--no-hashes",
    #         "--output-file", output_file,
    #     ])
