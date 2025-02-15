from pathlib import Path
import sys

from cyclopts import App

from payne import Payne
from payne.exceptions import AppVersionAlreadyInstalled

app = App()


@app.command
def status():
    Payne().status()


@app.command
def install(
        name: str | None = None,
        version: str | None = None,
        /, *,
        from_: Path | None = None,
        locked: bool = True,
        reinstall: bool = False,
        index: list[str] | None = None):  # TODO indices alias index?

    package_indices = dict(i.split("=", 1) for i in (index or ""))

    try:
        match name, version, from_:
            case n, v, None:
                Payne(package_indices=package_indices).install_package(n, v, locked=locked, reinstall=reinstall)
            case None, None, f:
                Payne(package_indices=package_indices).install_project(f, locked=locked, reinstall=reinstall)
            case _:
                print("Either name and version or --from have to be specified")
    except AppVersionAlreadyInstalled as e:
        print(e)


@app.command
def uninstall(package_name: str, version: str):
    Payne().uninstall(package_name, version)


@app.command
def list_():
    Payne().list_()


if __name__ == "__main__":
    sys.exit(app())
