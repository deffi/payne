from pathlib import Path


def child_names(directory: Path) -> list[str]:
    return [child.name for child in directory.iterdir()]
