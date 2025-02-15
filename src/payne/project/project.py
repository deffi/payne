from functools import cache
from pathlib import Path
import re
import tarfile

import build
import build.env

from payne.project import Pyproject, Metadata, DistMetadata
from payne.project.build_frontend import Frontend
from payne.util.file_system import TemporaryDirectory


class Project:
    """Assumes that the project uses uv"""

    def __init__(self, root: Path):
        self._root = root

    @property
    def root(self):
        return self._root

    def _read_metadata_from_pyproject_toml(self) -> Metadata:
        pyproject = Pyproject.load(self._root / "pyproject.toml")
        return Metadata(pyproject.name(), pyproject.version())

    def _build_and_read_metadata(self) -> Metadata:
        # TODO refactor
        with TemporaryDirectory() as temp_dir:
            with build.env.DefaultIsolatedEnv(installer="uv") as env:
                builder = build.ProjectBuilder.from_isolated_env(env, self.root)
                env.install(builder.build_system_requires)
                # TODO required?
                env.install(builder.get_requires_for_build("sdist", {}))
                # TOOD consider instead:
                #   * builder.prepare("wheel", temp_dir) -> path to dist_info dir (as string)
                #   * dist_info/METADATA
                #   * dist_info/entry_points.txt -> we get the script names
                sdist_file = Path(builder.build("sdist", temp_dir, {}))
                with tarfile.open(sdist_file, 'r:*') as sdist:
                    print(sdist.getnames())
                    pkg_info_names = [name for name in sdist.getnames() if
                                      re.fullmatch(r"[^/]+/PKG-INFO", name, re.IGNORECASE)]
                    print(pkg_info_names)
                    assert len(pkg_info_names) == 1
                    dist_metadata_text = sdist.extractfile(pkg_info_names[0]).read().decode()
                    dist_metadata = DistMetadata.parse(dist_metadata_text)
                    return Metadata(dist_metadata.name(), dist_metadata.version())

    def _prepare_and_read_metadata(self) -> Metadata:
        # TODO refactor
        with TemporaryDirectory() as temp_dir:
            with build.env.DefaultIsolatedEnv(installer="uv") as env:
                builder = build.ProjectBuilder.from_isolated_env(env, self.root)
                env.install(builder.build_system_requires)
                # TODO required?
                # env.install(builder.get_requires_for_build("sdist", {}))
                dist_info = Path(builder.prepare("wheel", temp_dir))
                dist_metadata = DistMetadata.load(dist_info / "METADATA")
                # We also get dist_info/entry_points.txt
                return Metadata(dist_metadata.name(), dist_metadata.version())

    @cache
    def metadata(self) -> Metadata:
        try:
            return self._read_metadata_from_pyproject_toml()
        except FileNotFoundError:
            # No pyproject.toml, seems like we have to prepare/build the project
            # TODO which one is better? Building an sdist or preparing for a wheel?

            # return self._build_and_read_metadata()
            return self._prepare_and_read_metadata()

    @cache
    def build_frontend(self) -> Frontend | None:
        return Frontend.create(self.root)
