from functools import cached_property
import json
from pathlib import Path
from typing import TYPE_CHECKING

from payne import AppMetadata

if TYPE_CHECKING:
    from payne import Payne


class App:
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

    @cached_property
    def metadata_file(self) -> Path:
        return self.app_dir / "payne_app.json"

    def write_metadata(self, metadata: AppMetadata):
        self.metadata_file.write_text(json.dumps(metadata.dump()))

    def read_metadata(self) -> AppMetadata:
        metadata_file = self.app_dir / "payne_app.json"
        data = json.loads(metadata_file.read_text())
        return AppMetadata.parse(data)

    def script_file_name(self, original: Path) -> str:
        stem_with_version = f"{original.stem}-{self._version}"
        return original.with_stem(stem_with_version).name
