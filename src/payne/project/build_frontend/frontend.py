from abc import ABC, abstractmethod
from pathlib import Path


class Frontend(ABC):
    def __init__(self, root: Path):
        self._root = root

    @property
    def root(self) -> Path:
        return self._root

    @abstractmethod
    def export_constraints(self, constraints_file: Path) -> None:
        ...

    @staticmethod
    def create(root: Path) -> "Frontend | None":
        from payne.project.build_frontend import UvFrontend

        if (root / "uv.lock").exists():
            return UvFrontend(root)
        else:
            return None
