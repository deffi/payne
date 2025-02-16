from payne.app import AppVersionMetadata
from payne.util.file_system import TemporaryDirectory
from payne.app.app_version_metadata import create_hash, hash_matches, Script


class TestAppVersionMetadata:
    def test_dump(self):
        with TemporaryDirectory() as root:
            metadata = AppVersionMetadata(
                scripts = [
                    Script(root / "a-1", "a", "sha1:asdf"),
                    Script(root / "b-1", "b", "sha1:sdfg"),
                ],
            )

            assert metadata.dump() == {
                "_schema": {
                    "name": "payne.app-version-metadata",
                    "version": "1.0",
                },
                "scripts": [
                    {"file": str(root / "a-1"), "script_name": "a", "hash": "sha1:asdf"},
                    {"file": str(root / "b-1"), "script_name": "b", "hash": "sha1:sdfg"},
                ],
            }

    def test_parse(self):
        with TemporaryDirectory() as root:
            metadata = AppVersionMetadata.load({
                "_schema": {
                    "name": "payne.app-version-metadata",
                    "version": "1.0",
                },
                "scripts": [
                    {"file": str(root / "a-1"), "script_name": "a", "hash": "sha1:asdf"},
                    {"file": str(root / "b-1"), "script_name": "b", "hash": "sha1:sdfg"},
                ],
            })

            assert metadata == AppVersionMetadata(
                scripts = [
                    Script(root / "a-1", "a", "sha1:asdf"),
                    Script(root / "b-1", "b", "sha1:sdfg"),
                ],
            )

    def test_hash(self):
        hash_ = create_hash(b"foo")
        assert hash_matches(b"foo", hash_)
        assert not hash_matches(b"bar", hash_)
