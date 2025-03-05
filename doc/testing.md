# Test data

Since Payne handles Python projects (applications and libraries), we need some
projects for testing it.

The versions of the projects have an *x.y.z* scheme:
  * *x* designates a set of related projects
  * *y* designates a project within the set
  * *z* designates a version of the project

Thus, version numbers are unique even across projects.


## Set 1 (foo, bar, baz)

To test transitive dependencies, we have three projects with dependencies like
this:
  * `foo` -> `bar`
  * `bar` -> `baz`
  * `baz`

The only thing that the projects to is to output their version. Conceptually,
`bar` and `baz` are libraries, although they do have a script so they can be
tested in isolation.

`baz` (project 1) has two versions:
  * 1.1.0
  * 1.1.1

`bar` (project 2) has two versions:
  * 1.2.0
  * 1.2.1

Both of them depend on an unspecified version of `baz`, and both are locked to
`baz` 1.1.0 (i.e., the earliest version). Therefore:
  * For unlocked install, we expect `baz` 1.1.1 (the latest version)
  * For locked install, we expect `baz` 1.1.0 (the locked version, even though a
    later version is available)

`foo` (project 3) has three versions:
  * 1.3.0 depends on an unspecified version of `bar`
  * 1.3.1 depends on `bar` 1.2.0, which in turn depends on an unspecified
    version of `baz`
  * 1.3.2 also depends on `bar` 1.2.0 and additionally on `baz` 1.1.0

All three of them are locked to `baz` 1.1.0 and `bar` 1.2.0 (i.e., the earliest
version for each). Thus:
  * For unlocked install, we expect:
    * `foo` 1.3.0: `bar` 1.2.1, `baz` 1.1.1 (the latest versions)
    * `foo` 1.3.1: `bar` 1.2.0, `baz` 1.1.1 (specific version of `bar`, but
      latest version of `baz` - even though it is locked to 1.1.0 in `bar`)
    * `foo` 1.3.2: `bar` 1.2.0, `baz` 1.1.0 (specific version of both; the
      direct dependency on `baz` forces 1.1.0 even though as a dependency of
      `bar`, it is unspecified)
  * For locked install, we expect `bar` 1.2.0 and `baz` 1.1.0 (the locked
    version, even though a later version is available)


## Set 2 (sup)

`sup` uses `setup.py` in lieu of `pyproject.toml`. This means that metadata is
not readily available without building at least a source distribution. Metadata
is required to determine the name and version when installing a local project. 


## Set 3 (dyn)

`dyn` uses a dynamic version in `pyproject.toml`. This means that we either have
to invoke the respective build tool to determine the version, or we have to
build a source distribution. 


# Building the test projects

Before running any tests that use the test projects, they must be built. This is
done by `scripts/build-test-data.py`, which invokes `uv build` on each of the
projects. The results are placed in `run/payne_test_data`.


# Serving the test projects

Since Payne installs dependencies from a package repository, we need some test
packages in a local package repository. There are two major options for the
repository location:
  * File system
  * HTTP server

A file system repository it is less hassle (because we don't have to run a
server) and slightly faster on both Windows and Linux.


## File system repository

In most cases, we can use a `file://` URL pointing to the local repository.



## HTTP repository

If we want to use an HTTP repository, we can start a web server on
`localhost:8000` that serves the contents of `run`. This can be accomplished by
running in the project root:

    uv run python -m http.server -d run

The repository is then available at http://localhost:8000/payne_test_data.

To test the server, run

    export UV_INDEX=payne_test_data=http://localhost:8000/payne_test_data
    uv tool run foo

This should result in

    This is foo 1.3.2
    This is bar 1.2.0
    This is baz 1.1.0


## Automated tests

Most automated tests use a file system repository.

For tests that need to use an HTTP repository, there's a Pytest fixture
`fixtures.index_server.index_server` that runs a server in a separate thread.
If a server has already been started manually, the extra server will fail to
start and the existing server will be used.


# Packages from PyPI

Cowsay:
  * Cowsay 5.0 has no wheel
  * Cowsay (up to) 6.0 has no pyproject.toml -> uv export fails
  * Cowsay 6.1 has no sdist

All of them can be installed (Cowsay 5.0 has to be built from the sdist, which
is handled automatically by uv). None of them can be installed with locked
dependencies because there is no lockfile (6.1 doesn't even have an sdist, so we
can't even check).
