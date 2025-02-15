from pathlib import Path
import shlex
import subprocess

from payne.project.build_frontend import Frontend


class UvFrontend(Frontend):
    def export_constraints(self, constraints_file: Path):
        constraints_file.parent.mkdir(parents=True, exist_ok=True)
        assert not constraints_file.exists()

        args = [
            "uv",
            "export",
            "--project", self._root,
            "--no-dev",
            "--no-emit-project",
            "--frozen",
            "--no-header",
            "--no-hashes",
            "--output-file", constraints_file,
        ]

        print(f"Calling uv: {shlex.join(map(str, args))}")
        subprocess.run(args, check=True)

        assert constraints_file.is_file()
