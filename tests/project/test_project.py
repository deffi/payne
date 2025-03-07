from pathlib import Path

from payne.project import Project

import pytest

from common import test_data


class TestProject:
    # TODO only sup is slow, the others are fast
    @pytest.mark.slow
    @pytest.mark.parametrize("directory, name, version", [
        ("foo-1.3.0", "foo", "1.3.0"),
        ("foo-1.3.1", "foo", "1.3.1"),
        ("foo-1.3.2", "foo", "1.3.2"),
        ("bar-1.2.0", "bar", "1.2.0"),
        ("bar-1.2.1", "bar", "1.2.1"),
        ("baz-1.1.0", "baz", "1.1.0"),
        ("baz-1.1.1", "baz", "1.1.1"),
        ("sup-2.1.0", "sup", "2.1.0"),
    ])
    def test_metadata(self, directory: Path, name: str, version: str):
        project = Project(test_data / directory)
        assert project.metadata().name == name
        assert project.metadata().version == version
