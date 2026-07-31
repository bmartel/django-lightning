"""
High-Performance Benchmark Script for django-lightning / django-bolt.
Measures realistic median throughput (RPS), p50, p95, p99 latency across endpoints.
"""

import argparse
import asyncio
import statistics
import time


async def send_request(reader, writer, path, host="127.0.0.1"):
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: benchmark/1.0\r\n"
        f"Accept: */*\r\n"
        f"Connection: keep-alive\r\n\r\n"
    )
    start = time.perf_counter()
    writer.write(req.encode("utf-8"))
    await writer.drain()

    # Read response status header
    line = await reader.readline()
    status_code = 200
    if line:
        parts = line.decode("utf-8", errors="ignore").split(" ")
        if len(parts) > 1:
            try:
                status_code = int(parts[1])
            except ValueError:
                pass

    content_length = 0
    while True:
        header = await reader.readline()
        if not header or header == b"\r\n":
            break
        header_str = header.decode("utf-8", errors="ignore").lower()
        if header_str.startswith("content-length:"):
            try:
                content_length = int(header_str.split(":")[1].strip())
            except ValueError:
                pass

    if content_length > 0:
        await reader.readexactly(content_length)

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return elapsed_ms, status_code


async def worker(host, port, path, num_requests, results, status_counts):
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    for _ in range(num_requests):
        try:
            latency, status = await send_request(reader, writer, path, host)
            results.append(latency)
            status_counts[status] = status_counts.get(status, 0) + 1
        except Exception:
            # Reconnect on error
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            try:
                reader, writer = await asyncio.open_connection(host, port)
            except Exception:
                break
    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass


async def run_benchmark(host, port, path, total_requests, concurrency):
    reqs_per_worker = total_requests // concurrency
    results = []
    status_counts = {}

    print("--- Starting Benchmark ---")
    print(f"Target: http://{host}:{port}{path}")
    print(
        f"Requests: {total_requests} across {concurrency} "
        f"concurrent connections ({reqs_per_worker} reqs/conn)"
    )

    start_time = time.perf_counter()
    tasks = [
        worker(host, port, path, reqs_per_worker, results, status_counts)
        for _ in range(concurrency)
    ]
    await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_time

    if not results:
        print("No successful requests recorded.")
        return

    rps = len(results) / total_time
    sorted_res = sorted(results)
    p50 = sorted_res[int(len(sorted_res) * 0.50)]
    p95 = sorted_res[int(len(sorted_res) * 0.95)]
    p99 = sorted_res[int(len(sorted_res) * 0.99)]
    avg = statistics.mean(sorted_res)

    print("\n--- Benchmark Results ---")
    print(f"Total Completed Requests : {len(sorted_res)}")
    print(f"Total Duration           : {total_time:.2f} seconds")
    print(f"Throughput (RPS)         : {rps:.2f} req/sec")
    print(f"Latency Mean             : {avg:.2f} ms")
    print(f"Latency Median (p50)     : {p50:.2f} ms")
    print(f"Latency p95              : {p95:.2f} ms")
    print(f"Latency p99              : {p99:.2f} ms")
    print(f"HTTP Status Counts       : {status_counts}")
    print("--------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="django-lightning benchmark script")
    parser.add_argument("--host", default="127.0.0.1", help="Target host")
    parser.add_argument("--port", type=int, default=8000, help="Target port")
    parser.add_argument("--path", default="/health", help="Target path")
    parser.add_argument("-n", "--requests", type=int, default=10000, help="Total requests")
    parser.add_argument("-c", "--concurrency", type=int, default=50, help="Concurrency level")
    args = parser.parse_args()

    asyncio.run(run_benchmark(args.host, args.port, args.path, args.requests, args.concurrency))
