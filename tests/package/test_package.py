from payne.package import Package

import pytest


class TestPackage:
    def test_version(self):
        Package("foo", "1.2.3")

        with pytest.raises(AssertionError):
            Package("foo", "=1.2.3")

    def test_requirement_specifyier(self):
        assert Package("foo", "1.2.3").requirement_specifier() == "foo==1.2.3"
