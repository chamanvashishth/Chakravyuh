"""Main FastAPI Application Entrypoint for Chakravyuh."""

import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from chakravyuh.api.routes import HoneypotOrchestrator, create_router
from chakravyuh.config import CONFIG


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Injects a unique X-Request-ID header into every HTTP response for traceability."""

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


def create_app(
    db_path: Optional[str] = None,
    api_key: Optional[str] = None,
    allowed_origins: Optional[List[str]] = None,
) -> FastAPI:
    """Create and configure the Chakravyuh FastAPI ASGI application."""
    app = FastAPI(
        title=CONFIG.app_name,
        version=CONFIG.version,
        description=(
            "Offensive Cyber Defense System using Gnani's vachana-vc-v1 ([1, 768] torch.bfloat16) "
            "speaker-embedding pipeline, Prisma v2.5 8kHz telephonic ASR, and Evon v3.3 Hinglish "
            "deception engine to intercept scam calls and compile live I4C FIR dossiers."
        ),
    )

    cors_origins = (
        ["*"]
        if CONFIG.allow_all_origins
        else (allowed_origins or list(CONFIG.allowed_origins))
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    orchestrator = HoneypotOrchestrator(db_path=db_path)
    app.state.orchestrator = orchestrator
    app.include_router(create_router(orchestrator, api_key=api_key))

    @app.get("/", response_class=HTMLResponse)
    def serve_command_center_ui() -> HTMLResponse:
        static_html = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.exists(static_html):
            with open(static_html, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        return HTMLResponse(
            content="<h1>Chakravyuh Active Voice-Clone Honeypot API Operational</h1>",
            status_code=200,
        )

    return app


app = create_app()
