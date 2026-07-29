"""Multi-Service Development Launcher for django-lightning.

Launches and supervises the django-bolt API server and SAQ background worker concurrently
in local development with graceful shutdown handling.

Usage:
    python scripts/dev_launcher.py
    uv run python scripts/dev_launcher.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    print("🚀 Starting django-lightning multi-service development environment...")
    base_dir = Path(__file__).resolve().parent.parent

    # Commands to run
    api_cmd = [sys.executable, "-m", "django", "runbolt", "--dev"]
    worker_cmd = [sys.executable, "-m", "saq", "app.tasks.settings"]

    processes = []

    try:
        # 1. Start API Server
        print("  ⚡ Launching Bolt API Dev Server (runbolt --dev)...")
        p_api = subprocess.Popen(
            api_cmd,
            cwd=base_dir,
            env=os.environ.copy(),
        )
        processes.append(("API", p_api))

        # 2. Start SAQ Worker
        print("  📦 Launching SAQ Async Background Worker (saq app.tasks.settings)...")
        p_worker = subprocess.Popen(
            worker_cmd,
            cwd=base_dir,
            env=os.environ.copy(),
        )
        processes.append(("WORKER", p_worker))

        print("\n✨ All services running! Press Ctrl+C to terminate all processes.\n")

        # Monitor process health
        while True:
            for name, proc in processes:
                poll = proc.poll()
                if poll is not None:
                    print(f"⚠️ Service '{name}' exited unexpectedly with status {poll}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down development services...")
        for name, proc in processes:
            print(f"  Terminating {name} process (PID {proc.pid})...")
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("✓ All dev services stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
