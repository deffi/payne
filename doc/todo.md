# TODO

## Basic functionality

Verify in pyproject.toml:
  * Version must exist
  * `build-system.build-backend` must be `hatchling`
    * Because we'll be using `tool.hatch.build.targets.wheel` (?)

Identify the source directory:
  * `foo` or `src/foo`
  * How does uv do it?
    * Does it support something else (e.g. `source/`)?
    * What if there are both?

Copy project to temporary directory

Modify pyproject.toml:
  * Append version number to project name
  * Append version number to entrypoints
  * `tool.hatch.build.targets.wheel.packages` = identified source directory
    * Because it will no longer match the project name
    * Or rename it, then we don't have to depend on the build backend
    * Unless it already exists

Generate temporary `requirements.txt` with  locked dependency version
  * `uv export --no-dev --no-emit-project --frozen --no-header --no-hashes --out-file $temp_requirements`

Call uv:
  * `uv tool install --constraints $temp_requirements --from $temp_dir $project-name`
  * Will --constraints work for indirect dependencies?
  * If that doesn't work, then use `uv add -r` with temporary requirements


## Desired functionality

Find uv executable
  * `--uv`
    * absolute
    * relative starting with `./`?
    * `PATH` lookup
    * How do other tools do it?
  * `$PAYNE_UV` (like `--uv`)
  * Default `uv`

Support older Poetry 1: scripts in `tool.poetry.scripts`


## Open questions

Can uv have a dynamic version in `pyproject.toml`? 


## Future work

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
