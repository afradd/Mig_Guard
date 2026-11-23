# POST /api/analyze — images or pasted text in, verified verdict out.

from typing import Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from starlette.concurrency import run_in_threadpool

from app.api.schemas import AnalyzeResponse
from app.config import settings
from app.pipeline.orchestrator import analyze_document
from app.utils.errors import AnalyzePipelineError

router = APIRouter(tags=["analyze"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGES_PER_REQUEST = 4


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_offer(
    files: Optional[list[UploadFile]] = File(default=None),
    text: Optional[str] = Form(default=None),
    language: str = Form(default="bn"),
) -> AnalyzeResponse:
    cleaned_text = (text or "").strip()
    uploaded_files = files or []

    if language not in {"bn", "en"}:
        raise HTTPException(
            status_code=400,
            detail="Language must be 'bn' or 'en'.",
        )

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
    images: list[tuple[bytes, str]] = []

    for upload in uploaded_files:
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type: {upload.content_type}",
            )
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

    try:
        return await run_in_threadpool(
            analyze_document,
            images,
            cleaned_text,
            language,
        )
    except AnalyzePipelineError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail=exc.as_detail(),
        ) from exc
