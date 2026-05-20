"""Session helpers to ensure the local FastAPI server is running for AI tests."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_server_process: subprocess.Popen[str] | None = None
_started_by_tests = False


def ensure_server_running(server_url: str, timeout: float = 30.0) -> str:
    """Return a base URL with a working /chat endpoint, starting uvicorn if needed."""
    global _server_process, _started_by_tests

    if _health_ok(server_url) and _chat_ready(server_url):
        return server_url.rstrip("/")

    parsed = urlparse(server_url)
    host = parsed.hostname or "127.0.0.1"
    port = _free_port() if _health_ok(server_url) else (parsed.port or 8000)
    base_url = f"http://{host}:{port}"

    _started_by_tests = True
    _server_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "server.app:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=_PROJECT_ROOT,
        env=os.environ.copy(),
    )

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _health_ok(base_url) and _chat_ready(base_url):
            return base_url
        if _server_process.poll() is not None:
            raise RuntimeError(
                f"Test server exited early with code {_server_process.returncode}"
            )
        time.sleep(0.5)

    raise RuntimeError(f"Timed out waiting for test server at {base_url}")


def shutdown_server() -> None:
    global _server_process, _started_by_tests
    if not _started_by_tests or _server_process is None:
        return
    _server_process.terminate()
    try:
        _server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _server_process.kill()
    _server_process = None
    _started_by_tests = False


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _health_ok(server_url: str) -> bool:
    try:
        response = requests.get(f"{server_url.rstrip('/')}/health", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _chat_ready(server_url: str) -> bool:
    try:
        response = requests.post(
            f"{server_url.rstrip('/')}/chat",
            json={"message": "ping"},
            timeout=5,
        )
        return response.status_code == 200 and "response" in response.json()
    except requests.exceptions.RequestException:
        return False
