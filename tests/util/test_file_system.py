from payne.util.file_system import TemporaryDirectory, safe_create, safe_ensure_exists

import pytest

from payne.util.path import is_empty


class TestFileSystem:
    def test_temporary_directory(self):
        with TemporaryDirectory() as d:
            assert d.is_dir()

        assert not d.exists()

    def test_safe_create_success(self):
        with TemporaryDirectory() as root:
            with safe_create(root / "a") as a:
                assert a == root / "a"
                assert a.is_dir()

                b = a / "b"
                b.write_text("b")
                assert b.is_file()

            assert root.is_dir()
            assert a.is_dir()
            assert b.is_file()

    def test_safe_create_invalid(self):
        with TemporaryDirectory() as root:
            with pytest.raises(FileNotFoundError):
                with safe_create(root / "a" / "b"):
                    pass

        with TemporaryDirectory() as root:
            a = root / "a"
            a.mkdir()

            with pytest.raises(FileExistsError):
                with safe_create(a):
                    pass

    def test_safe_create_failure(self):
        with TemporaryDirectory() as root:
            with pytest.raises(RuntimeError, match=r"^Dummy$"):
                with safe_create(root / "a") as a:
                    assert a == root / "a"
                    assert a.is_dir()

                    b = a / "b"
                    b.write_text("b")
                    assert b.is_file()

                    raise RuntimeError("Dummy")

            assert root.is_dir()
            assert not a.exists()
            assert not b.exists()

    def test_safe_ensure_exists(self):
        with TemporaryDirectory() as root:
            a = root / "a"
            b = a / "b"
            a.mkdir()

            with safe_ensure_exists(root / "a" / "b" / "c") as c:
                assert c == root / "a" / "b" / "c"
                assert a.is_dir()
                assert b.is_dir()
                assert c.is_dir()

                d = c / "d"
                d.write_text("d")
                assert d.is_file()

            assert root.is_dir()
            assert a.is_dir()
            assert b.is_dir()
            assert c.is_dir()
            assert d.is_file()

    def test_safe_ensure_exists_exists(self):
        with TemporaryDirectory() as root:
            a = root / "a"
            a.mkdir()

            with safe_ensure_exists(a):
                assert a.is_dir()
                assert is_empty(a)

            assert a.is_dir()

    def test_safe_ensure_exists_failure_non_empty(self):
        with TemporaryDirectory() as root:
            with pytest.raises(RuntimeError, match=r"^Dummy$"):
                a = root / "a"
                b = a / "b"
                a.mkdir()

                with safe_ensure_exists(root / "a" / "b" / "c") as c:
                    assert c == root / "a" / "b" / "c"
                    assert a.is_dir()
                    assert b.is_dir()
                    assert c.is_dir()

                    d = c / "d"
                    d.write_text("d")
                    assert d.is_file()

                    raise RuntimeError("Dummy")

            # There is something in the created directory, so nothing is removed
            assert root.is_dir()
            assert a.is_dir()
            assert b.is_dir()
            assert c.is_dir()
            assert d.is_file()

    def test_safe_ensure_exists_failure_empty(self):
        with TemporaryDirectory() as root:
            with pytest.raises(RuntimeError, match=r"^Dummy$"):
                a = root / "a"
                b = a / "b"
                a.mkdir()

                with safe_ensure_exists(root / "a" / "b" / "c") as c:
                    assert c == root / "a" / "b" / "c"
                    assert a.is_dir()
                    assert b.is_dir()
                    assert c.is_dir()

                    raise RuntimeError("Dummy")

            # There is something in the created directory, so nothing is removed
            assert root.is_dir()
            assert a.is_dir()  # Already existed
            assert not b.is_dir()  # Created by safe_ensure_exists
            assert not c.is_dir()  # Created by safe_ensure_exists
