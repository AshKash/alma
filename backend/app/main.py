from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.upload import router as upload_router
from app.api.health import router as health_router

app = FastAPI(title="Alma")

app.include_router(health_router)
app.include_router(upload_router, prefix="/api")

# Serve static frontend
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
