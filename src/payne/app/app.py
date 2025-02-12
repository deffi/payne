from collections.abc import Iterator
from functools import cached_property
import json
from pathlib import Path
import shutil
from typing import Self

from payne.app import AppMetadata
from payne.project import Project
from payne import Installer
from payne.util.path import is_empty
from payne.util.temp_file import TemporaryDirectory
from payne.package import Package


class App:
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

    # TODO don't we need extra index URLs here so we know where to get dependencies?
    def install_from_local(self, project: Project, bin_dir: Path, locked: bool):
        with TemporaryDirectory() as temp_bin_dir:
            Installer().install_project(project, self.app_dir, temp_bin_dir, locked)

            scripts = self._install_scripts(temp_bin_dir, bin_dir)

            metadata = AppMetadata()
            metadata.scripts.extend(scripts)
            self.write_metadata(metadata)

    def corresponding_package(self) -> Package:
        return Package(self.name, self.version)

    # TODO very similar to install_From_local
    def install_from_remote(self, bin_dir: Path, locked: bool, extra_index_urls: list[str] | None = None):
        with TemporaryDirectory() as temp_bin_dir:
            # TODO should not be self.corresponding_package?
            Installer().install_from_remote(self.corresponding_package(), self.app_dir, temp_bin_dir, locked, extra_index_urls)

            scripts = self._install_scripts(temp_bin_dir, bin_dir)

            metadata = AppMetadata()
            metadata.scripts.extend(scripts)
            self.write_metadata(metadata)

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
