from collections.abc import Iterator
from functools import cached_property
import json
from pathlib import Path
import shutil
from typing import Self

from payne.app import AppMetadata
from payne.downloader import Downloader
from payne.project import Project
from payne.installer import Installer
from payne.util.temp_file import TemporaryDirectory
from payne.package import Package


class App:
    def __init__(self, root: Path, name: str, version: str):
        self._root = root
        self._name = name
        self._version = version

    @property
    def root(self) -> Path:
        return self._root

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

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
        return self.root.exists()

    def _post_install(self, temp_bin_dir: Path, bin_dir: Path):
        scripts = self._install_scripts(temp_bin_dir, bin_dir)

        metadata = AppMetadata()
        metadata.scripts.extend(scripts)
        self.write_metadata(metadata)

    # TODO don't we need extra index URLs here so we know where to get dependencies?
    def install_project(self, project: Project, bin_dir: Path, locked: bool):
        with TemporaryDirectory() as temp_dir:
            if locked:
                constraints = temp_dir / "requirements.txt"
                project.create_requirements_from_lock_file(constraints)
            else:
                constraints = None

            temp_bin_dir = temp_dir / "bin"
            Installer().install_project(project, self.root, temp_bin_dir, constraints=constraints)
            self._post_install(temp_bin_dir, bin_dir)

    def install_package(self, package: Package, bin_dir: Path, locked: bool, extra_index_urls: list[str] | None = None):
        with TemporaryDirectory() as temp_dir:
            if locked:
                download_dir = temp_dir / "download"
                project = Project(Downloader().download_and_unpack_sdist(package, download_dir, extra_index_urls))

                constraints = temp_dir / "requirements.txt"
                project.create_requirements_from_lock_file(constraints)
            else:
                constraints = None

            temp_bin_dir = temp_dir / "bin"
            Installer().install_package(package, self.root, temp_bin_dir, constraints=constraints)
            self._post_install(temp_bin_dir, bin_dir)

    def uninstall(self):
        metadata = self.read_metadata()

        for script in metadata.scripts:
            print(f"Uninstall script {script}")
            script.unlink(missing_ok=True)

        shutil.rmtree(self.root)

    # Metadata #################################################################

    @cached_property
    def metadata_file(self) -> Path:
        return self.root / "payne_app.json"

    def write_metadata(self, metadata: AppMetadata):
        self.metadata_file.write_text(json.dumps(metadata.dump()))

    def read_metadata(self) -> AppMetadata:
        metadata_file = self.root / "payne_app.json"
        data = json.loads(metadata_file.read_text())
        return AppMetadata.parse(data)
