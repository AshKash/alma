from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.upload import router as upload_router
from app.api.health import router as health_router

app = FastAPI(title="Alma")

app.include_router(health_router)
app.include_router(upload_router, prefix="/api")

static_dir = Path(__file__).parent / "static"


@app.get("/")
async def index():
    return FileResponse(static_dir / "index.html")


# Serve other static files (CSS/JS if added later)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
