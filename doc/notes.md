# App installation

Building packages ourselves might not be feasible (e.g., if something needs to
be compiled). So we should prefer to install wheels if possible (when installing
from a package index).

We call an installer tool for installing packages (and their dependencies). For
now, this is `uv` (regardless of the build frontend that was used for the
package). In the future, we might want to support other tools as an alternative,
if they provide an advantage (e.g., pipx).


# Locked package versions

To get reproducible installs, we need to consider the project's lockfile and
install the exact locked versions of all dependencies (including indirect
dependencies).

Since the lockfile is not in the wheel, we absolutely need the sources here.
  * If we're installing from sources (or VCS), we already have them
  * If we're installing from a package index (even if we're installing a wheel),
    we have to fetch the sdist. If we can't, then we won't be able to install
    locked versions

The lockfile will depend on the build frontend. We don't know which one this is,
so we have to see which lockfiles are there:
  * uv: `uv.lock`
  * Poetry: ...
  * ...

We then need the respective tool to extract the locked versions. If we don't
find a lockfile, then we won't be able to install locked versions. If we find
multiple lockfiles, then we'll have to have the user specify which one to use.

If we are in a controlled environment where we'll only be installing packages
with pre-pinned packages, then we don't need this functionality.


## Installing the locked versions

`uv tool install` does not use the lockfile.


### Solution: specify exact versions during installation

`uv tool install` seems to have some functionality here:
  * `--with-requirements`
  * `--constraints`
  * `--overrides`

Hopefully, one of the is suitable for this purpose.


### Solution: re-write dependencies in (temporary) `pyproject.toml`

This seems easily done using `uv add -r requirements.txt` with a
`requirements.txt` exported from the lockfile. Then, `uv tool install` would be
forced to use the correct versions.

However, this requires re-building the project.


# Installing multiple app versions

Package installation involves:
  * Installing the package (and its dependencies) into a (package-specific) venv
    within a package directory
  * Installing wrappers (symlinks on Linux or trampolines on Windows) for all
    scripts into a bin directory

To install multiple versions, we need to avoid conflicts in both.


## App installation directory

Uv installs all tools below the tool directory (`UV_TOOL_DIR`), in a directory
whose name is the project name and can't be overridden. Therefore, installing
multiple versions of an app would lead to conflicts.


### Solution: separate tool directories for each app

We could install each app to a different directory by setting `UV_TOOL_DIR`.

For example, for installing `foo` version 1.0.0, we could set `UV_TOOL_DIR` to
`~/.local/share/payne/apps/foo-1.0.0`. We'd get another subdirectory from uv, so
the app would end up in `~/.local/share/payne/apps/foo-1.0.0/foo`, which seems
acceptable (it might even come in handy if we want to add metadata, and it would
avoid polluting the actual uv tool directory).

This means that the user can't use `uv tool` to manage the installed
apps (at least not without manually setting `UV_TOOL_DIR`), which has some
advantages:
  * We can clean up the wrappers on uninstallation, if we have to
  * The used installer is hidden from the user

Since the user can't use uv to manage the installed apps, we'll have to
implement that ourselves; at least, we'll need `payne list` and `payne
uninstall` commands.

The directory `~/.local/share/payne` should be determined in the same way that
uv uses to determine the default `UV_TOOL_DIR`, not least in order to support
different platforms.

This would be independent of the build backend.


### Solution: Changing the project name to include the version

We could also change the project name in `pyproject.toml` to include the
version - i.e., change `foo` to `foo-1.0.0`. That way, each version of the app
would be installed to a different directory in the tool directory.

We might still want to choose a different tool directory than the one of uv, for
the reasons described above.

This would require us to re-build the project.


#### Problem: source directory

Another problem would be that if the source directory isn't configured
explicitly in `pyproject.toml`, the build backend will select it based on the
project name, and if the project name is changed, the build backend won't be
able actual to identify the correct source directory.

This is only relevant if the source directory isn't configured explicitly.

The selection heuristic depends on the build backend:
  * Hatch: https://hatch.pypa.io/latest/plugins/builder/wheel/#default-file-selection

The explicit configuration also depends on the build backend:
  * Hatch: `tool.hatch.build.targets.wheel.packages`

To solve this, we'd first have to identify the actual source directory, using
the same heuristic as the build backend (and using the original project name).
Then, we'd have two options:
  * Rename the source directory to match the project name. Since the project
    name might not be a valid Python package name, we'd have to modify it - and
    in the same way as expected by the build backend.
  * Explicitly configure the source directory in `pyproject.toml`, in the way
    that is specific to the build backend.


## Wrapper installation

In order for the user to run any of the installed versions of an app, they must
be distinguished by name (contrary to the installation directory, it's not
sufficient to install them in different directories with the same name).

We also don't want to add a PATH entry for each of them because that would
require shell-specific configuration (and it would bloat the PATH). Therefore,
we install all wrappers to a single bin directory.

Uv doesn't allow overriding the name of the wrapper. Therefore, installing
multiple versions of an app would lead to conflicts.

By default, uv uses `~/.local/bin` as the bin directory, which may be shared
with other applications (in particular, uv itself). We'll probably want to use
the same directory because it's likely to already be on the PATH (in particular,
if uv is installed). Or we might want to choose another one to avoid conflicts.


### Solution: rename wrappers after installation

We could install the app first, and then rename the wrapper to append the
version.

We should install them to a temporary bin directory first because otherwise...
  * ...we might overwrite something that's already there (assuming a shared bin
    directory or a prefix conflict)
  * ...we would have to read the script names from `pyproject.toml` because
    otherwise, it would be hard to tell what was installed (comparing files
    before and after installation would incur a race condition)
 
The advantage is that it would work with any build backend, even standard
non-compliant ones like Poetry 1.


### Solution: change script names

We could also change the script names in `pyproject.toml` to append the version,
e.g., `foo-1.0.0`.

This would require us to re-build the project.

Build backends (e.g., Poetry 1) might use non-standard configuration in
`pyproject.toml`, so we'd have to handle this explicitly and reject all build
backends which we don't handle.


# Name conflicts

Unless we can define the behavior, we should reject installation of the whole
app if a conflict is detected.


## Package names and versions

We append the version to the (distribution) package name, separated by some
string (e.g., a single dash: `foo-1.0.0`).

A conflict can occur if the separator string occurs multiple times in the full
name, and it can't be determined which one is the separate because the separator
string could be part of both the name and the version. For example, with
separator string `"-"`:
  * foo version 1-2
  * foo-1 version 2
Both of these would result in the directory name foo-1-1.

We could get around this by replacing all dashes in the name with underscores.
Since PyPI doesn't allow different package names that normalize to the same
name, we know that the first dash in the full name is the separator, even if a
dash appears in the version. Therefore, there can't be any conflicts.
https://packaging.python.org/en/latest/specifications/name-normalization/

We could also separate the version with a tilde, which is not allowed in package
names (nor versions).

The user is not expected to interact with the tool directories directly, so this
would not be a big problem. We would, however, need to store the original name
in the app metadata for presentation to the user.


## Script names and versions

We can get the same conflict between scripts with appended version if the
version contains a dash:
  * foo version 1-2
  * foo-1 version 2

Here, replacing dashes with underscores is not an option because we don't want
to modify the script names.

Separating the version with a tilde would be possible because the version can't
contain a tilde.
https://packaging.python.org/en/latest/specifications/version-specifiers/


## Same script in multiple apps

Multiple packages can declare the same script. This will cause a conflict.

We could get around this by appending the package name; e.g.
`frob-frobnicate-1.0.0` (package `frobnicate` with script `frob`)

This could cause more conflicts, e.g.:
  * Package `bar-baz`, script `foo`
  * Package `baz`, script `foo-bar`
Both would result in `foo-bar-baz-1.0.0`.

We could probably use a tilde here because while the script name can contain
one, neither the package name nor the version can.

But we would only want to do this in case of an actual conflict, and this means
that on conflict
  * Either one of the names would change
  * Or the result would depend on the order in which the packages were installed

In case of a conflict, we might allow the user to replace or modify the name. In
this case, we'll need to store the mapping in the metadata. 


# Summary

We need to actually install the locked versions
  * Specify to `uv tool install`
  * Re-write dependencies in `pyproject.toml`

App installation directories would cause conflicts
  * Separate tool directories for each app
  * Change project name in `pyproject.toml`
    Mismatch between new project name and auto-detected source directory
    * Rename source directory
    * Explicitly configure source directory

We need to change the wrapper names
  * Rename after installation
  * Change script names in `pyproject.toml`

Conflicts can occur
  * Between package-version names
    * Replace dashes in project name with underscores
    * Use package~version instead
  * Between script-version names
    * Use script~version instead
  * Between scripts of different packages


# Decision

We want to avoid re-building, so changing `pyproject.toml` is out.

Therefore, the only option is:
  * Specify locked versions to `uv tool install`
  * Use separate tool directories for each app; this also avoid the source
    directory name mismatch and has some additional advantages
  * Rename the wrappers after installation (and therefore install them to a
    temporary bin directory first)

We don't handle conflicts related to the version for now. They are probably
pretty rare. If one is detected, we reject the installation.

We don't handle conflicts between scripts of different packages for now. They
are probably semi-rare. If one is detected, we reject the installation.
