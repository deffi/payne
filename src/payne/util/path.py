from pathlib import Path


def is_empty(directory: Path):
    assert directory.is_dir()
    return not any(directory.iterdir())
