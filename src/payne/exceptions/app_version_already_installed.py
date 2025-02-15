from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from payne.app import App


class AppVersionAlreadyInstalled(Exception):
    def __init__(self, app: "App"):
        self.app = app

    def __str__(self):
        # TODO factor out "{app.name} {app.version}"
        return f"{self.app.name} {self.app.version} already installed in {self.app.root}"
