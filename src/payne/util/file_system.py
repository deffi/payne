from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile

from payne.util.path import is_empty


class TemporaryDirectory(tempfile.TemporaryDirectory):
    """Same as tempfile.TemporaryDirectory, but returns Path"""
    def __enter__(self) -> Path:
        return Path(super().__enter__())


@contextmanager
def safe_create(directory: Path):
    directory.mkdir()

    try:
        yield directory
    except BaseException:
        print(f"Cleaning up {directory}")
        shutil.rmtree(directory)
        raise


@contextmanager
def safe_ensure_exists(directory: Path):
    to_create = []

    if directory.exists():
        assert directory.is_dir()
    else:
        to_create.insert(0, directory)

        for parent in directory.parents:
            if parent.exists():
                assert parent.is_dir()
                break
            else:
                to_create.insert(0, parent)

    for d in to_create:
        d.mkdir(parents=False, exist_ok=False)

    try:
        yield directory
    except BaseException:
        for d in reversed(to_create):
            if is_empty(d):
                d.rmdir()

        raise
