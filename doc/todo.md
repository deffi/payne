# Next 

# Essential

Identify paths like uv (`uv tool install`; XDG standard):
  * Apps directory
      * $PAYNE_APPS_DIR
      * $XDG_DATA_HOME/payne/apps (Linux)
      * $HOME/.local/share/payne/apps (Linux)
        $APPDATA or $LOCALAPPDATA? / payne/apps (Windows) How does uv?
  * bin directory:
      * $PAYNE_BIN_DIR
      * $XDG_BIN_HOME (not really in the XDG spec, but quite common)
      * $XDG_DATA_HOME/../bin
      * $HOME/.local/bin (Linux)
        $USERPROFILE/.local/bin (Windows) 
  * https://docs.astral.sh/uv/reference/cli/#uv-tool-dir
  * https://specifications.freedesktop.org/basedir-spec/latest/
  * platformdirs package?
  * xdg-base-dirs? pyxdg?

Refuse installation on script name collision


# Desired features

The output of uv export does not contain information about what index a package
is pinned to - not even the name. So on installation, if we're missing the index
definition, might we install the wrong package (same name in a different index)?

Don't re-use UV_* environment variables, use PAYNE_* or command line arguments
instead

Option to install without scripts
  * Command to install/remove scripts after installing the app

Better messages:
  * When building a project
  * Hide uv invocation messages?

Remove script name from metadata? On Windows, it includes the ".exe" suffix
because it is generated from the files installed by uv.

"Uninstall script" message is bad

Find out why the GitHub Windows test jobs fail during cleanup and re-enable them

Help texts for parameters

Configuration file:
  * $XDG_CONFIG_HOME/uv/uv.toml
  * ($XDG_CONFIG_DIRS)/uv/uv.toml
  * File name TBD
  * $HOME/.config/payne/payne.toml (Linux)
    $APPDATA/payne/payne.toml (Windows)

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

Example error message from uv:
    error: Failed to install: xyz.whl
      Caused by: failed to read directory `...`: [exception message]

payne list: metadata could not be loaded

payne install: no version specified

Specified uv does not exit 

Frontend not recognized: suggest `--no-locked`


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

For projects with backend hatchling, we can use `hatch version` to get the
version instead of building the project. Maybe also for others? And is there a
library interface to that? We'll still need the name from pyproject.toml.

Colored output (with rich)

App version metadata:
  * From where the app was installed
    * If from a project, whether it was built

payne config edit (like pip)

Payne status: show where 


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

When installing a project, make sure that the lockfile remains unchanged
