from pathlib import Path
import sys

from cyclopts import App

from payne import Payne

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
        index: list[str] | None = None):  # TODO indices alias index?

    package_indices = dict(i.split("=", 1) for i in index)

    match name, version, from_:
        case n, v, None:
            Payne(package_indices=package_indices).install_package(n, v, locked=locked)
        case None, None, f:
            Payne(package_indices=package_indices).install_project(f, locked=locked)
        case _:
            print("Either name and version or --from have to be specified")


@app.command
def uninstall(package_name: str, version: str):
    Payne().uninstall(package_name, version)


@app.command
def list_():
    Payne().list_()


if __name__ == "__main__":
    sys.exit(app())
