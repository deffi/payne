# Basic functionality

## Common

Identify paths:
  * Apps directory: ~/.local/share/payne/apps
  * bin directory: ~/.local/bin


## Locked dependencies

Test data with dependencies

When installing from package index:
  * Fetch sdist to temporary directory

Generate temporary `requirements.txt` with  locked dependency version
  * `uv export --no-dev --no-emit-project --frozen --no-header --no-hashes --out-file $temp_requirements`

Installation:
  * `uv tool install --constraints $temp_requirements ...`
    * Will --constraints work for indirect dependencies?
    * If that doesn't work, then use `uv add -r` with temporary requirements



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

Store script md5sum in metadata and don't delete it if it was changed

Should we allow installing an app under a different name than the package name?
This might be useful if we want to install packages with the same name from
different repositories, or from a repository and from a local directory. But
we'd also be likely to get conflicting scripts names.


# Open questions

Can uv have a dynamic version in `pyproject.toml`? 


# Future work

Support packages from PyPI
  * Download sdist
  * Unpack to temporary directory
  * Need to check `pyproject.toml` conditions after unpacking rather than before
    copying

Install from local archive
https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

Other sources?
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
