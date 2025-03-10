from pathlib import Path

import pytest

from payne import Config
from payne.config import config
from payne.util.file_system import TemporaryDirectory


class TestConfig:
    def test_create_explicit(self):
        with TemporaryDirectory() as temp_dir:
            c = Config(
                apps_dir=temp_dir / "app",
                bin_dir=temp_dir / "bin",
                package_indices={},
                uv="UV",
            )

            assert c.apps_dir == temp_dir / "app"
            assert c.bin_dir == temp_dir / "bin"
            assert c.package_indices == {}
            assert c.uv == "UV"

    def test_context(self):
        c = Config(
            apps_dir=Path(),
            bin_dir=Path(),
            package_indices={},
            uv="uv",
        )

        with pytest.raises(AssertionError):
            config()

        for _ in range(2):
            with c:
                assert config() is c

            with pytest.raises(AssertionError):
                assert config() is None
