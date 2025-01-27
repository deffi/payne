import sys

from cyclopts import App

app = App()


@app.command
def install(path: str, version: str | None = None, /):
    ...


if __name__ == "__main__":
    sys.exit(app())
