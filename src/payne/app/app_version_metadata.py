import hashlib
from pathlib import Path
from typing import Literal

from attrs import define, field
import attrs.validators
from cattrs import structure, unstructure

schema = {
    "name": "payne.app-version-metadata",
    "version": "1.0",
}


def create_hash(data: bytes) -> str:
    name = "sha1"
    hash_ = hashlib.new(name, data).hexdigest()
    return f"{name}:{hash_}"


def hash_matches(data: bytes, hash_: str) -> bool:
    name, hash_ = hash_.split(":", maxsplit=1)
    data_hash = hashlib.new(name, data).hexdigest()
    return data_hash == hash_

# @define
# class ProjectSource:
#     path: Path
#
# @define
# class PackageSource:
#     name: str
#     version: str


@define
class Script:
    file: Path
    script_name: str
    hash: str


# TODO cf. uv-receipt.toml
@define
class AppVersionMetadata:
    # source: ProjectSource | PackageSource
    scripts: list[Script] = field(factory=list)



    def dump(self):
        data = unstructure(self)
        data = {"_schema": schema, **data}
        return data

    @classmethod
    def load(cls, data: dict):
        data = dict(data)

        if data["_schema"] != schema:
            raise ValueError("Schema doesn't match")
        del data["_schema"]

        return structure(data, cls)
