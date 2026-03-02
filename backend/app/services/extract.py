import base64
import json
import mimetypes

import anthropic
from pydantic import BaseModel

from app.core.config import ANTHROPIC_API_KEY

MODEL = "claude-sonnet-4-20250514"


class PassportData(BaseModel):
    last_name: str = ""
    first_name: str = ""
    middle_name: str = ""
    passport_number: str = ""
    country_of_issue: str = ""
    nationality: str = ""
    date_of_birth: str = ""
    place_of_birth: str = ""
    sex: str = ""
    date_of_issue: str = ""
    date_of_expiration: str = ""


class G28Data(BaseModel):
    # Attorney info
    family_name: str = ""
    given_name: str = ""
    middle_name: str = ""
    # Address
    street_number_and_name: str = ""
    apt_ste_flr: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = ""
    # Contact
    daytime_phone: str = ""
    mobile_phone: str = ""
    email: str = ""
    # Eligibility
    licensing_authority: str = ""
    bar_number: str = ""
    # Firm
    law_firm_name: str = ""


PASSPORT_PROMPT = """\
Extract the following fields from this passport document. Return ONLY a JSON object with these keys:
- last_name
- first_name
- middle_name
- passport_number
- country_of_issue
- nationality
- date_of_birth (format: YYYY-MM-DD)
- place_of_birth
- sex
- date_of_issue (format: YYYY-MM-DD)
- date_of_expiration (format: YYYY-MM-DD)

All date fields must be in YYYY-MM-DD format. If a field cannot be determined, use an empty string.
Return ONLY valid JSON, no markdown fences or extra text."""

G28_PROMPT = """\
Extract the following fields from this G-28 (Notice of Entry of Appearance as Attorney or Accredited Representative) form. Return ONLY a JSON object with these keys:
- family_name (attorney/representative last name)
- given_name (attorney/representative first name)
- middle_name (attorney/representative middle name)
- street_number_and_name
- apt_ste_flr (apartment, suite, or floor number)
- city
- state
- zip_code
- country
- daytime_phone
- mobile_phone
- email
- licensing_authority (state bar or equivalent)
- bar_number
- law_firm_name

If a field cannot be determined, use an empty string.
Return ONLY valid JSON, no markdown fences or extra text."""


def _media_type(filename: str) -> str:
    mt, _ = mimetypes.guess_type(filename)
    if mt:
        return mt
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "pdf": "application/pdf",
    }.get(ext, "application/octet-stream")


def _is_pdf(filename: str) -> bool:
    return _media_type(filename) == "application/pdf"


def _build_content_block(file_bytes: bytes, filename: str) -> dict:
    """Build the appropriate Claude API content block for a file."""
    media = _media_type(filename)
    data = base64.standard_b64encode(file_bytes).decode("ascii")

    if _is_pdf(filename):
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": media,
                "data": data,
            },
        }
    else:
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media,
                "data": data,
            },
        }


async def extract_document(
    file_bytes: bytes, filename: str, doc_type: str
) -> PassportData | G28Data:
    """Extract structured data from a passport or G-28 document using Claude Vision."""
    if doc_type == "passport":
        prompt = PASSPORT_PROMPT
        model_cls = PassportData
    elif doc_type == "g28":
        prompt = G28_PROMPT
        model_cls = G28Data
    else:
        raise ValueError(f"Unknown doc_type: {doc_type}")

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    message = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    _build_content_block(file_bytes, filename),
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    data = json.loads(raw)
    return model_cls.model_validate(data)
