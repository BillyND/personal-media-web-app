from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db.schema import init_db
from app.paths import STATIC_DIR
from app.routes import auth, files, jobs, pages


def create_app() -> FastAPI:
    settings = get_settings()
    settings.ensure_ready()
    init_db()

    app = FastAPI(title="Personal Media Web App")
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(auth.router)
    app.include_router(pages.router)
    app.include_router(jobs.router)
    app.include_router(files.router)

    @app.get("/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
