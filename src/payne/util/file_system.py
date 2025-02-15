from pathlib import Path
import tempfile


class TemporaryDirectory(tempfile.TemporaryDirectory):
    """Same as tempfile.TemporaryDirectory, but returns Path"""
    def __enter__(self):
        return Path(super().__enter__())
