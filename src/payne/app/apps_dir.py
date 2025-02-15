from collections.abc import Iterator
from contextlib import contextmanager, suppress

from pathlib import Path

from payne.app import App
from payne.util.path import is_empty


class AppsDir:
    def __init__(self, root: Path):
        self._root = root

    @property
    def root(self) -> Path:
        return self._root

    def installed_apps(self) -> Iterator[App]:
        if self.root.exists():
            for app_dir in self.root.iterdir():
                for app_version_dir in app_dir.iterdir():
                    yield App(app_version_dir, app_dir.name, app_version_dir.name)

    def app_dir(self, name: str) -> Path:
        return self.root / name

    @contextmanager
    def cleanup_app_dir(self, name: str) -> Iterator[Path]:
        dir_ = self.app_dir(name)

        try:
            dir_.mkdir(parents=True, exist_ok=True)
            yield self.app_dir(name)
        finally:
            with suppress(BaseException):
                if dir_.exists() and is_empty(dir_):
                    dir_.rmdir()
                if self.root.exists() and is_empty(self.root):
                    self.root.rmdir()

    def app_version_dir(self, name: str, version: str) -> Path:
        return self.app_dir(name) / version
