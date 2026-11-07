"""Serve a Unity Web build on this computer with the required gzip and WASM headers."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class UnityWebHandler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".wasm": "application/wasm", ".data": "application/octet-stream"}

    def guess_type(self, path):
        return super().guess_type(path[:-3] if path.endswith(".gz") else path)

    def end_headers(self):
        if urlsplit(self.path).path.endswith(".gz"):
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--port", type=int, default=18767)
    args = parser.parse_args()
    if not (args.directory / "index.html").is_file():
        parser.error("directory must contain the Unity build's index.html")
    with ThreadingHTTPServer(("127.0.0.1", args.port), partial(UnityWebHandler, directory=str(args.directory.resolve()))) as server:
        print(f"Unity browser preview: http://127.0.0.1:{args.port}/", flush=True)
        server.serve_forever()
