# LLM client for Mig_Guard — wraps the Google Gemini SDK.
# Sends images + text to Gemini and returns structured OfferExtraction JSON.
# Falls back to a secondary model automatically if the primary call fails.

import base64
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from google import genai
from google.genai import types

from app.api.schemas import OfferExtraction
from app.config import settings


class LLMExtractionError(Exception):
    """Raised when no model can produce a valid extraction."""


# Prompt lives beside this file so it can be edited without touching code.
PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "extract_system.txt"
)


@lru_cache(maxsize=4)
def _get_client(api_key: str) -> genai.Client:
    """Cache Gemini clients — one per API key — to avoid recreating them on every request."""
    return genai.Client(api_key=api_key)


def _load_prompt() -> str:
    """Read the extraction system prompt from disk; fail fast if the file is missing."""
    if not PROMPT_PATH.exists():
        raise LLMExtractionError(
            f"Extraction prompt not found at {PROMPT_PATH}"
        )
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_contents(
    images: Sequence[tuple[bytes, str]],
    text: str,
    prompt: str,
) -> list:
    """Assemble the content list that Gemini's generate_content expects.

    The list starts with the system prompt as a text Part, then any
    pasted text, then the uploaded images (each preceded by a label).
    Using types.Part keeps the format compatible with the SDK's type checker.
    """
    parts: list[types.Part] = []

    # System instruction as the first user-turn text Part.
    parts.append(types.Part.from_text(text=prompt))

    # Optional pasted text from the user.
    if text.strip():
        parts.append(
            types.Part.from_text(
                text=f"Additional text supplied by the user:\n{text.strip()}"
            )
        )

    # Attach each uploaded image together with a human-readable label.
    for index, (image_bytes, mime_type) in enumerate(images, start=1):
        parts.append(
            types.Part.from_text(text=f"Uploaded document image {index}:")
        )
        # from_bytes is the correct SDK method for inline binary image data.
        parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        )

    return parts


def _call_gemini(
    api_key: str,
    model: str,
    images: Sequence[tuple[bytes, str]],
    text: str,
    prompt: str,
) -> OfferExtraction:
    """Call one Gemini model and parse the structured JSON response.

    Uses GenerateContentConfig with response_schema so the model is
    constrained to return JSON that matches OfferExtraction exactly.
    """
    client = _get_client(api_key)
    contents = _build_contents(images, text, prompt)

    # response_schema constrains Gemini to return JSON matching OfferExtraction.
    # response_mime_type tells the API we expect application/json text.
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=OfferExtraction,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    # response.text is the raw JSON string from the model.
    output_text = response.text
    if not output_text:
        raise ValueError(f"Model '{model}' returned an empty response.")

    # Validate the JSON against our Pydantic schema before returning.
    return OfferExtraction.model_validate_json(output_text)


def extract_structured_fields(
    images: Sequence[tuple[bytes, str]],
    text: str = "",
) -> OfferExtraction:
    """Entry point: try the primary model, fall back to the secondary model on any error.

    Raises LLMExtractionError if both models fail or no key is configured.
    """
    if not settings.primary_llm_api_key:
        raise LLMExtractionError(
            "PRIMARY_LLM_API_KEY is not set. Add it to backend/.env."
        )

    prompt = _load_prompt()

    # --- Primary model attempt ---
    try:
        return _call_gemini(
            api_key=settings.primary_llm_api_key,
            model=settings.primary_llm_model,
            images=images,
            text=text,
            prompt=prompt,
        )
    except Exception as primary_error:
        pass  # Try fallback below; primary_error captured for chaining.

    # --- Fallback model attempt ---
    # Use fallback key if set, otherwise reuse the primary key with a different model.
    fallback_key = (
        settings.fallback_llm_api_key
        or settings.primary_llm_api_key
    )
    fallback_model = settings.fallback_llm_model

    # Only attempt fallback if it is meaningfully different from the primary.
    should_try_fallback = bool(fallback_key) and bool(fallback_model) and (
        fallback_model != settings.primary_llm_model
        or fallback_key != settings.primary_llm_api_key
    )

    if should_try_fallback:
        try:
            return _call_gemini(
                api_key=fallback_key,
                model=fallback_model,
                images=images,
                text=text,
                prompt=prompt,
            )
        except Exception as fallback_error:
            raise LLMExtractionError(
                "Both primary and fallback extraction failed."
            ) from fallback_error

    # Re-raise the original primary error wrapped in LLMExtractionError.
    raise LLMExtractionError(
        f"Primary extraction failed and no fallback is configured: {primary_error}"
    ) from primary_error
