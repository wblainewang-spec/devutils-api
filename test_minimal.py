"""Minimal socket server for Railway deployment debugging."""
import sys
import os
import socket
import select

sys.stderr.write("=== minimal server starting ===\n")
sys.stderr.flush()

port = int(os.environ.get("PORT", 8080))
sys.stderr.write(f"Creating socket on port {port}...\n")
sys.stderr.flush()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    s.listen(128)
    s.setblocking(False)
    sys.stderr.write(f"Socket listening on 0.0.0.0:{port}\n")
    sys.stderr.flush()
except Exception as e:
    sys.stderr.write(f"FAILED to create socket: {e}\n")
    import traceback as tb
    tb.print_exc()
    sys.stderr.flush()
    raise

response = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 17\r\n\r\n{\"status\":\"ok\"}"
counter = 0

sys.stderr.write("=== entering accept loop ===\n")
sys.stderr.flush()

try:
    while True:
        r, _, _ = select.select([s], [], [], 1.0)
        if r:
            conn, addr = s.accept()
            counter += 1
            sys.stderr.write(f"Request #{counter} from {addr}\n")
            sys.stderr.flush()
            try:
                data = conn.recv(4096)
                sys.stderr.write(f"  Data: {data[:100]}...\n")
                sys.stderr.flush()
                conn.sendall(response)
            except Exception as e:
                sys.stderr.write(f"  Error handling request: {e}\n")
                sys.stderr.flush()
            finally:
                conn.close()
except KeyboardInterrupt:
    sys.stderr.write("Shutting down...\n")
    sys.stderr.flush()
    s.close()
