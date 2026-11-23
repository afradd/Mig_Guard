import base64
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from google import genai

from app.api.schemas import OfferExtraction
from app.config import settings


class LLMExtractionError(Exception):
    """Raised when the LLM cannot produce a valid extraction."""


PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "extract_system.txt"
)


@lru_cache(maxsize=4)
def get_client(api_key: str) -> genai.Client:
    """
    Reuse Gemini clients rather than creating a new one
    for every uploaded document.
    """
    return genai.Client(api_key=api_key)


def load_extraction_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise LLMExtractionError(
            "Extraction prompt file was not found."
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def call_gemini(
    api_key: str,
    model: str,
    contents: list[dict],
) -> OfferExtraction:

    client = get_client(api_key)

    interaction = client.interactions.create(
        model=model,
        input=contents,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": OfferExtraction.model_json_schema(),
        },
        stream=False,
    )

    output_text = interaction.output_text

    if not output_text:
        raise ValueError("Gemini returned an empty response.")

    # Validate the returned JSON against our Pydantic model.
    return OfferExtraction.model_validate_json(output_text)


def extract_structured_fields(
    images: Sequence[tuple[bytes, str]],
    text: str = "",
) -> OfferExtraction:

    if not settings.primary_llm_api_key:
        raise LLMExtractionError(
            "PRIMARY_LLM_API_KEY is not configured."
        )

    prompt = load_extraction_prompt()

    contents = [
        {
            "type": "text",
            "text": prompt,
        }
    ]

    if text.strip():
        contents.append({
            "type": "text",
            "text": (
                "Additional text supplied by the user:\n"
                f"{text.strip()}"
            ),
        })

    # Attach all uploaded images to the same request.
    for index, (image_bytes, mime_type) in enumerate(
        images,
        start=1,
    ):
        contents.append({
            "type": "text",
            "text": f"Uploaded document image {index}:",
        })

        contents.append({
            "type": "image",
            "data": base64.b64encode(image_bytes).decode("ascii"),
            "mime_type": mime_type,
        })

    # First attempt: primary model.
    try:
        return call_gemini(
            api_key=settings.primary_llm_api_key,
            model=settings.primary_llm_model,
            contents=contents,
        )

    except Exception as primary_error:

        # Second attempt: fallback model.
        fallback_key = (
            settings.fallback_llm_api_key
            or settings.primary_llm_api_key
        )

        fallback_model = settings.fallback_llm_model

        should_try_fallback = (
            bool(fallback_key)
            and bool(fallback_model)
            and (
                fallback_model != settings.primary_llm_model
                or fallback_key != settings.primary_llm_api_key
            )
        )

        if should_try_fallback:
            try:
                return call_gemini(
                    api_key=fallback_key,
                    model=fallback_model,
                    contents=contents,
                )

            except Exception as fallback_error:
                raise LLMExtractionError(
                    "Both primary and fallback extraction failed."
                ) from fallback_error

        raise LLMExtractionError(
            "Primary extraction failed."
        ) from primary_error