---
title: 06 - One-Shot Web Servers for Payload Delivery and Callbacks
description: |-
  A practical look at building minimal, disposable web servers inside OSWE PoC scripts.
  This article covers one-shot HTTP servers for payload delivery, blind callbacks, and data
  exfiltration, focusing on simplicity, control, and stage-level integration rather than
  full infrastructure.
author: Roger Dooley
series: Building Robust OSWE PoCs
part: 6
topics:
  - exploit development
  - one-shot web servers
  - payload delivery
  - blind callbacks
  - poc tooling
prerequisites:
  - argparse
  - basic python classes
  - http basics (GET requests)
  - exploit staging concepts
related:
  - 02 - Argument Parsing for OSWE PoCs - argparse vs dotenv
  - 03 - Context Management with Dataclasses
  - 04 - Control Flow and Stage Management in OSWE PoCs
  - 05 - Structured Logging for Exploit Development
next: 07 - Asynchronous Execution for Request-Heavy Exploit Stages
---


Over the next three articles, I want to walk through a few patterns and techniques that I found genuinely helpful throughout the labs. Each tool or concept reduced friction during exploit development, either by simplifying the PoC or by speeding up execution. This isn't about infrastructure building, but optimizing and automating processes. 

As a starting point, let's look at the exam requirements. When running a PoC, you are allowed to initiate listeners and a web server prior to executing the exploit code ([Exam Requirements](https://help.offsec.com/hc/en-us/articles/360046869951-WEB-300-Advanced-Web-Attacks-and-Exploitation-OSWE-Exam-Guide#section-1-exam-requirements)). Let's focus on the web server initiation. There are a myriad of web servers to choose from: Apache, Python, etc... For most, the simplest option is executing `python3 -m http.server` which serves HTTP traffic over port 8000 by default.

Not every PoC needs a running web server. However, if a stage involves data exfiltration , serving payloads, or handling blind callbacks, a server is usually required. Standing one up manually is easy enough, but doing so introduces an extra step for yourself or someone else running the exploit. Additionally, for these contrived course web applications, the automated admin or user will end up continuously calling back to your server and possibly re-running code that calls back to the attacking machine. If all that is needed is a single request from the target or the attacker, managing a separate server process starts to feel unnecessary. This is where a one-shot web server becomes useful.

Standing up a web server in code can be accomplished in many ways. When deciding how to approach this, I only had two criteria:
1. Lightweight with minimal fuss
2. Detection of payload delivery or reception in order to tear down the server
My first iteration, which I'll present here, used [`http.server`](https://docs.python.org/3/library/http.server.html) mainly because it is part of the Python standard library. Eventually, I ended up writing a flexible one-shot server that handled more use cases than required for the course labs. I'm not going to show the resulting library I created using [Flask](https://flask.palletsprojects.com/en/stable/) for the backing server because doing so would require a series of articles in it's own right. 

The example below shows one way to solve this problem. It is intentionally simple and includes a basic guard in place which checks the IP Address of the requester. If the request doesn't originate from the expected host, then the web server responds with a 403 and continues waiting. Once the payload is correctly served to the correct host, the server shuts down. In a full PoC, this would typically mark the end of a stage and trigger the next step in the exploit chain.

To start, we'll define what functionality is actually required. In the simplest case, support for the `GET` method is sufficient. The `http.server` module provides a straightforward way to do this by subclassing `BaseHTTPRequestHandler` and overriding the `do_GET` method.

`BaseHTTPRequestHandler` defines the default behavior for handling HTTP requests and responses. It is designed to be subclassed so that specific methods can be overridden. By implementing `do_GET`, we gain full control over how incoming requests are handled. This also allows flexibility in how the endpoint is exposed. For example, the path could be randomized on each run to make the delivery less predictable. In this example, the path is fixed to /exploit for clarity.

`OneShotSever` could be written to accept requests from any source, but we can implement minimal safeguards trivially. One simple measure it to implement a restriction to which IP Address can receive the payload. This is accomplished by defining an allowed host (`allowed_host`) and comparing it to the source address of the incoming request. If they do not match, the server responds with a 403 and continues to run.

A second restriction is enforcing a specific request path. If the IP address is valid but the path does not match, a 404 response is returned. When both checks pass, the payload is delivered. In this example, a URL-safe random string is written to a file and served as the response body.

After parsing arguments, the PoC initializes `allowed_host` and `payload_path` on the handler class. The HTTP server is started on the specified address and port. A `should_stop` flag is initialized to `False`. Once a payload is successfully served, the flag is set to `True`. A loop checks this value and shuts down the server when the delivery has occurred. In practice, this logic would live inside a single exploit stage.


```python
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

```

Running the one-shot-server so that only requests from `192.168.1.97` are allowed.

```bash
uv run poc-one-shot-server.py --target-ip 192.168.1.97 --listening-ip 0.0.0.0 --payload-port 8000
Target IP: 192.168.1.97
Target Port: 80
Listening IP: 0.0.0.0
Payload Port: 8000
2026-01-16 15:45:36,625 - INFO - rejecting host 192.168.1.105
192.168.1.105 - - [16/Jan/2026 15:45:36] code 403, message Forbidden
192.168.1.105 - - [16/Jan/2026 15:45:36] "GET /exploit HTTP/1.1" 403 -
2026-01-16 15:45:43,661 - INFO - rejecting host 127.0.0.1
127.0.0.1 - - [16/Jan/2026 15:45:43] code 403, message Forbidden
127.0.0.1 - - [16/Jan/2026 15:45:43] "GET /exploit HTTP/1.1" 403 -
192.168.1.97 - - [16/Jan/2026 15:45:51] "GET /exploit HTTP/1.1" 200 -

```

Trying from host `192.168.1.105` (which is also `localhost`).

```bash
 curl http://192.168.1.105:8000/exploit
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 403</p>
        <p>Message: Forbidden.</p>
        <p>Error code explanation: 403 - Request forbidden -- authorization will not help.</p>
    </body>
</html>
❯ curl http://127.0.0.1:8000/exploit
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 403</p>
        <p>Message: Forbidden.</p>
        <p>Error code explanation: 403 - Request forbidden -- authorization will not help.</p>
    </body>
</html>
❯ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:1c:42:65:46:6e brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.105/24 brd 192.168.1.255 scope global dynamic noprefixroute eth0
       valid_lft 64963sec preferred_lft 64963sec
    inet6 fe80::21c:42ff:fe65:466e/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever

```

Now run `curl` from the allowed host.

```bash
❯ curl http://192.168.1.105:8000/exploit
Ibl_M5DNukPLIfzYppWxn01Rsyxp8jFdRg76YgdgjC3ks6WSFsHFUIJShV9fsDsb7wEC47-GF3ihI-fw_Ng0AQ%
❯ ifconfig | grep 97
	inet 192.168.1.97 netmask 0xffffff00 broadcast 192.168.1.255
```

There are other ways to stand up a web server using Python. Frameworks like [Flask](https://flask.palletsprojects.com/en/stable/)or even [wsgiref.simple_server](https://docs.python.org/3/library/wsgiref.html#module-wsgiref.simple_server) can be used if more flexibility is required beyond simple HTTP requests. This might include receiving data via POST, handling exfiltration, or uploading payloads as part of a command injection or deserialization chain. Expanding on the ideas presented here opens up a number of useful extensions, including:
- Handles GET/POST requests for raw or base64-encoded data
- Enforcing one-time or limited-use transfers
- Gracefully shuts down after a successful transfer or via a local trigger
- Providing a simple HTML landing page for download links
- Randomizing routes for each PoC run
- Supporting custom callbacks to trigger the next exploit stage

At this point, we’ve solved a very specific problem: standing up just enough infrastructure to deliver or receive exactly one piece of data and then disappear. The one-shot web server is intentionally simple, synchronous, and short-lived. It blocks, it waits, and once its job is done, it shuts down.

That simplicity is a feature, not a limitation. For payload delivery, callbacks, and blind exfiltration triggers, predictability matters more than throughput.

However, not every stage of an exploit has that shape.

Some stages are not about waiting for a single request, but about making hundreds or thousands of them: brute-forcing tokens, extracting secrets character by character, or probing timing-based side channels. In those cases, the bottleneck is no longer logic or setup, but time.

 In the [next article](<07 – Asynchronous Execution for Request-Heavy Exploit Stages.md>), we’ll shift focus away from infrastructure and look at asynchronous execution as a tool for accelerating request-heavy stages. Async isn’t a replacement for the patterns we’ve built so far. It’s an optimization applied selectively, when a stage demands it.
