from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

import anthropic as anthropic_sdk

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from services.api.search_service import SearchService
from services.rest_client import RestClient
from utils.api_client import create_cart
from utils.data_loader import get_config, get_test_data, has_secret_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
ALLURE_REPORT_DIR = PROJECT_ROOT / "allure-report"
ALLURE_SUMMARY_PATH = ALLURE_REPORT_DIR / "summary.json"
JOB_TTL_SECONDS = 3600
MAX_FINISHED_JOBS = 100


class PytestRunRequest(BaseModel):
    args: list[str] = Field(default_factory=list)


class AllureGenerateRequest(BaseModel):
    results_dir: str = "allure-results"


class MockCartAddRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    system: str | None = None


class Job(BaseModel):
    id: str
    command: list[str]
    status: str
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    finished_at: float | None = None


class Product(BaseModel):
    product_id: str
    name: str
    price: float


class MockStore:
    def __init__(self) -> None:
        self.products = [
            Product(product_id="43", name="MacBook", price=602.0),
            Product(product_id="40", name="iPhone", price=123.2),
            Product(product_id="42", name="Apple Cinema 30", price=110.0),
            Product(product_id="30", name="Canon EOS 5D", price=98.0),
        ]
        self.cart: dict[str, int] = {}

    def search(self, query: str, max_price: float | None = None) -> list[Product]:
        normalized = query.casefold()
        products = [
            product
            for product in self.products
            if normalized in product.name.casefold()
        ]
        if max_price is not None:
            products = [product for product in products if product.price <= max_price]
        return products

    def add_to_cart(self, product_id: str, quantity: int) -> Product:
        product = next(
            (item for item in self.products if item.product_id == product_id),
            None,
        )
        if product is None:
            raise KeyError(product_id)
        self.cart[product_id] = self.cart.get(product_id, 0) + quantity
        return product

    def cart_items(self) -> dict[str, Any]:
        items = []
        total = 0.0
        for product_id, quantity in self.cart.items():
            product = next(
                item for item in self.products if item.product_id == product_id
            )
            line_total = product.price * quantity
            total += line_total
            items.append(
                {
                    "product": product.model_dump(),
                    "quantity": quantity,
                    "line_total": round(line_total, 2),
                }
            )
        return {"items": items, "total": round(total, 2)}

    def clear_cart(self) -> None:
        self.cart.clear()


jobs: dict[str, Job] = {}
mock_store = MockStore()


def _safe_project_path(path_value: str) -> Path:
    path = (PROJECT_ROOT / path_value).resolve()
    if PROJECT_ROOT not in path.parents and path != PROJECT_ROOT:
        raise HTTPException(status_code=400, detail="Path must stay inside project root")
    return path


def _run_job(job: Job) -> None:
    process = subprocess.run(
        job.command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    job.returncode = process.returncode
    job.stdout = process.stdout[-12000:]
    job.stderr = process.stderr[-12000:]
    job.status = "passed" if process.returncode == 0 else "failed"
    job.finished_at = time.time()


def _prune_jobs(now: float | None = None) -> None:
    if now is None:
        now = time.time()
    stale_job_ids = [
        job_id
        for job_id, job in jobs.items()
        if job.finished_at is not None and (now - job.finished_at) > JOB_TTL_SECONDS
    ]
    for job_id in stale_job_ids:
        jobs.pop(job_id, None)

    finished_jobs = [
        (job_id, job.finished_at)
        for job_id, job in jobs.items()
        if job.finished_at is not None
    ]
    if len(finished_jobs) <= MAX_FINISHED_JOBS:
        return

    finished_jobs.sort(key=lambda item: item[1])
    overflow = len(finished_jobs) - MAX_FINISHED_JOBS
    for job_id, _ in finished_jobs[:overflow]:
        jobs.pop(job_id, None)


def _start_job(command: list[str]) -> Job:
    _prune_jobs()
    job_id = uuid.uuid4().hex
    job = Job(id=job_id, command=command, status="running")
    jobs[job_id] = job
    thread = threading.Thread(target=_run_job, args=(job,), daemon=True)
    thread.start()
    return job


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ness Automation API",
        version="1.0.0",
        description="Local API for test data, pytest runs, Allure reports, and mocks.",
    )
    app.mount(
        "/reports/allure/view",
        StaticFiles(directory=ALLURE_REPORT_DIR, html=True, check_dir=False),
        name="allure-report",
    )

    @app.get("/architecture", response_class=HTMLResponse)
    def architecture_doc() -> str:
        html_path = PROJECT_ROOT / "architecture.html"
        if not html_path.exists():
            raise HTTPException(status_code=404, detail="Architecture documentation not found")
        return html_path.read_text(encoding="utf-8")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/automation/config")
    def read_config() -> dict[str, Any]:
        return get_config()

    @app.get("/automation/test-data")
    def read_all_test_data() -> Any:
        return get_test_data()

    @app.get("/automation/test-data/{key}")
    def read_test_data(key: str) -> Any:
        all_data = get_test_data()
        if not isinstance(all_data, dict) or key not in all_data:
            raise HTTPException(status_code=404, detail=f"Unknown test data key: {key}")
        return get_test_data(key)

    @app.get("/automation/secrets/status")
    def secrets_status() -> dict[str, bool]:
        return {"configured": has_secret_file()}

    @app.get("/automation/external/search")
    def external_search(query: str = Query(min_length=1)) -> dict[str, Any]:
        base_url = get_config()["base_url"]
        client = RestClient()
        try:
            service = SearchService(client, base_url)
            response = service.search(query)
            response.raise_for_status()
            return {
                "query": query,
                "status_code": response.status_code,
                "product_names": service.product_names(response.text),
                "product_ids": service.product_ids(response.text),
                "prices": service.prices(response.text),
                "card_count": len(service.product_cards(response.text)),
            }
        finally:
            client.close()

    @app.post("/automation/external/cart")
    def external_cart_from_test_data() -> dict[str, Any]:
        config = get_config()
        data = get_test_data()
        search = data["search"]
        ocsessid, products = create_cart(
            base_url=config["base_url"],
            query=search["query"],
            max_price=search["max_price"],
            limit=search["limit"],
        )
        return {
            "ocsessid": ocsessid,
            "products": [asdict(product) for product in products],
        }

    @app.post("/runs/pytest", response_model=Job)
    def run_pytest(request: PytestRunRequest) -> Job:
        blocked = {";", "&&", "||", "|", ">", "<", "$(", "`"}
        for arg in request.args:
            if any(token in arg for token in blocked):
                raise HTTPException(status_code=400, detail=f"Unsafe pytest arg: {arg}")
        return _start_job([sys.executable, "-m", "pytest", *request.args])

    @app.get("/runs/{job_id}", response_model=Job)
    def read_job(job_id: str) -> Job:
        _prune_jobs()
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Unknown job: {job_id}")
        return job

    @app.get("/reports/allure/status")
    def allure_status() -> dict[str, Any]:
        return {
            "results_exists": ALLURE_RESULTS_DIR.exists(),
            "report_exists": (ALLURE_REPORT_DIR / "index.html").exists(),
            "summary_exists": ALLURE_SUMMARY_PATH.exists(),
            "report_url": "/reports/allure/view/index.html",
        }

    @app.get("/reports/allure/summary")
    def allure_summary() -> dict[str, Any]:
        if not ALLURE_SUMMARY_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail="Allure summary not found. Run npm run allure:generate first.",
            )
        return json.loads(ALLURE_SUMMARY_PATH.read_text(encoding="utf-8"))

    @app.post("/reports/allure/generate", response_model=Job)
    def generate_allure(request: AllureGenerateRequest) -> Job:
        results_dir = _safe_project_path(request.results_dir)
        if not results_dir.exists():
            raise HTTPException(status_code=404, detail="Allure results directory missing")
        relative_results_dir = str(results_dir.relative_to(PROJECT_ROOT))
        return _start_job(["npx", "allure", "generate", relative_results_dir])

    @app.get("/mock/products", response_model=list[Product])
    def mock_products() -> list[Product]:
        return mock_store.products

    @app.get("/mock/products/search", response_model=list[Product])
    def mock_product_search(
        query: str = Query(min_length=1),
        max_price: float | None = Query(default=None, ge=0),
    ) -> list[Product]:
        return mock_store.search(query, max_price)

    @app.post("/mock/cart/add")
    def mock_cart_add(request: MockCartAddRequest) -> dict[str, Any]:
        try:
            product = mock_store.add_to_cart(request.product_id, request.quantity)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Product not found") from exc
        return {"added": product.model_dump(), "cart": mock_store.cart_items()}

    @app.get("/mock/cart")
    def mock_cart() -> dict[str, Any]:
        return mock_store.cart_items()

    @app.delete("/mock/cart")
    def mock_cart_clear() -> dict[str, str]:
        mock_store.clear_cart()
        return {"status": "cleared"}

    @app.post("/chat")
    def chat(request: ChatRequest) -> dict[str, Any]:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="ANTHROPIC_API_KEY is not configured on this server",
            )
        client = anthropic_sdk.Anthropic(api_key=api_key)
        try:
            result = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                system=request.system or "You are a helpful assistant.",
                messages=[{"role": "user", "content": request.message}],
            )
        except anthropic_sdk.APIError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "response": result.content[0].text,
            "model": result.model,
            "input_tokens": result.usage.input_tokens,
            "output_tokens": result.usage.output_tokens,
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server.app:app", host="127.0.0.1", port=port, reload=True)
