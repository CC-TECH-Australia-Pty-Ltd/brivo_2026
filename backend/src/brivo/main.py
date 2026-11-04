"""FastAPI application entry point.

Run locally with:  uv run uvicorn brivo.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from brivo import __version__
from brivo.core import db
from brivo.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Brivo Clinical System API",
        version=__version__,
        # Interactive docs only outside production.
        docs_url=None if settings.environment == "production" else "/docs",
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness: the API process is running."""
        return {"status": "ok", "version": __version__}

    @app.get("/health/db", tags=["health"])
    def health_db() -> dict[str, str]:
        """Readiness: the API can reach the database."""
        try:
            db.ping()
        except SQLAlchemyError as exc:
            raise HTTPException(status_code=503, detail="database unavailable") from exc
        return {"status": "ok"}

    # Module routers are registered here as they are built, e.g.:
    # app.include_router(participants.router, prefix="/participants")
    return app


app = create_app()
