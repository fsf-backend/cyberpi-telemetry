#!/usr/bin/env python3

import json
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from collectors import collect


LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 8080


class StatusHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path != "/status":
            self.send_response(404)
            self.end_headers()
            return

        payload = json.dumps(
            collect()
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(payload))
        )
        self.end_headers()

        self.wfile.write(payload)

    def log_message(self, *_):
        pass


def main():

    server = HTTPServer(
        (LISTEN_IP, LISTEN_PORT),
        StatusHandler
    )

    print(
        f"CyberPi SOC Agent listening on "
        f"{LISTEN_IP}:{LISTEN_PORT}"
    )

    server.serve_forever()


if __name__ == "__main__":
    main()
