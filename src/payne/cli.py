from pathlib import Path
import sys
from typing import Annotated

from cyclopts import App, Parameter

from payne import Payne, Config
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
):
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
def uninstall(package_name: str, version: str):
    Payne().uninstall(package_name, version)


@app.command
def list_():
    Payne().list_()


@app.meta.default
def main_meta(
        *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
        apps_dir: Path | None = None,
        bin_dir: Path | None = None,
        uv: Path | None = None,
        index: list[str] | None = None,
        ):
    with Config.create(
            apps_dir=apps_dir,
            bin_dir=bin_dir,
            package_indices=dict(i.split("=", 1) for i in (index or [])),
            uv=uv):
        app(tokens)


def main():
    return app.meta()


if __name__ == "__main__":
    sys.exit(main())
