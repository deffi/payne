import os
from pathlib import Path
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

        return subprocess.call(call_args, env=env)

    def tool_install_local(self, path: Path, package: str, extra_path: list[Path] = None):
        self._run([
            "tool",
            "install",
            "--from", path,
            package,
        ], extra_path=extra_path)

    def tool_uninstall(self, name: str, extra_path: list[Path] = None):
        self._run([
            "tool",
            "uninstall",
            name,
        ], extra_path=extra_path)
