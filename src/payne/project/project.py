from functools import cached_property, cache
from pathlib import Path
import re
import shlex
import subprocess
import tarfile
from tkinter.font import names

import build
import build.env
import uv

from payne.project import Pyproject
from payne.project.build_frontend import Frontend
from payne.util.file_system import TemporaryDirectory


class Project:
    """Assumes that the project uses uv"""

    def __init__(self, root: Path):
        self._root = root

        self._name = None
        self._version = None

    @property
    def root(self):
        return self._root

    def _load_metadata(self):
        pyproject_toml = self._root / "pyproject.toml"
        if pyproject_toml.exists():
            pyproject = Pyproject.load(pyproject_toml)
            self._name = pyproject.name()
            self._version = pyproject.version()
        else:
            # No pyproject.toml, seems like we have to build the project
            # TODO refactor
            # TODO can we just get the metadata without building the whole package?
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
                        pkg_info_names = [name for name in sdist.getnames() if re.fullmatch(r"[^/]+/PKG-INFO", name, re.IGNORECASE)]
                        print(pkg_info_names)
                        assert len(pkg_info_names) == 1
                        metadata = sdist.extractfile(pkg_info_names[0]).read().decode().splitlines()
                        for line in metadata:
                            key, value = line.split(": ", maxsplit=1)
                            # TODO better error handling
                            if key == "Name":
                                self._name = value
                            elif key == "Version":
                                self._version = value

        assert self._name is not None
        assert self._version is not None

    def name(self):
        if self._name is None:
            self._load_metadata()

        return self._name

    def version(self):
        if self._version is None:
            self._load_metadata()

        return self._version

    @cache
    def build_frontend(self) -> Frontend | None:
        return Frontend.create(self.root)
