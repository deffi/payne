# payne

Payne allows a user to install multiple versions of a Python application at the
same time. It uses `uv` for isolation between applications and caching.

**Note**: there may be incompatible chages before version 1.0. If you use an 
earlier version, you may have to delete your applications directory and
re-install applications.


## Testing

Before running the tests, run `scripts/build-test-data.py`

When testing manually, start an HTTP server in `run`...:

    uv tool run python -m http.server -d run

...and set UV_INDEX
    
    UV_INDEX=payne_test_data=http://localhost:8000/payne_test_data

The automated tests run their own server, but will use the already running one
if there is one.


## Etymology

This should have been called "Pain", for **P**ython **a**pplication
**in**staller, but that name was already taken on PyPI. "Payne" is considered
close enough.
