# Basic functionality

## Test data

Without dependencies
  * Application foo
    * 1.0.0
    * 1.1.0

With dependencies
  * Library bar
  * Library baz


## Common

Identify paths:
  * Apps directory: ~/.local/share/payne/apps
  * bin directory: ~/.local/bin


## Installing from local dir

Read `pyproject.toml`:
  * `project.dynamic` must not contain `"version"`
  * Read `project.name`
  * Read `project.version`

Generate temporary `requirements.txt` with  locked dependency version
  * `uv export --no-dev --no-emit-project --frozen --no-header --no-hashes --out-file $temp_requirements`

Call uv:
  * Set UV_TOOL_DIR to $apps-dir/$project-name
  * Set UV_BIN_DIR to temporary dir
  * `uv tool install --constraints $temp_requirements --from $temp_dir $project-name`
    * Will --constraints work for indirect dependencies?
    * If that doesn't work, then use `uv add -r` with temporary requirements
  * Rename and move wrappers from temporary UV_BIN_DIR to bin dir


## Installing from package index

Fetch sdist to temporary directory

Generate temporary `requirements.txt` with  locked dependency version

Call uv:
  * Set UV_TOOL_DIR
  * Set UV_BIN_DIR to temporary dir
  * `uv tool install --constraints $temp_requirements $project-name`
  * Rename and move wrappers from temporary UV_BIN_DIR to bin dir


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


# Open questions

Can uv have a dynamic version in `pyproject.toml`? 


# Future work

Support packages from PyPI
  * Download sdist
  * Unpack to temporary directory
  * Need to check `pyproject.toml` conditions after unpacking rather than before
    copying

Other sources?
  * Git
  * SVN

Support other package mangers
  * https://pypi.org/project/migrate-to-uv/

Add `payne uninstall`

Allow requesting a coarser version. E.g., request version 1 and get 1.0.0.
  * Should we then also provide a `foo-1` (and potentially `foo-1.0`) command in
    addition to `foo-1.0.0`? Should we even do that unconditionally, provided
    that there is only one such version?
  * Should we do updates of such a version?
  * Should we install into `foo-1` or `foo-1.0.0`?

Handle conflicts between multiple packages that declare the same script
