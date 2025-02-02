from pathlib import Path
import sys

from cyclopts import App

from payne import Payne

app = App()


@app.command
def status():
    Payne().status()


@app.command
def install(*, from_: Path):
    Payne().install_from_local(from_)


@app.command
def uninstall(package_name: str, version: str):
    Payne().uninstall(package_name, version)


@app.command
def list_():
    Payne().list_()


if __name__ == "__main__":
    sys.exit(app())
