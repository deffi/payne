from pathlib import Path
import subprocess


def child_names(directory: Path, missing_ok: bool = False) -> set[str]:
    try:
        return {child.name for child in directory.iterdir()}
    except FileNotFoundError:
        if missing_ok:
            return set()
        else:
            raise


def process_output(args: list) -> tuple[str, str]:
    # Run the script
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            universal_newlines=True,
            check=True,
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)  # TODO to stderr? (all instances)
        raise
