import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import pytest

from payne import Payne

from fixtures.index_server import index_server
from dirs import test_data
from util import child_names


class TestPayneLocal:
    def test_install_from_local_free(self):
        with TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            apps_dir = temp_dir / "apps"
            bin_dir = temp_dir / "bin"

            payne = Payne(apps_dir, bin_dir)

            # TODO this variable should be independent of uv
            os.environ["UV_INDEX"] = "payne_test_data=http://localhost:8000/payne_test_data"
            payne.install_from_local(test_data / "foo-1.3.0")

            assert child_names(apps_dir) == ["foo"]
            assert child_names(apps_dir / "foo") == ["1.3.0"]
            assert (apps_dir / "foo" / "1.3.0" / "payne_app.json").is_file()
            assert (apps_dir / "foo" / "1.3.0" / "foo").is_dir()

            assert child_names(bin_dir) == ["foo-1.3.0.exe"]  # TODO windows-specific

            # Run the script
            try:
                result = subprocess.run(
                    [bin_dir / "foo-1.3.0.exe"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                    universal_newlines=True,
                    check=True,
                )
                assert result.stdout == "This is foo 1.3.0\nThis is bar 1.2.1\nThis is baz 1.1.1\n"
                assert result.stderr == ""
            except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)  # TODO to stderr? (all instances)
                raise
