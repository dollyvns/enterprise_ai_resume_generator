from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.resumes import router as resumes_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.telemetry import configure_telemetry


settings = get_settings()

configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Secure multi-agent resume generation API using LangGraph orchestration, "
        "structured LLM outputs, JWT authentication, logging, metrics, and review gates."
    ),
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env != "prod" else None,
    redoc_url="/redoc" if settings.app_env != "prod" else None,
)


@app.get("/")
def root():
    return {
        "message": "Enterprise AI Resume Generator is running",
        "docs": "/docs",
    }


app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(resumes_router)


if settings.metrics_enabled:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


configure_telemetry(app, settings)