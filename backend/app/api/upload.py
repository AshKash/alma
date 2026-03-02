from fastapi import APIRouter, UploadFile

router = APIRouter()


@router.post("/upload")
async def upload_documents(
    passport: UploadFile,
    g28: UploadFile,
):
    """Accept passport and G-28 uploads. Returns extracted data. TODO: implement."""
    return {
        "status": "ok",
        "passport_filename": passport.filename,
        "g28_filename": g28.filename,
        "extracted": {},
    }
