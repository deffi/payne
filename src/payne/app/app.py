from collections.abc import Iterator
from contextlib import contextmanager
from functools import cached_property
import json
from pathlib import Path
import shutil
from typing import Self

from payne.app import AppMetadata
from payne.download import download_and_unpack_sdist
from payne.project import Project
from payne import Installer
from payne.util.path import is_empty
from payne.util.temp_file import TemporaryDirectory
from payne.package import Package


class App:
    # TODO this should just take a root directly
    def __init__(self, apps_dir: Path, name: str, version: str):
        self._apps_dir = apps_dir
        self._name = name
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @cached_property
    def app_dir(self) -> Path:
        return self._apps_dir / self._name / self._version

    # Scripts ##################################################################

    def _script_file_name(self, original: Path) -> str:
        stem_with_version = f"{original.stem}-{self._version}"
        return original.with_stem(stem_with_version).name

    def _install_scripts(self, source_dir: Path, bin_dir: Path) -> Iterator[Path]:
        bin_dir.mkdir(parents=True, exist_ok=True)

        for source_script in source_dir.iterdir():
            script = bin_dir / self._script_file_name(source_script)
            print(f"Installing script {source_script.name} to {script}")
            shutil.move(source_script, script)
            yield script

    # Installation #############################################################

    def is_installed(self) -> bool:
        return self.app_dir.exists()

    @classmethod
    def installed_apps(cls, apps_dir: Path) -> Iterator[Self]:
        if apps_dir.exists():
            for app_dir in apps_dir.iterdir():
                app_name = app_dir.name
                for version_dir in app_dir.iterdir():
                    yield cls(apps_dir, app_name, version_dir.name)

    def _install_project(self, installer: Installer, project: Project, app_dir: Path, bin_dir: Path, locked: bool):
        if locked:
            with TemporaryDirectory() as temp_dir:
                requirements_file = temp_dir / "requirements.txt"
                project.create_requirements_from_lock_file(requirements_file)
                installer.install_project(project, requirements=requirements_file, target_dir=app_dir, bin_dir=bin_dir)
        else:
            installer.install_project(project, requirements=None, target_dir=app_dir, bin_dir=bin_dir)

    # TODO similar to install_project
    def _install_package(self, installer: Installer, package: Package, app_dir: Path, bin_dir: Path, locked: bool, extra_index_urls: list[str] | None = None):
        if locked:
            with TemporaryDirectory() as temp_dir:
                download_dir = temp_dir / "download"

                requirements_file = temp_dir / "requirements.txt"
                project = Project(download_and_unpack_sdist(package, download_dir, extra_index_urls))
                project.create_requirements_from_lock_file(requirements_file)
                installer.install_package(package, requirements=requirements_file, target_dir=app_dir, bin_dir=bin_dir)
        else:
            installer.install_package(package, requirements=None, target_dir=app_dir, bin_dir=bin_dir)

    @contextmanager
    def _install(self, bin_dir: Path):  # TODO annotate
        with TemporaryDirectory() as temp_bin_dir:
            yield temp_bin_dir

            scripts = self._install_scripts(temp_bin_dir, bin_dir)

            metadata = AppMetadata()
            metadata.scripts.extend(scripts)
            self.write_metadata(metadata)

    # TODO don't we need extra index URLs here so we know where to get dependencies?
    def install_project(self, project: Project, bin_dir: Path, locked: bool):
        with self._install(bin_dir) as temp_bin_dir:
            self._install_project(Installer(), project, self.app_dir, temp_bin_dir, locked)

    def install_package(self, package: Package, bin_dir: Path, locked: bool, extra_index_urls: list[str] | None = None):
        with self._install(bin_dir) as temp_bin_dir:
            self._install_package(Installer(), package, self.app_dir, temp_bin_dir, locked, extra_index_urls)

    def uninstall(self):
        metadata = self.read_metadata()

        for script in metadata.scripts:
            print(f"Uninstall script {script}")
            script.unlink(missing_ok=True)

        shutil.rmtree(self.app_dir)
        # TODO factor out self.(directory that contains the app dirs for the individual versions)
        # TODO factor out is_empty
        if is_empty(self._apps_dir / self._name):
            (self._apps_dir / self._name).rmdir()

    # Metadata #################################################################

    @cached_property
    def metadata_file(self) -> Path:
        return self.app_dir / "payne_app.json"

    def write_metadata(self, metadata: AppMetadata):
        self.metadata_file.write_text(json.dumps(metadata.dump()))

    def read_metadata(self) -> AppMetadata:
        metadata_file = self.app_dir / "payne_app.json"
        data = json.loads(metadata_file.read_text())
        return AppMetadata.parse(data)
