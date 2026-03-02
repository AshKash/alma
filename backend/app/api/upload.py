import base64
import logging

from fastapi import APIRouter, UploadFile

from app.services.extract import extract_document
from app.services.form_filler import fill_form

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_documents(
    passport: UploadFile,
    g28: UploadFile,
):
    """Accept passport and G-28 uploads, extract data, fill form, return results."""
    passport_bytes = await passport.read()
    g28_bytes = await g28.read()

    logger.info(
        "Extracting passport=%s (%d bytes), g28=%s (%d bytes)",
        passport.filename,
        len(passport_bytes),
        g28.filename,
        len(g28_bytes),
    )

    passport_data = await extract_document(
        passport_bytes, passport.filename, "passport"
    )
    g28_data = await extract_document(g28_bytes, g28.filename, "g28")

    logger.info("Filling form with extracted data")
    screenshot = await fill_form(passport_data, g28_data)

    return {
        "passport_data": passport_data.model_dump(),
        "g28_data": g28_data.model_dump(),
        "screenshot": base64.b64encode(screenshot).decode("ascii"),
    }
