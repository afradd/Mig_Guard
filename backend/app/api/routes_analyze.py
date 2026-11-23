# POST /api/analyze — receives images or pasted text, returns extracted offer fields.
# Validates inputs, calls the extraction pipeline, and wraps results in AnalyzeResponse.
# Phase 1: extraction only; risk scoring and flags are added in Phase 2.

from typing import Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.api.schemas import AnalyzeResponse
from app.llm.client import LLMExtractionError  # fixed import path
from app.pipeline.extract import extract_offer_fields


router = APIRouter(tags=["analyze"])

# Only safe browser-uploadable image formats are accepted.
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

# Cap at 4 images per request to control token and latency costs.
MAX_IMAGES_PER_REQUEST = 4


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_offer(
    files: Optional[list[UploadFile]] = File(default=None),
    text: Optional[str] = Form(default=None),
    language: str = Form(default="bn"),
) -> AnalyzeResponse:
    """Accept one or more document images (or pasted text) and return extracted fields."""

    cleaned_text = (text or "").strip()
    uploaded_files = files or []

    # Validate language early so the error message is clear.
    if language not in {"bn", "en"}:
        raise HTTPException(
            status_code=400,
            detail="Language must be 'bn' or 'en'.",
        )

    # Require at least one input.
    if not cleaned_text and not uploaded_files:
        raise HTTPException(
            status_code=400,
            detail="Please upload an image or paste offer text.",
        )

    if len(uploaded_files) > MAX_IMAGES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_IMAGES_PER_REQUEST} images are allowed per request.",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    # Read and validate each uploaded image into memory.
    images: list[tuple[bytes, str]] = []

    for upload in uploaded_files:

        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type: {upload.content_type}",
            )

        # Read one byte over the limit so we can detect oversized files.
        payload = await upload.read(max_bytes + 1)

        if len(payload) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Image exceeds {settings.max_upload_size_mb} MB.",
            )

        if not payload:
            raise HTTPException(
                status_code=400,
                detail="An uploaded image is empty.",
            )

        images.append((payload, upload.content_type))

    # Run the synchronous Gemini SDK call in a thread so it doesn't block the event loop.
    try:
        extraction = await run_in_threadpool(
            extract_offer_fields,
            images,
            cleaned_text,
        )

    except LLMExtractionError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Document extraction is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    # Build a human-readable summary of what was submitted.
    summary_parts = []
    if images:
        summary_parts.append(f"{len(images)} image(s) analyzed")
    if cleaned_text:
        summary_parts.append(f"{len(cleaned_text)} characters of text analyzed")

    return AnalyzeResponse(
        # Phase 1 placeholder values — real scoring added in Phase 2.
        verdict="caution",
        score=50,
        language=language,
        input_summary=(
            "; ".join(summary_parts)
            + "; extraction completed, risk checks pending"
        ),
        extracted=extraction.model_dump(),
        flags=[],
        unverifiable=["risk_assessment_pending_phase_2"],
    )
