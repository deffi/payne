from functools import cached_property
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from payne import Payne


class App:
    def __init__(self, payne: "Payne", name: str, version: str):
        self._payne = payne
        self._name = name
        self._version = version

    @cached_property
    def app_dir(self) -> Path:
        return self._payne.apps_dir / self._name / self._version

    @cached_property
    def metadata_file(self) -> Path:
        return self.app_dir / "payne_app.json"

    def write_metadata(self, metadata: dict):
        self.metadata_file.write_text(json.dumps(metadata))

    def read_metadata(self) -> dict:
        metadata_file = self.app_dir / "payne_app.json"
        return json.loads(metadata_file.read_text())

    def script_file_name(self, original: Path) -> str:
        stem_with_version = f"{original.stem}-{self._version}"
        return original.with_stem(stem_with_version).name
