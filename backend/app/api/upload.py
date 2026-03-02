import asyncio
import base64
import json
import logging
import time
from collections.abc import AsyncGenerator, Callable, Coroutine

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from app.services.extract import extract_document
from app.services.form_filler import fill_form

logger = logging.getLogger(__name__)

router = APIRouter()

# Type for log callback: async fn(message: str) -> None
LogCallback = Callable[[str], Coroutine]


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _process_upload(
    passport_bytes: bytes,
    passport_filename: str,
    g28_bytes: bytes,
    g28_filename: str,
) -> AsyncGenerator[str, None]:
    """Process upload and yield SSE events with detailed logs."""
    t0 = time.time()

    def elapsed() -> str:
        return f"{time.time() - t0:.1f}s"

    # --- Passport extraction ---
    yield _sse_event("log", {
        "message": f"Received passport: {passport_filename} ({len(passport_bytes):,} bytes)"
    })
    yield _sse_event("log", {
        "message": f"Received G-28: {g28_filename} ({len(g28_bytes):,} bytes)"
    })

    yield _sse_event("log", {
        "message": f"[{elapsed()}] Sending passport to Claude Vision API (model: claude-sonnet-4-20250514)..."
    })

    passport_data = await extract_document(
        passport_bytes, passport_filename, "passport"
    )

    passport_dict = passport_data.model_dump()
    filled = {k: v for k, v in passport_dict.items() if v}
    yield _sse_event("log", {
        "message": f"[{elapsed()}] Passport extracted — {len(filled)} fields found"
    })
    for k, v in filled.items():
        label = k.replace("_", " ").title()
        yield _sse_event("log", {"message": f"  {label}: {v}"})

    # --- G-28 extraction ---
    yield _sse_event("log", {
        "message": f"[{elapsed()}] Sending G-28 to Claude Vision API..."
    })

    g28_data = await extract_document(g28_bytes, g28_filename, "g28")

    g28_dict = g28_data.model_dump()
    filled_g28 = {k: v for k, v in g28_dict.items() if v}
    yield _sse_event("log", {
        "message": f"[{elapsed()}] G-28 extracted — {len(filled_g28)} fields found"
    })
    for k, v in filled_g28.items():
        label = k.replace("_", " ").title()
        yield _sse_event("log", {"message": f"  {label}: {v}"})

    # --- Form filling ---
    yield _sse_event("log", {
        "message": f"[{elapsed()}] Launching browser and navigating to form..."
    })

    screenshot = await fill_form(passport_data, g28_data)

    yield _sse_event("log", {
        "message": f"[{elapsed()}] Form filled successfully — browser left open for review"
    })

    # --- Done ---
    yield _sse_event("log", {
        "message": f"[{elapsed()}] Done! Screenshot captured ({len(screenshot):,} bytes)"
    })

    yield _sse_event("done", {
        "screenshot": base64.b64encode(screenshot).decode("ascii"),
    })


@router.post("/upload")
async def upload_documents(
    passport: UploadFile,
    g28: UploadFile,
):
    """Accept passport and G-28 uploads, stream progress via SSE."""
    passport_bytes = await passport.read()
    g28_bytes = await g28.read()

    return StreamingResponse(
        _process_upload(
            passport_bytes, passport.filename,
            g28_bytes, g28.filename,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
