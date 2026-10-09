
import asyncio
import threading
import time
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)

import httpx


REQUEST_COUNT = 8
DELAY_SECONDS = 0.2
CONCURRENCY_LIMIT = 3


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/delay":
            self.send_error(404)
            return

        time.sleep(DELAY_SECONDS)

        try:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        except (BrokenPipeError, ConnectionResetError):
            # 客户端超时或取消后可能关闭连接
            pass

    def log_message(self, format, *args):
        pass


def start_server():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        DemoHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    url = f"http://127.0.0.1:{server.server_port}/delay"
    return server, thread, url


def run_sync(url):
    start = time.perf_counter()

    with httpx.Client(timeout=5.0) as client:
        for _ in range(REQUEST_COUNT):
            response = client.get(url)
            response.raise_for_status()

    return time.perf_counter() - start


async def run_async(url):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    active = 0
    peak = 0

    async with httpx.AsyncClient(timeout=5.0) as client:

        async def fetch(index):
            nonlocal active, peak

            async with semaphore:
                active += 1
                peak = max(peak, active)

                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text
                finally:
                    active -= 1

        start = time.perf_counter()

        results = await asyncio.gather(
            *(fetch(i) for i in range(REQUEST_COUNT))
        )

        elapsed = time.perf_counter() - start

    assert len(results) == REQUEST_COUNT
    assert all(result == "ok" for result in results)
    assert peak <= CONCURRENCY_LIMIT

    return elapsed, peak


async def test_timeout(url):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(0.05)
    ) as client:
        try:
            await client.get(url)
        except httpx.TimeoutException:
            print("Timeout: PASSED")
            return

    raise AssertionError("Expected timeout")


async def test_cancellation(url):
    async with httpx.AsyncClient(timeout=5.0) as client:

        async def slow_request():
            return await client.get(url)

        task = asyncio.create_task(slow_request())

        # 给请求少量时间开始执行
        await asyncio.sleep(0.02)

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            print("Cancellation: PASSED")
            return

    raise AssertionError("Expected cancellation")


async def main(url):
    sync_time = await asyncio.to_thread(run_sync, url)
    async_time, peak = await run_async(url)

    print(f"Sync:  {sync_time:.3f}s")
    print(f"Async: {async_time:.3f}s")
    print(f"Peak concurrency: {peak}")

    await test_timeout(url)
    await test_cancellation(url)


if __name__ == "__main__":
    server, thread, url = start_server()

    try:
        asyncio.run(main(url))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
