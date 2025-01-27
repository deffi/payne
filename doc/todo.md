# TODO

## Basic functionality

Find uv executable
  * `--uv`
    * absolute
    * relative starting with `./`?
    * `PATH` lookup
    * How do other tools do it?
  * `$PAYNE_UV` (like `--uv`)
  * Default `uv`

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
  * If that doesn't work, then use `uv add -r` with temporary requirements


## Open questions

Can uv have a dynamic version? 


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
