import sys

from cyclopts import App

app = App()


@app.command
def install(name_or_path: str, version: str | None = None, /):
    print(f"{name_or_path} {version}")


@app.command
def uninstall(name: str, version: str | None = None, /):
    print(f"{name} {version}")


if __name__ == "__main__":
    sys.exit(app())
