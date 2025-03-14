import tomllib

import pytest

from common import test_data_index_url_files
from payne.downloader import Downloader
from payne.package import Package
from payne.util.file_system import TemporaryDirectory


class TestDownload:
    @pytest.mark.slow
    @pytest.mark.parametrize("package", [
        Package("payne", "0.1.0"),
        Package("foo", "1.3.1"),
    ])
    def test_download(self, package):
        with TemporaryDirectory() as temp_dir:
            # TODO factor out URL
            downloader = Downloader()
            target = downloader.download_and_unpack_sdist(package, temp_dir, package_indices={"payne_test_data": test_data_index_url_files})

            pyproject_toml = target / "pyproject.toml"
            assert pyproject_toml.is_file()
            pyproject = tomllib.loads(pyproject_toml.read_text())
            assert pyproject.get("project", {}).get("name", None) == package.name
            assert pyproject.get("project", {}).get("version", None) == package.version

            pkg_info_file = target / "PKG-INFO"
            assert pkg_info_file.is_file()
            pkg_info = pkg_info_file.read_text().splitlines()
            assert f"Name: {package.name}" in pkg_info
            assert f"Version: {package.version}" in pkg_info
