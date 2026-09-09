"""Локальний сервер: віддає проєкт і приймає готовий PNG від генератора."""
import http.server, pathlib, socketserver

ROOT = pathlib.Path(r"D:\creation\site saas")
TARGET = ROOT / "assets" / "og-image.png"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def do_POST(self):
        if self.path != "/save-og":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", 0))
        TARGET.write_bytes(self.rfile.read(n))
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"saved {n} bytes".encode())
        print(f"[og] wrote {n} bytes -> {TARGET}")

    def log_message(self, *a):
        pass


with socketserver.TCPServer(("127.0.0.1", 8790), Handler) as httpd:
    print("serving on 8790")
    httpd.serve_forever()
