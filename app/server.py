"""DevUtils API server - Zero external dependencies, uses only Python stdlib.

A lightweight REST API providing developer utilities.
Ready for deployment and RapidAPI marketplace.
"""

import json
import os
import re
import hashlib
import uuid
import base64
import io
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional


# ─── Configuration ────────────────────────────────────────────────────────────

class Config:
    API_KEY = os.environ.get("API_KEY", "devutils-secret-2ae7436568540215")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8080"))
    APP_NAME = "DevUtils API"
    APP_VERSION = "1.0.0"
    DEBUG = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")


config = Config()


# ─── Authentication ───────────────────────────────────────────────────────────

def verify_auth(headers: dict) -> Optional[str]:
    """Verify API key from X-Api-Key or X-RapidAPI-Proxy-Secret header."""
    if not config.API_KEY:
        return None  # No auth required
    api_key = headers.get("x-api-key") or headers.get("x-rapidapi-proxy-secret")
    if not api_key:
        return "Missing API key"
    if api_key != config.API_KEY:
        return "Invalid API key"
    return None


# ─── JSON helpers ─────────────────────────────────────────────────────────────

def json_response(data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return (status, {"Content-Type": "application/json"}, body)


def error_response(message, status=400):
    return json_response({"success": False, "error": message}, status)


# ─── Route handlers ────────────────────────────────────────────────────────────

def handle_root(query, body, headers):
    return json_response({
        "status": "ok",
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "qr": {
                "generate": "GET /qr/generate?data=...&size=10&border=4",
            },
            "text": {
                "slugify": "GET /text/slugify?text=...",
                "hash": "GET /text/hash?text=...&algorithm=sha256",
                "case": "GET /text/case?text=...&to=upper",
                "count": "GET /text/count?text=...",
            },
            "data": {
                "uuid": "GET /data/uuid",
                "base64-encode": "GET /data/base64/encode?text=...",
                "base64-decode": "GET /data/base64/decode?text=...",
                "json-validate": "POST /data/json/validate",
            },
        },
    })


def handle_health(query, body, headers):
    return json_response({"status": "healthy"})


def handle_docs(query, body, headers):
    """Return HTML documentation page."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{config.APP_NAME} - Docs</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0d1117; color: #c9d1d9; max-width: 900px; margin: 0 auto; padding: 2rem; }}
  h1 {{ color: #58a6ff; margin-bottom: 0.5rem; }}
  h2 {{ color: #f0f6fc; margin: 2rem 0 1rem; border-bottom: 1px solid #30363d; padding-bottom: 0.5rem; }}
  h3 {{ color: #f0f6fc; margin: 1.5rem 0 0.5rem; }}
  code {{ background: #161b22; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.9em; color: #f0f6fc; }}
  pre {{ background: #161b22; padding: 1rem; border-radius: 6px; overflow-x: auto; margin: 0.5rem 0; }}
  pre code {{ background: none; padding: 0; }}
  .endpoint {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1rem; margin: 0.5rem 0; }}
  .method {{ display: inline-block; font-weight: bold; padding: 0.2em 0.6em; border-radius: 4px; font-size: 0.85em; }}
  .get {{ background: #1f6feb22; color: #58a6ff; border: 1px solid #1f6feb44; }}
  .post {{ background: #23863622; color: #3fb950; border: 1px solid #23863644; }}
  .path {{ font-family: monospace; margin-left: 0.5rem; }}
  .desc {{ margin-top: 0.5rem; color: #8b949e; font-size: 0.9rem; }}
  .param {{ margin: 0.25rem 0 0.25rem 1rem; font-size: 0.85rem; color: #8b949e; }}
  hr {{ border: none; border-top: 1px solid #30363d; margin: 2rem 0; }}
  footer {{ text-align: center; color: #8b949e; font-size: 0.85rem; margin-top: 3rem; }}
</style>
</head>
<body>
<h1>{config.APP_NAME}</h1>
<p>A collection of handy developer utilities exposed as a simple REST API.</p>
<p>Version: {config.APP_VERSION}</p>

<h2>Authentication</h2>
<p>Send API key via <code>X-Api-Key</code> header or <code>X-RapidAPI-Proxy-Secret</code> when proxied through RapidAPI.</p>

<h2>Endpoints</h2>

<h3>QR Code</h3>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/qr/generate?data=URL&size=10&border=4&fill_color=%23000000&back_color=%23FFFFFF</span>
  <div class="desc">Generate a QR code image (PNG).</div>
  <div class="param"><code>data</code> (required) - Text or URL to encode</div>
  <div class="param"><code>size</code> (optional, default 10) - Box size in pixels per module</div>
  <div class="param"><code>border</code> (optional, default 4) - Border width in modules</div>
  <div class="param"><code>fill_color</code> (optional, default #000000) - QR code foreground color</div>
  <div class="param"><code>back_color</code> (optional, default #FFFFFF) - QR code background color</div>
</div>

<h3>Text Utilities</h3>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/text/slugify?text=Hello World&separator=-</span>
  <div class="desc">Convert text to URL-friendly slug. Returns JSON with original and slug.</div>
</div>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/text/hash?text=hello&algorithm=sha256</span>
  <div class="desc">Hash text using md5, sha1, sha256, or sha512.</div>
</div>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/text/case?text=hello_world&to=camel</span>
  <div class="desc">Convert text case: upper, lower, title, camel, snake, kebab.</div>
</div>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/text/count?text=Hello world. How are you?</span>
  <div class="desc">Count characters, words, sentences, and paragraphs.</div>
</div>

<h3>Data Utilities</h3>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/data/uuid</span>
  <div class="desc">Generate a UUID v4.</div>
</div>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/data/base64/encode?text=hello</span>
  <div class="desc">Encode text to Base64.</div>
</div>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/data/base64/decode?text=aGVsbG8=</span>
  <div class="desc">Decode Base64 to text.</div>
</div>
<div class="endpoint">
  <span class="method post">POST</span><span class="path">/data/json/validate</span>
  <div class="desc">Validate and pretty-print JSON. Send JSON string in body.</div>
</div>

<h2>Health</h2>
<div class="endpoint">
  <span class="method get">GET</span><span class="path">/health</span>
  <div class="desc">Health check endpoint.</div>
</div>

<hr>
<footer>Powered by Python stdlib | Ready for RapidAPI</footer>
</body>
</html>"""
    return (200, {"Content-Type": "text/html; charset=utf-8"}, html.encode("utf-8"))


def handle_qr_generate(query, body, headers):
    """Generate QR code using a pure-Python algorithm.
    Returns a PNG image.
    """
    data = query.get("data", [None])[0]
    if not data:
        return error_response("Missing required parameter: data")

    try:
        size = int(query.get("size", ["10"])[0])
        border = int(query.get("border", ["4"])[0])
    except ValueError:
        return error_response("size and border must be integers")

    fill_color = query.get("fill_color", ["#000000"])[0]
    back_color = query.get("back_color", ["#FFFFFF"])[0]

    # Pure Python QR code generation using the built-in approach
    # We use a minimal QR code implementation
    try:
        png_data = generate_qr_png(data, size=size, border=border,
                                   fill_color=fill_color, back_color=back_color)
        return (200, {"Content-Type": "image/png"}, png_data)
    except Exception as e:
        return error_response(f"QR generation failed: {str(e)}", 500)


def handle_text_slugify(query, body, headers):
    text = query.get("text", [None])[0]
    if text is None:
        return error_response("Missing required parameter: text")
    separator = query.get("separator", ["-"])[0]

    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s" + re.escape(separator) + r"]", "", slug)
    slug = re.sub(r"\s+", separator, slug)
    slug = re.sub(r"\-+", "-", slug)
    slug = slug.strip(separator)

    return json_response({"original": text, "slug": slug, "separator": separator})


def handle_text_hash(query, body, headers):
    text = query.get("text", [None])[0]
    if text is None:
        return error_response("Missing required parameter: text")
    algorithm = query.get("algorithm", ["sha256"])[0]

    alg_map = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }

    if algorithm not in alg_map:
        return error_response(f"Unsupported algorithm: {algorithm}. Use: md5, sha1, sha256, sha512")

    hash_obj = alg_map[algorithm](text.encode("utf-8"))
    return json_response({
        "algorithm": algorithm,
        "input": text,
        "hash": hash_obj.hexdigest(),
    })


def handle_text_case(query, body, headers):
    text = query.get("text", [None])[0]
    if text is None:
        return error_response("Missing required parameter: text")
    to = query.get("to", ["upper"])[0]

    result = text
    if to == "upper":
        result = text.upper()
    elif to == "lower":
        result = text.lower()
    elif to == "title":
        result = text.title()
    elif to == "camel":
        words = re.sub(r"[^a-zA-Z0-9]", " ", text).split()
        if words:
            result = words[0].lower() + "".join(w.capitalize() for w in words[1:])
    elif to == "snake":
        result = re.sub(r"[^a-zA-Z0-9]", "_", text).lower()
        result = re.sub(r"_+", "_", result).strip("_")
    elif to == "kebab":
        result = re.sub(r"[^a-zA-Z0-9]", "-", text).lower()
        result = re.sub(r"-+", "-", result).strip("-")
    else:
        return error_response(f"Unsupported case: {to}")

    return json_response({"original": text, "converted": result, "case": to})


def handle_text_count(query, body, headers):
    text = query.get("text", [None])[0]
    if text is None:
        return error_response("Missing required parameter: text")

    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    word_count = len(text.split()) if text.strip() else 0
    sentence_count = len(re.split(r"[.!?]+", text)) - 1 if text.strip() else 0
    paragraph_count = len([p for p in text.split("\n\n") if p.strip()]) if text.strip() else 0

    return json_response({
        "characters": char_count,
        "characters_no_spaces": char_count_no_spaces,
        "words": word_count,
        "sentences": max(0, sentence_count),
        "paragraphs": max(1, paragraph_count),
    })


def handle_data_uuid(query, body, headers):
    return json_response({"uuid": str(uuid.uuid4()), "version": 4})


def handle_base64_encode(query, body, headers):
    text = query.get("text", [None])[0]
    if text is None:
        return error_response("Missing required parameter: text")
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return json_response({"original": text, "encoded": encoded})


def handle_base64_decode(query, body, headers):
    text = query.get("text", [None])[0]
    if text is None:
        return error_response("Missing required parameter: text")
    try:
        decoded = base64.b64decode(text.encode("ascii")).decode("utf-8")
        return json_response({"original": text, "decoded": decoded})
    except Exception as e:
        return error_response(f"Invalid Base64 input: {str(e)}")


def handle_json_validate(query, body, headers):
    if not body:
        return error_response("Request body is required")
    try:
        parsed = json.loads(body)
        pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
        return json_response({
            "valid": True,
            "pretty": pretty,
            "type": type(parsed).__name__,
        })
    except json.JSONDecodeError as e:
        return json_response({
            "valid": False,
            "error": str(e),
            "position": e.pos,
            "line": e.lineno,
            "column": e.colno,
        })


# ─── Minimal QR Code Generator (pure Python) ─────────────────────────────────

def generate_qr_png(data: str, size: int = 10, border: int = 4,
                    fill_color: str = "#000000", back_color: str = "#FFFFFF") -> bytes:
    """Generate a QR code PNG using a minimal pure-Python implementation."""
    from .minimal_qr import MinimalQR
    qr = MinimalQR(data)
    matrix = qr.get_matrix()

    # Calculate dimensions
    module_count = len(matrix)
    img_size = (module_count + 2 * border) * size

    # Parse colors
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    fill = hex_to_rgb(fill_color)
    back = hex_to_rgb(back_color)

    # Build raw pixel data (RGBA)
    pixels = bytearray()
    for row_idx in range(img_size):
        for col_idx in range(img_size):
            # Check if this pixel is a QR module
            r = (row_idx // size) - border
            c = (col_idx // size) - border
            if 0 <= r < module_count and 0 <= c < module_count and matrix[r][c]:
                pixels.extend(fill)
                pixels.extend([255])  # Alpha
            else:
                pixels.extend(back)
                pixels.extend([255])

    # Write PNG manually
    return _write_png(pixels, img_size, img_size)


def _write_png(pixels, width, height):
    """Write a minimal valid PNG file."""
    import struct
    import zlib

    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)

    # IDAT chunk - raw pixel data
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # Filter byte (none)
        for x in range(width):
            offset = (y * width + x) * 4
            raw.extend(pixels[offset:offset + 4])
    compressed = zlib.compress(bytes(raw))

    # IEND chunk
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


# ─── Router ───────────────────────────────────────────────────────────────────

ROUTES = {
    ("GET", "/"): handle_root,
    ("GET", "/health"): handle_health,
    ("GET", "/docs"): handle_docs,
    ("GET", "/qr/generate"): handle_qr_generate,
    ("POST", "/qr/generate"): handle_qr_generate,
    ("GET", "/text/slugify"): handle_text_slugify,
    ("GET", "/text/hash"): handle_text_hash,
    ("GET", "/text/case"): handle_text_case,
    ("GET", "/text/count"): handle_text_count,
    ("GET", "/data/uuid"): handle_data_uuid,
    ("GET", "/data/base64/encode"): handle_base64_encode,
    ("GET", "/data/base64/decode"): handle_base64_decode,
    ("POST", "/data/json/validate"): handle_json_validate,
}


def route(method, path, query, body, headers):
    handler = ROUTES.get((method, path))
    if handler:
        return handler(query, body, headers)
    return error_response(f"Not found: {method} {path}", 404)


# ─── HTTP Handler ────────────────────────────────────────────────────────────

class DevUtilsHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if config.DEBUG:
            super().log_message(format, *args)

    def _handle_request(self, method):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

        # Normalize headers to lowercase keys
        headers = {k.lower(): v for k, v in self.headers.items()}

        # Auth check
        auth_error = verify_auth(headers)
        if auth_error:
            status, resp_hdrs, resp_body = error_response(auth_error, 401)
            self._send_response(status, resp_hdrs, resp_body)
            return

        # Route the request
        try:
            status, resp_hdrs, resp_body = route(method, path, query, body, headers)
        except Exception as e:
            if config.DEBUG:
                traceback.print_exc()
            err_msg = str(e) if config.DEBUG else "Internal server error"
            status, resp_hdrs, resp_body = error_response(err_msg, 500)
            if resp_hdrs is None:
                resp_hdrs = {}

        self._send_response(status, resp_hdrs, resp_body)

    def _send_response(self, status, headers_dict, body):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key, X-RapidAPI-Proxy-Secret")
        if headers_dict:
            for k, v in headers_dict.items():
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key, X-RapidAPI-Proxy-Secret")
        self.end_headers()


def start():
    server = HTTPServer((config.HOST, config.PORT), DevUtilsHandler)
    print(f"🌐 {config.APP_NAME} v{config.APP_VERSION}")
    print(f"   Listening on http://{config.HOST}:{config.PORT}")
    print(f"   Docs:      http://localhost:{config.PORT}/docs")
    print(f"   Health:    http://localhost:{config.PORT}/health")
    if config.API_KEY:
        print(f"   Auth:      API key required (X-Api-Key header)")
    else:
        print("   Auth:      DISABLED (set API_KEY env var to enable)")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    start()
