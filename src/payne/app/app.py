from collections.abc import Iterator
from functools import cached_property
import json
from pathlib import Path
import shutil

from payne.app import AppMetadata
from payne.installer import Installer, InstallSource
from payne.util.temp_file import TemporaryDirectory


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

    def install(self, source: InstallSource, bin_dir: Path, constraints_file: Path, package_indices: dict[str, str]):
        with TemporaryDirectory() as temp_dir:
            temp_bin_dir = temp_dir / "bin"
            Installer(package_indices).install(source, self.root, temp_bin_dir, constraints=constraints_file)

            scripts = self._install_scripts(temp_bin_dir, bin_dir)

            metadata = AppMetadata()
            metadata.scripts.extend(scripts)
            self.write_metadata(metadata)

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
