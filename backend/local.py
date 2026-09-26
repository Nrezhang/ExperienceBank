"""In-memory API for local React development. Data resets when this process stops."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import app


class MemoryTable:
    def __init__(self):
        self.items = {}

    def scan(self):
        return {"Items": list(self.items.values())}

    def put_item(self, Item):
        self.items[Item["id"]] = Item

    def delete_item(self, Key):
        self.items.pop(Key["id"], None)


app._table = lambda: TABLE
TABLE = MemoryTable()


class ApiHandler(BaseHTTPRequestHandler):
    def _handle(self):
        path = urlsplit(self.path).path
        if path == "/api/items" and self.command in ("GET", "POST"):
            route_key = f"{self.command} /api/items"
            path_parameters = {}
        elif path.startswith("/api/items/") and self.command == "DELETE":
            route_key = "DELETE /api/items/{id}"
            path_parameters = {"id": path.rsplit("/", 1)[1]}
        else:
            route_key = ""
            path_parameters = {}

        length = int(self.headers.get("Content-Length", "0"))
        event = {
            "routeKey": route_key,
            "pathParameters": path_parameters,
            "body": self.rfile.read(length).decode("utf-8") if length else None,
        }
        result = app.handler(event, None)
        body = result.get("body", "").encode("utf-8")
        self.send_response(result["statusCode"])
        for key, value in result.get("headers", {}).items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = _handle
    do_POST = _handle
    do_DELETE = _handle


if __name__ == "__main__":
    print("Local API listening at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), ApiHandler).serve_forever()
