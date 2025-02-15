from abc import ABC, abstractmethod
from pathlib import Path

from payne.project import Project
from payne.package import Package


InstallSource = Project | Package


class Installer(ABC):
    def __init__(self, package_indices: dict[str, str]):
        self._package_indices = package_indices

    @property
    def package_indices(self) -> dict[str, str]:
        return self._package_indices

    @abstractmethod
    def install_project(self, project: Project, target_dir: Path, bin_dir: Path, *, constraints: Path | None):
        ...

    @abstractmethod
    def install_package(self, package: Package, target_dir: Path, bin_dir: Path, *, constraints: Path | None):
        ...

    def install(self, source: InstallSource, target_dir: Path, bin_dir: Path, *, constraints: Path | None):
        match source:
            case Project():
                self.install_project(source, target_dir, bin_dir, constraints=constraints)
            case Package():
                self.install_package(source, target_dir, bin_dir, constraints=constraints)
            case _:
                raise TypeError(f"Unknown installation source: {source}")
