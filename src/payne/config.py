from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import os


@dataclass
class Config:
    apps_dir: Path
    bin_dir: Path
    package_indices: dict[str, str]
    uv: str

    def __enter__(self):
        global _config
        assert _config is None
        _config = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _config
        _config = None

    @staticmethod
    def _default_apps_dir() -> Path:
        # TODO better
        return Path.home() / ".local" / "share" / "payne" / "apps"

    @staticmethod
    def _default_bin_dir() -> Path:
        # TODO better
        return Path.home() / ".local" / "bin"

    @staticmethod
    def _value[T](explicit: T | None, environment: tuple[str, Callable[[str], T]] | None, default: T) -> T:
        if explicit is not None:
            return explicit

        if environment is not None:
            environment_variable, converter = environment
            if environment_variable in os.environ:
                return converter(os.environ[environment_variable])

        return default

    @classmethod
    def create(
            cls,
            apps_dir: Path | None,
            bin_dir: Path | None,
            package_indices: dict[str, str],
            uv: str | None,
    ):
        print(os.environ)
        return Config(
            apps_dir=cls._value(apps_dir, ("PAYNE_APPS_DIR", Path), cls._default_apps_dir()),
            bin_dir=cls._value(bin_dir, ("PAYNE_BIN_DIR", Path), cls._default_bin_dir()),
            package_indices=cls._value(package_indices, None, {}),  # TODO allow environment
            uv=cls._value(uv, ("PAYNE_UV", str), "uv"),
        )


_config: Config | None = None


def config() -> Config:
    assert _config is not None
    return _config
