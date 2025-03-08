from dataclasses import dataclass
from pathlib import Path
import sys

from cyclopts import App, Parameter

from payne import Payne, Config
from payne.exceptions import AppVersionAlreadyInstalled

app = App()


@Parameter(name="*")  # Flatten the namespace; i.e. option will be "--url" instead of "--common.url"
@dataclass
class Common:
    apps_dir: Path | None = None
    "Where apps are installed"

    bin_dir: Path | None = None
    "Where scripts are installed"

    uv: Path | None = None
    "Uv executable"

    # TODO indices alias index?
    index: list[str] | None = None
    "Extra package index, NAME=URL (can be specified multiple times)"

    def create_config(self):
        return Config.create(
            apps_dir=self.apps_dir,
            bin_dir=self.bin_dir,
            package_indices=dict(i.split("=", 1) for i in (self.index or [])),
            uv=self.uv,
        )


@app.command
def status(*, common: Common | None = None):
    with (common or Common()).create_config():
        Payne().status()


@app.command
def install(
        name: str | None = None,
        version: str | None = None,
        /, *,
        from_: Path | None = None,
        locked: bool = True,
        reinstall: bool = False,
        common: Common | None = None,
):
    with (common or Common()).create_config():
        try:
            match name, version, from_:
                case n, v, None:
                    Payne().install_package(n, v, locked=locked, reinstall=reinstall)
                case None, None, f:
                    Payne().install_project(f, locked=locked, reinstall=reinstall)
                case _:
                    print("Either name and version or --from have to be specified")
        except AppVersionAlreadyInstalled as e:
            print(e)


@app.command
def uninstall(package_name: str, version: str, common: Common | None = None):
    with (common or Common()).create_config():
        Payne().uninstall(package_name, version)


@app.command
def list_(common: Common | None = None):
    with (common or Common()).create_config():
        Payne().list_()


if __name__ == "__main__":
    sys.exit(app())
