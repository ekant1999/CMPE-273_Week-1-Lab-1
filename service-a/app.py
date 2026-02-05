"""
Service A (Echo API) - CMPE 273 Week 1 Lab 1
Runs on localhost:8080. Exposes /health and /echo.
No external dependencies (stdlib only).
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import json
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SERVICE_NAME = "service-a"
HOST = "127.0.0.1"
PORT = 8080


class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.perf_counter()
        parsed = urlparse(self.path)
        endpoint = parsed.path

        if endpoint == "/health":
            status_code = 200
            payload = {"status": "ok"}
        elif endpoint == "/echo":
            msg = parse_qs(parsed.query).get("msg", [""])[0]
            status_code = 200
            payload = {"echo": msg}
        else:
            status_code = 404
            payload = {"error": "not found"}

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

        latency_ms = int((time.perf_counter() - start) * 1000)
        status_label = "ok" if status_code == 200 else "error"
        logger.info(
            f"service={SERVICE_NAME} endpoint={endpoint} status={status_label} latency_ms={latency_ms}"
        )

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), EchoHandler)
    logger.info(f"service={SERVICE_NAME} startup host={HOST} port={PORT}")
    server.serve_forever()
