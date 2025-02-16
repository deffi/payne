import tomllib
from pathlib import Path


class Pyproject:
    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def load(cls, file: Path):
        return cls(tomllib.loads(file.read_text()))

    def name(self):
        return self._data["project"]["name"]

    def is_dynamic_version(self) -> bool:
        return "version" in self._data["project"].get("dynamic", [])

    def static_version(self) -> str:
        assert not self.is_dynamic_version()
        return self._data["project"]["version"]
