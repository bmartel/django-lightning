"""
High-Performance Multi-Process Benchmark Script for django-lightning / django-bolt.
Measures true maximum server throughput (RPS), p50, p95, and p99 latency.
"""

from __future__ import annotations

import argparse
import asyncio
import multiprocessing
import os
import statistics
import time


def raw_worker_process(
    host: str,
    port: int,
    path: str,
    num_requests: int,
    concurrency: int,
    result_queue: multiprocessing.Queue,
):
    """Worker process executing high-speed HTTP keep-alive socket transactions."""
    raw_req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"User-Agent: lightning-bench/1.0\r\n"
        f"Accept: */*\r\n"
        f"Connection: keep-alive\r\n\r\n"
    ).encode()

    async def run_async_worker():
        reqs_per_conn = num_requests // concurrency
        latencies: list[float] = []
        status_200 = 0

        async def conn_task():
            nonlocal status_200
            try:
                reader, writer = await asyncio.open_connection(host, port)
            except Exception:
                return

            for _ in range(reqs_per_conn):
                t0 = time.perf_counter()
                try:
                    writer.write(raw_req)
                    await writer.drain()

                    # Fast header read
                    head_data = await reader.readuntil(b"\r\n\r\n")
                    if b"200 OK" in head_data:
                        status_200 += 1

                    # Content-Length extraction
                    cl_idx = head_data.lower().find(b"content-length:")
                    if cl_idx != -1:
                        end_line = head_data.find(b"\r\n", cl_idx)
                        cl_str = head_data[cl_idx + 15 : end_line].strip()
                        cl = int(cl_str)
                        if cl > 0:
                            await reader.readexactly(cl)
                    t1 = time.perf_counter()
                    latencies.append((t1 - t0) * 1000.0)
                except Exception:
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

        tasks = [conn_task() for _ in range(concurrency)]
        await asyncio.gather(*tasks)
        result_queue.put((latencies, status_200))

    asyncio.run(run_async_worker())


def main():
    parser = argparse.ArgumentParser(description="django-lightning high-throughput benchmark")
    parser.add_argument("--host", default="127.0.0.1", help="Target host")
    parser.add_argument("--port", type=int, default=8000, help="Target port")
    parser.add_argument("--path", default="/health", help="Target path")
    parser.add_argument("-n", "--requests", type=int, default=50000, help="Total requests")
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=100,
        help="Total concurrency across client processes",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=min(os.cpu_count() or 4, 8),
        help="Client worker processes",
    )
    args = parser.parse_args()

    print("--- Starting High-Performance Multi-Process Load Test ---")
    print(f"Target      : http://{args.host}:{args.port}{args.path}")
    print(f"Requests    : {args.requests:,}")
    print(f"Concurrency : {args.concurrency} across {args.workers} client processes")

    reqs_per_proc = args.requests // args.workers
    conn_per_proc = max(1, args.concurrency // args.workers)

    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    processes: list[multiprocessing.Process] = []

    start_time = time.perf_counter()

    for _ in range(args.workers):
        p = multiprocessing.Process(
            target=raw_worker_process,
            args=(args.host, args.port, args.path, reqs_per_proc, conn_per_proc, result_queue),
        )
        p.start()
        processes.append(p)

    all_latencies: list[float] = []
    total_200 = 0

    for _ in range(args.workers):
        latencies, count_200 = result_queue.get()
        all_latencies.extend(latencies)
        total_200 += count_200

    for p in processes:
        p.join()

    total_time = time.perf_counter() - start_time
    if not all_latencies:
        print("No successful responses received.")
        return

    rps = len(all_latencies) / total_time
    sorted_res = sorted(all_latencies)
    p50 = sorted_res[int(len(sorted_res) * 0.50)]
    p95 = sorted_res[int(len(sorted_res) * 0.95)]
    p99 = sorted_res[int(len(sorted_res) * 0.99)]
    avg = statistics.mean(sorted_res)

    print("\n--- Benchmark Performance Results ---")
    print(f"Total Completed Requests : {len(sorted_res):,}")
    print(f"Total Duration           : {total_time:.2f} s")
    print(f"Throughput (RPS)         : {rps:,.2f} req/sec")
    print(f"Latency Mean             : {avg:.2f} ms")
    print(f"Latency Median (p50)     : {p50:.2f} ms")
    print(f"Latency p95              : {p95:.2f} ms")
    print(f"Latency p99              : {p99:.2f} ms")
    print(f"HTTP 200 OK Responses    : {total_200:,}")
    print("--------------------------------------\n")


if __name__ == "__main__":
    main()
