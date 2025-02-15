from pathlib import Path
from typing import Self


class DistMetadata:
    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def parse(cls, text: str) -> Self:
        data = {}
        for line in text.splitlines():
            key, value = line.split(": ", maxsplit=1)  # TODO what if a line doesn't have ": "?
            data[key] = value

        return cls(data)

    @classmethod
    def load(cls, file: Path) -> Self:
        return cls.parse(file.read_text())

    def name(self):
        return self._data["Name"]

    def version(self) -> str:
        return self._data["Version"]
