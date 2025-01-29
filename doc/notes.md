# Problem: app installation directory

The uv tool installation directory (within `UV_TOOL_DIR`) is the project name
and can't be overridden. Therefore, we can't easily install multiple versions of
a project.


## Solution: Installing to different tool directory

We could install to a different directory by setting `UV_TOOL_DIR`.

For example, for installing `foo` version 1.0.0, we could set `UV_TOOL_DIR` to
`~/.local/share/payne/apps/foo-1.0.0`. We'd get another subdirectory from uv, so
the application would end up in `~/.local/share/payne/apps/foo-1.0.0/foo`, which
seems acceptable (it might even come in handy if we want to add metadata, and it
would avoid polluting the uv tool dir).

This means that the user can't use `uv tool` to manage the installed
applications (at least not without manually setting `UV_TOOL_DIR`), but that
isn't a problem - we'll just have to provide `payne list` and `payne uninstall`
commands. As a bonus, the fact that we used `uv tool` to install the package
would be hidden from the user.

Really, the directory `~/.local/share/payne` should be determined in the same
way that uv uses to determine the default `UV_TOOL_DIR`, not least in order to
support different platforms.

This would be independent of the build backend.


## Solution: Changing the project name to include the version

We could also change the project name to include the version - i.e., change
`foo` to `foo-1.0.0`. That way, the app would be installed to
`~/local/share/uv/tools/foo-1.0.0`.


### Problem: source directory

This would create a new problem, though: if the source directory isn't
configured explicitly in `pyproject.toml`, the build backend will select it
based on the project name, and if that is changed, the actual source directory
won't be found.

If there is an explicit configuration, this is irrelevant.

The selection heuristic depends on the build backend:
  * Hatch: https://hatch.pypa.io/latest/plugins/builder/wheel/#default-file-selection

The explicit configuration also depends on the build backend:
  * Hatch: `tool.hatch.build.targets.wheel.packages`

For all solutions, we have to identify the actual source directory, using the
same heuristic as the build backend.


#### Solution: rename the source directory

We could rename the source directory to match the project name.

Since the project name might not be a valid Python package name, we'd have to
modify it - and in the same way as the build backend.


#### Solution: configure the source directory explicitly

We could add the path to the source directory to `pyproject.toml`


# Problem: wrapper names

For all scripts (and gui-scripts), uv will install a wrapper/shim/trampoline to
`PATH`. The name is the same as the script name and can't be overridden.
Therefore, the names from multiple versions will conflict.


## Solution: rename wrappers after installation

We could install the app first, and then rename the wrapper to append the
version.

This would require us to find them in the first place, handle the case where the
name is already present (will uv overwrite it or skip it?), and handle
uninstallation.


## Solution: change script names

We could update the script names in `pyproject.toml` to append the version,
e.g., `foo-1.0.0`.

This would require us to modify `pyproject.toml`, which we could get around
otherwise.

Note that Poetry 1 uses the non-standard `tool.poetry.scripts` `pyproject.toml`.

We should reject all build backends for which we cannot be sure about the script
configuration.
