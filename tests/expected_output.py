_F = False
_T = True

_expected_output = {
    # baz 1.1.0
    ("baz", "1.1.0", _F, "baz"):"This is baz 1.1.0\n",
    ("baz", "1.1.0", _T, "baz"): "This is baz 1.1.0\n",

    # baz 1.1.1
    ("baz", "1.1.1", _F, "baz"): "This is baz 1.1.1\n",
    ("baz", "1.1.1", _T, "baz"): "This is baz 1.1.1\n",

    # bar 1.2.0: latest baz
    ("bar", "1.2.0", _F, "bar"): "This is bar 1.2.0\nThis is baz 1.1.1\n",
    ("bar", "1.2.0", _T, "bar"): "This is bar 1.2.0\nThis is baz 1.1.0\n",

    # bar 1.2.1: latest baz
    ("bar", "1.2.1", _F, "bar"): "This is bar 1.2.1\nThis is baz 1.1.1\n",
    ("bar", "1.2.1", _T, "bar"): "This is bar 1.2.1\nThis is baz 1.1.0\n",

    # foo 1.3.0: latest bar, latest baz
    ("foo", "1.3.0", _F, "foo"): "This is foo 1.3.0\nThis is bar 1.2.1\nThis is baz 1.1.1\n",
    ("foo", "1.3.0", _T, "foo"): "This is foo 1.3.0\nThis is bar 1.2.0\nThis is baz 1.1.0\n",

    # foo 1.3.1: bar pinned, latest baz
    ("foo", "1.3.1", _F, "foo"): "This is foo 1.3.1\nThis is bar 1.2.0\nThis is baz 1.1.1\n",
    ("foo", "1.3.1", _T, "foo"): "This is foo 1.3.1\nThis is bar 1.2.0\nThis is baz 1.1.0\n",

    # foo 1.3.2: bar pinned, baz pinned
    ("foo", "1.3.2", _F, "foo"): "This is foo 1.3.2\nThis is bar 1.2.0\nThis is baz 1.1.0\n",
    ("foo", "1.3.2", _T, "foo"): "This is foo 1.3.2\nThis is bar 1.2.0\nThis is baz 1.1.0\n",

    # sup 2.1.0
    ("sup", "2.1.0", _F, "sup"): "This is sup 2.1.0\n",
    # `sup` has no lockfile

    # dyn 3.1.0
    ("dyn", "3.1.0", _F, "dyn"): "This is dyn 3.1.0\n",
    ("dyn", "3.1.0", _T, "dyn"): "This is dyn 3.1.0\n",

    # dep 4.1.0: pygments constrained
    ("dep", "4.1.0", _F, "dep"): "This is dep 4.1.0\nThis is pygments 2.1\n",
    ("dep", "4.1.0", _T, "dep"): "This is dep 4.1.0\nThis is pygments 2.0\n",

    # dep 4.1.1: pygments pinned
    ("dep", "4.1.1", _F, "dep"): "This is dep 4.1.1\nThis is pygments 2.0\n",
    ("dep", "4.1.1", _T, "dep"): "This is dep 4.1.1\nThis is pygments 2.0\n",
}


def expected_output(name: str, version: str, locked: bool, script: str):
    return _expected_output[(name, version, locked, script)]
