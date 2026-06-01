"""Minimal test server for Railway deployment."""
import sys, os

sys.stderr.write("=== test_railway starting ===\n")
sys.stderr.write(f"Python: {sys.version}\n")
sys.stderr.write(f"PORT: {os.environ.get('PORT', 'NOT SET')}\n")
sys.stderr.write(f"PWD: {os.getcwd()}\n")
sys.stderr.write(f"Files: {os.listdir('.')}\n")
sys.stderr.flush()

port = int(os.environ.get("PORT", 8080))

from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        sys.stderr.write(f"Got request: {self.path}\n")
        sys.stderr.flush()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    def log_message(self, *a):
        pass

sys.stderr.write(f"Binding to 0.0.0.0:{port}...\n")
sys.stderr.flush()

try:
    server = HTTPServer(("0.0.0.0", port), Handler)
    sys.stderr.write(f"Serving on port {port}...\n")
    sys.stderr.flush()
    server.serve_forever()
except Exception as e:
    import traceback
    sys.stderr.write(f"Error: {e}\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    raise
