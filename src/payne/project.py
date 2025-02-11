from functools import cached_property
from pathlib import Path
import shlex
import subprocess

from payne import Pyproject


class Project:
    """Assumes that the project uses uv"""

    def __init__(self, root: Path):
        self._root = root

    @property
    def root(self):
        return self._root

    @cached_property
    def _pyproject(self) -> Pyproject:
        return Pyproject.load(self._root / "pyproject.toml")

    def name(self):
        return self._pyproject.name()

    def version(self):
        return self._pyproject.version()

    def _lock_file(self) -> Path:
        return self._root / "uv.lock"

    def has_lock_file(self) -> bool:
        return self._lock_file().exists()

    def create_requirements_from_lock_file(self, requirements_file: Path):
        args = [
            "uv",
            "export",
            "--project", self._root,
            "--no-dev",
            "--no-emit-project",
            "--frozen",
            "--no-header",
            "--no-hashes",
            "--output-file", requirements_file,
        ]

        print(f"Calling uv: {shlex.join(map(str, args))}")
        subprocess.run(args, check=True)
