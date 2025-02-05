from collections.abc import Iterator
from functools import cached_property
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Self

from payne import AppMetadata, Uv

if TYPE_CHECKING:
    from payne import Payne


class App:
    # TODO remove the reference to Payne, store apps_dir instead
    def __init__(self, payne: "Payne", name: str, version: str):
        self._payne = payne
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
        return self._payne.apps_dir / self._name / self._version

    # Scripts ##################################################################

    def _script_file_name(self, original: Path) -> str:
        stem_with_version = f"{original.stem}-{self._version}"
        return original.with_stem(stem_with_version).name

    def _install_scripts(self, source_dir: Path, bin_dir: Path) -> Iterator[Path]:
        for source_script in source_dir.iterdir():
            script = bin_dir / self._script_file_name(source_script)
            print(f"Installing script {source_script.name} to {script}")
            shutil.move(source_script, script)
            yield script

    # Installation #############################################################

    def is_installed(self) -> bool:
        return self.app_dir.exists()

    @classmethod
    def installed_apps(cls, payne: "Payne") -> Iterator[Self]:
        apps_dir = payne.apps_dir

        if apps_dir.exists():
            for app_dir in apps_dir.iterdir():
                app_name = app_dir.name
                for version_dir in app_dir.iterdir():
                    yield cls(payne, app_name, version_dir.name)

    def install(self, source_path: Path, bin_dir: Path, uv_binary: Path):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            uv = Uv(uv_binary, tool_dir=self.app_dir, tool_bin_dir=temp_dir)
            uv.tool_install_local(source_path, self.name, extra_path=[temp_dir])
            scripts = self._install_scripts(temp_dir, bin_dir)

            metadata = AppMetadata()
            metadata.scripts.extend(scripts)
            self.write_metadata(metadata)

    def uninstall(self, uv_binary: Path):
        metadata = self.read_metadata()

        for script in metadata.scripts:
            print(f"Uninstall script {script}")
            script.unlink(missing_ok=True)

        # TODO remove metadata file

        # Use a temporary tool bin dir for uv so it doesn't uninstall scripts
        # that we didn't install
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            uv = Uv(uv_binary, tool_dir=self.app_dir, tool_bin_dir=temp_dir)
            uv.tool_uninstall(self.name)

        # TODO remove app dir if it still exists, and output a warning if it
        #  isn't empty

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
