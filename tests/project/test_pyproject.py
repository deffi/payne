from payne.project import Pyproject


class TestPyproject:
    def test_name(self):
        p = Pyproject({
            "project": {
                "name": "foo",
            },
        })

        assert p.name() == "foo"
