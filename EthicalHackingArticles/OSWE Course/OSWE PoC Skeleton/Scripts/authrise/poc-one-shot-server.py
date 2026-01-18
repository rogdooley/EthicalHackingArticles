import argparse
import logging
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class OneShotServer(BaseHTTPRequestHandler):
    allowed_host: str = ""
    payload_path: Path

    def do_GET(self):
        client_ip = self.client_address[0]

        if client_ip != self.allowed_host:
            logging.info(f"rejecting host {client_ip}")
            self.send_error(403)
            return

        if self.path != "/exploit":
            logging.info(f"invalid path {self.path} from {client_ip}")
            self.send_error(404)
            return

        data = self.payload_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

        self.server.should_stop = True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Minimal PoC with One-shot HTTP Server."
    )

    # --- Target options ---
    target_group = parser.add_argument_group("Target options")
    target_group.add_argument(
        "--target-ip", type=str, required=True, help="Target server IP address"
    )
    target_group.add_argument(
        "--target-port",
        type=int,
        default=80,
        help="Target web frontend port (default: 80)",
    )
    target_group.add_argument(
        "--target-api-port",
        type=int,
        default=5000,
        help="Target API port (default: 5000)",
    )

    # --- Attacker options ---
    attacker_group = parser.add_argument_group("Attacker options")
    attacker_group.add_argument(
        "--listening-ip",
        type=str,
        default="127.0.0.1",
        help="IP to listen on for reverse shell (default: 127.0.0.1)",
    )
    attacker_group.add_argument(
        "--listening-port",
        type=int,
        default=9001,
        help="Port to listen for reverse shell (default: 9001)",
    )
    attacker_group.add_argument(
        "--payload-port",
        type=int,
        default=9999,
        help="Port to listen for xss or other payload (default: 9999)",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Target IP: {args.target_ip}")
    print(f"Target Port: {args.target_port}")
    print(f"Listening IP: {args.listening_ip}")
    print(f"Payload Port: {args.payload_port}")

    secret_string = secrets.token_urlsafe(64)
    payload = Path("payload.txt")
    payload.write_text(secret_string)

    # start http server
    OneShotServer.allowed_host = args.target_ip
    OneShotServer.payload_path = payload

    httpd = HTTPServer((args.listening_ip, args.payload_port), OneShotServer)
    httpd.should_stop = False

    while not httpd.should_stop:
        httpd.handle_request()

    httpd.server_close()

    Path("payload.txt").unlink()


if __name__ == "__main__":
    main()
