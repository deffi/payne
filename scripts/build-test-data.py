from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

from cyclopts import App

import payne


test_data = Path(payne.__file__).parent.parent.parent / "test_data"
package_dir = Path(payne.__file__).parent.parent.parent / "run" / "payne_test_data"


@dataclass(frozen=True)
class Project:
    name: str
    version: str

    @property
    def dir(self) -> Path:
        return test_data / f"{self.name}-{self.version}"

    @property
    def package_dir(self) -> Path:
        return package_dir / self.name

    @property
    def package_file_pattern(self) -> str:
        return f"{self.name}-{self.version}*"

    def __str__(self):
        return f"{self.name} {self.version}"


app = App()


@app.default
def build_test_data(uv: str = "uv", rebuild: bool = False):

    projects = (
        Project("baz", "1.1.0"),
        Project("baz", "1.1.1"),
        Project("bar", "1.2.0"),
        Project("bar", "1.2.1"),
        Project("foo", "1.3.0"),
        Project("foo", "1.3.1"),
        Project("foo", "1.3.2"),
        Project("sup", "2.1.0"),
    )

    for project in projects:
        if not rebuild and any(project.package_dir.glob(project.package_file_pattern)):
            print(f"{project.package_file_pattern} already exists in {project.package_dir}, skipping {project}")
        else:
            print(f"Building project {project}")

            try:
                subprocess.check_call([
                    uv,
                    "build",
                    "--out-dir", project.package_dir,
                ], cwd=project.dir)
            except BaseException:
                print(f"Build aborted, removing {project.package_file_pattern} from {project.package_dir}")
                for path in project.package_dir.glob(project.package_file_pattern):
                    # print(f"  {path}")
                    path.unlink()


if __name__ == "__main__":
    sys.exit(app())
