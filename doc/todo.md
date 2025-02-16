# Next 

Can we speed up tests by using a file:// repository?


# Essential

Test installing from local index with dependency from PyPI

Identify paths like uv (`uv tool install`):
  * Apps directory
    * Unix: ~/.local/share/payne/apps
  * bin directory: ~/.local/bin

Warn if the bin directory isn't in PATH

Allow configuring uv binary with command line argument 

Handle dynamic version in `pyproject.toml`? We'll have to do the same package
building procedure as we do if there is no `pyproject.toml` in the first place.


# Project

Add project metadata
https://packaging.python.org/en/latest/tutorials/packaging-projects/#configuring-metadata

Verfify sdist contents


# Desired features

Payne list: message if there are no apps

Don't re-use UV_* environment variables, use PAYNE_* or command line arguments
instead

Option to install without scripts
  * Command to install/remove scripts after installing the app


# Error handling

Error while uninstalling:
  * Reading metadata:
    * Don't do anything
    * Allow forcing (scripts might not be uninstalled)
  * Deleting stuff (e.g., permission denied or file locked in bin directory)
    * Continue deleting the rest
    * Output a warning

App (not app-version) directory isn't always remove when installation fails,
e.g. 
    uv run payne install --index payne_test_data=http://localhost:8000/payne_test_data foo 1.3.0 --no-locked
While the server isn't running. Looks like it tries, but somthing still has the file open.


# Nice to have features

Configuration
  * Source
    * Command line --foo
    * Environment $PAYNE_FOO
    * User config
    * System config
    * Default
  * For uv binary:
    * Absolute path
    * Relative path to CWD (command line only)
    * Plain name, lookup in PATH
  * How do other tools do it?
    * uv
    * pip

Allow specifying app name and version
  * When installing from a project, don't read the metadata (which might mean
    building the project) if both are overridden
  * When installing from a package, use the override values over the package
    name and version

Allow uninstalling all versions of a specific tool


# Robustness

All subprocess invocations:
  * Controlled environment (specify the entire environment to avoid accidentally
    picking up local configuration)
  * Controlled CWD

Wherever listing files/directories, handle if there is an unexpected
directory/file


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

Test data: different names for project, package, and script 

When testing, clear the environment?

Re-install an app
Uninstall a non-installed app

CLI tests (mock class Payne)

End-to-end tests

Install cowsay

Integrated server is (attempted) started twice

Slow on Windows with integrated server

