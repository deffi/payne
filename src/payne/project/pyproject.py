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

    def version(self) -> str:
        # TODO better check
        assert "version" not in self._data.get("dynamic", [])
        return self._data["project"]["version"]
