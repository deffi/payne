from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from payne.package import Package
#     from payne.project import Project


class FrontendNotRecognized(Exception):
    def __init__(self, source: "Project | Package"):
        self.source = source

    def __str__(self):
        return f"Build frontend not recognized for {self.source}"
