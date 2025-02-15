# Basic functionality

Test installing from local index with dependency from PyPI

Identify paths:
  * Apps directory: ~/.local/share/payne/apps
  * bin directory: ~/.local/bin

When testing, clear the environment?


# Desired functionality

Find uv executable
  * Command line `--uv`
    * absolute
    * relative starting with `./`?
    * `PATH` lookup
    * How do other tools do it?
  * `$PAYNE_UV` (like `--uv`)
  * User config
    * Like command line, but no relative path
  * System config
    * Like user config
  * Default `uv` (`PATH` lookup)

Identify apps directory like uv

Store more script metadata:
  * Original name
  * Checksum, and don't delete it if it was changed

Should we allow installing an app under a different name than the package name?
This might be useful if we want to install packages with the same name from
different repositories, or from a repository and from a local directory. But
we'd also be likely to get conflicting scripts names.

Uninstalling corrupted app installations (e.g. metadata file missing or can't
be read)

Don't re-use UV_* environment variables, use PAYNE_* or command line arguments
instead

What is currently called "app" should be "app version", and then we can use
"app" for the unit of all installed versions of an app.

Allow overriding name and version for projects; don't read metadata (or build
the project) if name and version are overridden.

Allow uninstalling all versions of a specific tool


# Error handling

App (not app-version) directory isn't always remove when installation fails,
e.g. 
    uv run payne install --index payne_test_data=http://localhost:8000/payne_test_data foo 1.3.0 --no-locked
While the server isn't running. Looks like it tries, but somthing still has the file open.


# Robustness

All subprocess invocations:
  * Controlled environment (specify the entire environment to avoid accidentally
    picking up local configuration)
  * Controlled PWD

Wherever listing files/directories, handle if there is an unexpectred
directory/file


# Open questions

Can uv have a dynamic version in `pyproject.toml`?
  * Can we get it by building a source package?


# Future work

Other sources?
  * Local archive
    https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
  * Git
  * SVN

Support other package mangers
  * https://pypi.org/project/migrate-to-uv/

Allow requesting a coarser version. E.g., request version 1 and get 1.0.0.
  * Should we then also provide a `foo-1` (and potentially `foo-1.0`) command in
    addition to `foo-1.0.0`? Should we even do that unconditionally, provided
    that there is only one such version?
  * Should we do updates of such a version?
  * Should we install into `foo-1` or `foo-1.0.0`?

Handle conflicts between multiple packages that declare the same script

Support installing with venv instead of uv


# Tests

Re-install an app
Uninstall a non-installed app

CLI tests (mock class Payne)

End-to-end tests

Install cowsay
