from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Package:
    name: str
    version: str

    def __post_init__(self):
        assert re.fullmatch(r'\d.*', self.version)

    def __str__(self):
        return f"{self.name} {self.version}"

    def requirement_specifier(self) -> str:
        return f"{self.name}=={self.version}"
