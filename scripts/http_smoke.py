from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib import request


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def get_json(url: str) -> dict:
    with request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_health(base_url: str) -> None:
    last_error: Exception | None = None
    for _ in range(30):
        try:
            if get_json(base_url + "/health")["status"] == "ok":
                return
        except Exception as exc:  # pragma: no cover - diagnostic path
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"backend did not become healthy: {last_error}")


def main() -> int:
    port = free_port()
    base_url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=BACKEND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_health(base_url)
        health = get_json(base_url + "/health")
        session = post_json(base_url + "/api/students/session", {"stage": "upper_primary"})
        course = get_json(base_url + "/api/courses?stage=upper_primary")
        assert health["status"] == "ok"
        assert session["session_id"]
        assert len(course["knowledge_points"]) >= 10
        print("http smoke passed")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
