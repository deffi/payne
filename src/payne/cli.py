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
        from_: Path | None = None):
    match name, version, from_:
        case n, v, None:
            Payne().install_from_remote(name, version)
        case None, None, from_:
            Payne().install_from_local(from_)
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
