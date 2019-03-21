"""Serve application."""
from wsgiref.simple_server import make_server

from readable_api import build_wsgi


def serve(app, host="0.0.0.0", port=8888):
    """Serve a WSGI app at host:port."""
    server = make_server(host, port, app)
    print(f"Starting server at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    app = build_wsgi()
    serve(app)
