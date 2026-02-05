"""
Service B (Client) - CMPE 273 Week 1 Lab 1
Runs on localhost:8081. Exposes /health and /call-echo (calls Service A with timeout).
No external dependencies (stdlib only).
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen
import json
import logging
import socket
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SERVICE_NAME = "service-b"
SERVICE_A_URL = "http://127.0.0.1:8080"
ECHO_TIMEOUT_SEC = 2.0
HOST = "127.0.0.1"
PORT = 8081


class ClientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.perf_counter()
        parsed = urlparse(self.path)
        endpoint = parsed.path

        if endpoint == "/health":
            status_code = 200
            payload = {"status": "ok"}
            self._write_json(status_code, payload)
            self._log_ok(endpoint, start)
            return

        if endpoint == "/call-echo":
            msg = parse_qs(parsed.query).get("msg", [""])[0]
            try:
                target_url = f"{SERVICE_A_URL}/echo?msg={quote(msg)}"
                with urlopen(target_url, timeout=ECHO_TIMEOUT_SEC) as resp:
                    body = resp.read().decode("utf-8")
                data = json.loads(body)
                status_code = 200
                payload = {"service_b": "ok", "service_a": data}
                self._write_json(status_code, payload)
                self._log_ok(endpoint, start)
                return
            except HTTPError as e:
                error_msg = f"Service A returned HTTP {e.code}"
            except URLError as e:
                if isinstance(e.reason, socket.timeout):
                    error_msg = f"timeout after {ECHO_TIMEOUT_SEC}s"
                else:
                    error_msg = "Service A unreachable (connection refused or down)"
            except socket.timeout:
                error_msg = f"timeout after {ECHO_TIMEOUT_SEC}s"
            except Exception as e:
                error_msg = str(e)

            status_code = 503
            payload = {
                "service_b": "ok",
                "service_a": "unavailable",
                "error": error_msg,
            }
            self._write_json(status_code, payload)
            self._log_error(endpoint, start, error_msg)
            return

        status_code = 404
        payload = {"error": "not found"}
        self._write_json(status_code, payload)
        self._log_error(endpoint, start, "not found")

    def _write_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _log_ok(self, endpoint, start):
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            f"service={SERVICE_NAME} endpoint={endpoint} status=ok latency_ms={latency_ms}"
        )

    def _log_error(self, endpoint, start, error_msg):
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.error(
            f"service={SERVICE_NAME} endpoint={endpoint} status=error error=\"{error_msg}\" latency_ms={latency_ms}"
        )

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ClientHandler)
    logger.info(f"service={SERVICE_NAME} startup host={HOST} port={PORT}")
    server.serve_forever()
