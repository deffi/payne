# Basic functionality

On installing cowsay:
  * Cowsay 5.0 has no wheel
  * Cowsay (up to) 6.0 has no pyproject.toml -> uv export fails
  * Cowsay 6.1 has no sdist

Installing:
  * If installing locked: determine locked dependencies
    * If installing a package: get the sdist as a temporary project
    * Identify the project frontend
    * Export constraints
  * If installing an (actual, not temporary) project: determine the version
    * Try to read it from pyproject.toml
    * If there is no pyproject or the version is dynamic
      * Build the sdist (partly?) to get the metadata
  * Install (from the original source)

Extra package indices:
  * We're using different tools, sometimes in the same invocation
    * uv tool
    * build library
    * unearth library
    * pip tool
  * These tools are configured in different ways
  * We want them to behave consistently
  * So we use our own configuration and pass it on to the tools on invocation,
    overriding any configuration that may come from the environment or
    configuration files
  * We need the name of the index if we have packages that are pinned to an
    index 
    * uv tool install --from .
    * uv export

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


# Error handling

If the testdata server isn't running, installing foo fails, but it will still
look like it is installed because the directory exists


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
