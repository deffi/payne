from dataclasses import dataclass


@dataclass(frozen=True)
class Metadata:
    name: str
    version: str
