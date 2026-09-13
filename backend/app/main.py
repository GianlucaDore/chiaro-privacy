from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, Env, get_backend_root
from app.api.router import api_router
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import os


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # avvio 
    os.makedirs(get_backend_root() / "uploads", exist_ok=True)
    yield
    # spegnimento — per ora niente


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url=(f"{settings.API_PREFIX}/docs" if settings.ENV != Env.DEV else "/docs"),
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_PREFIX)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'" if settings.ENV == Env.DEV else "default-src 'none'; frame-ancestors 'none'"
        response.headers['Cross-Origin-Resource-Policy'] = 'same-site'
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp; report-to=default'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin; report-to=default'
        # response.headers['Content-Type'] = 'application/json'
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    

app.add_middleware(SecurityHeadersMiddleware)

if settings.ENV == Env.DEV:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.BACKEND_CORS_ORIGIN)],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )



logging.basicConfig(format='%(levelname)-9s %(asctime)s - %(name)s - %(message)s', level=logging.DEBUG if settings.ENV == Env.DEV else logging.INFO)
