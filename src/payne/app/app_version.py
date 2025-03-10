from collections.abc import Iterator
from functools import cached_property
import json
import os
from pathlib import Path
import shutil

from payne.app import AppVersionMetadata
from payne.app import app_version_metadata
from payne.installer import Installer, InstallSource
from payne.util.file_system import TemporaryDirectory, safe_create


class AppVersion:
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

    def _install_scripts(self, source_dir: Path, bin_dir: Path) -> Iterator[app_version_metadata.Script]:
        bin_dir.mkdir(parents=True, exist_ok=True)

        for source_script in source_dir.iterdir():
            script = bin_dir / self._script_file_name(source_script)
            print(f"Installing script {source_script.name} to {script}")
            shutil.move(source_script, script)
            yield app_version_metadata.Script(
                script,
                source_script.name,
                app_version_metadata.create_hash(script.read_bytes()))

        # TODO factor out
        search_path = os.environ["PATH"].split(os.pathsep)
        search_path = [p.lower() for p in search_path]
        if str(bin_dir).lower() not in search_path:
            print(f"Warning: the bin directory is not in the PATH: {bin_dir}")

    # Installation #############################################################

    def is_installed(self) -> bool:
        return self.root.exists()

    def install(self, installer: Installer, source: InstallSource, bin_dir: Path, constraints_file: Path):
        with safe_create(self.root) as root:
            with TemporaryDirectory() as temp_dir:
                temp_bin_dir = temp_dir / "bin"
                installer.install(source, root, temp_bin_dir, constraints=constraints_file)

                scripts = list(self._install_scripts(temp_bin_dir, bin_dir))
                metadata = AppVersionMetadata(scripts)
                self.write_metadata(metadata)

    def uninstall(self):
        # TODO handle: script not found (others must still be deleted)
        # TODO handle: metadata could not be read
        try:
            metadata = self.read_metadata()

            for script in metadata.scripts:
                print(f"Uninstall script {script}")
                # TODO verify the hash
                script.file.unlink(missing_ok=True)

        except BaseException:
            # TODO better
            print("Error while uninstalling, uninstall may be incomplete")

        finally:
            shutil.rmtree(self.root)

    # Metadata #################################################################

    @cached_property
    def metadata_file(self) -> Path:
        return self.root / "payne_app-version.json"

    def write_metadata(self, metadata: AppVersionMetadata):
        self.metadata_file.write_text(json.dumps(metadata.dump()))

    def read_metadata(self) -> AppVersionMetadata:
        data = json.loads(self.metadata_file.read_text())
        return AppVersionMetadata.load(data)
