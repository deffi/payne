from pathlib import Path

from unearth import PackageFinder

from payne.package import Package


class Downloader:
    @staticmethod
    def download_and_unpack_sdist(package: Package, target: Path, package_indices: dict[str, str]) -> Path:
        """Downloads and unpacks a source distribution package

        One might assume that this functionality would be available in pip. But
        while there is `pip download`, it seems like that will not just download but
        also (partly?) build the package - apparently, for reasons[1].

        At the same time, it seems like the `unearth` package duplicates just the
        finding and downloading part of pip, so we'll use that instead.

        [1] https://discuss.python.org/t/pip-download-just-the-source-packages-no-building-no-metadata-etc/4651/8
        """

        finder = PackageFinder(no_binary=[package.name])

        for url in package_indices.values():
            finder.add_index_url(url)

        # TODO handle not found
        result = finder.find_best_match(package.requirement_specifier())
        best_package = result.best

        # Unearth only has combined downloading and unpacking. Since we will have to
        # unpack it anyway, that's fine.
        # TODO verify that this works with a proxy and a locally installed
        #  certificate. If it doesn't, we may have to download `best_package.link`
        # in another way and unpack it ourselves.
        return finder.download_and_unpack(best_package.link, target)
