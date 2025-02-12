from pathlib import Path


class AppMetadata:
    def __init__(self):
        self.scripts: list[Path] = []

    def dump(self):
        return {
            "scripts": [str(script) for script in self.scripts],
        }

    @classmethod
    def parse(cls, metadata: dict):
        result = cls()
        result.scripts = [Path(script) for script in metadata["scripts"]]
        return result

