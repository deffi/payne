import http.server
from threading import Thread

import pytest

from dirs import run


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(run), **kwargs)

    def log_message(self, format_, *args):
        match format_, args:
            case '"%s" %s %s', (_, '200' | '404', _):
                pass
            case "'code %d, message %s'", _:
                pass
            case _:
                # print(repr(format_), args)
                # super().log_message(format_, *args)
                pass


def _run_server():
    server = http.server.ThreadingHTTPServer(('', 8000), Handler)
    server.serve_forever()


@pytest.fixture(scope="session", autouse=True)
def index_server():
    Thread(target=_run_server, daemon=True).start()
