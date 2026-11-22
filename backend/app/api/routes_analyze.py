# Accepts uploaded images (files) and/or text plus language (bn or en), processes everything in memory without saving files to disk, and returns a clean scaffolded response until the extraction and rules pipeline is wired in

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.config import settings
from app.api.schemas import AnalyzeResponse

router = APIRouter(tags=["analyze"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_offer(
    files: Optional[list[UploadFile]] = File(default=None),
    text: Optional[str] = Form(default=None),
    language: str = Form(default="bn"),
) -> AnalyzeResponse:
    cleaned_text = (text or "").strip()
    uploaded_files = files or []

    if not cleaned_text and not uploaded_files:
        raise HTTPException(
            status_code=400,
            detail="Please provide an offer image or paste job offer text.",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    read_file_names: list[str] = []

    for upload in uploaded_files:
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {upload.content_type}",
            )
        # Read in memory and discard without writing to disk
        payload = await upload.read()
        if len(payload) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File {upload.filename} exceeds {settings.max_upload_size_mb} MB limit.",
            )
        read_file_names.append(upload.filename or "uploaded_image")

    summary_parts: list[str] = []
    if read_file_names:
        summary_parts.append(f"{len(read_file_names)} image(s) received in memory")
    if cleaned_text:
        summary_parts.append(f"{len(cleaned_text)} chars of text received")

    return AnalyzeResponse(
        verdict="caution",
        score=50,
        language=language,
        input_summary="; ".join(summary_parts),
        unverifiable=["full_extraction_and_rules_pending"],
        audio_script_bn="তথ্য গ্রহণ করা হয়েছে। যাচাই প্রক্রিয়া প্রাথমিক পর্যায়ে রয়েছে; দাপ্তরিক সূত্রের সাথে যাচাই করুন।",
    )