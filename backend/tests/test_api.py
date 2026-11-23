# Integration tests for POST /api/analyze and GET /api/health.
# Uses FastAPI's TestClient so no real server or LLM calls are made.
# Run with: pytest tests/ (from the backend/ directory)

import io
import json
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.api.schemas import ExtractedField, OfferExtraction


client = TestClient(app)


def _empty_extraction() -> OfferExtraction:
    """Return an OfferExtraction where every field is empty (LLM found nothing)."""
    return OfferExtraction()


def _extraction_with_destination(value="Malaysia") -> OfferExtraction:
    """Return an OfferExtraction with a filled destination field."""
    return OfferExtraction(
        destination=ExtractedField(
            value=value,
            confidence=0.9,
            source_snippet=f"Destination: {value}",
        )
    )


# ---------------------------------------------------------------------------
# Health route
# ---------------------------------------------------------------------------

def test_health_returns_ok():
    """GET /api/health must return 200 with status=ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "env" in body


# ---------------------------------------------------------------------------
# /api/analyze — input validation
# ---------------------------------------------------------------------------

def test_analyze_no_input_returns_400():
    """Posting with neither images nor text must be rejected with 400."""
    response = client.post("/api/analyze")
    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower() or "text" in response.json()["detail"].lower()


def test_analyze_invalid_language_returns_400():
    """Posting an unsupported language must be rejected with 400."""
    response = client.post(
        "/api/analyze",
        data={"text": "Some offer text", "language": "fr"},
    )
    assert response.status_code == 400
    assert "language" in response.json()["detail"].lower()


def test_analyze_unsupported_image_type_returns_400():
    """Uploading a non-image file type must be rejected with 400."""
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    response = client.post(
        "/api/analyze",
        files={"files": ("offer.pdf", fake_pdf, "application/pdf")},
    )
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_analyze_empty_image_returns_400():
    """An empty image upload must be rejected with 400."""
    empty = io.BytesIO(b"")
    response = client.post(
        "/api/analyze",
        files={"files": ("empty.jpg", empty, "image/jpeg")},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# /api/analyze — successful extraction (LLM mocked)
# ---------------------------------------------------------------------------

@patch("app.api.routes_analyze.extract_offer_fields")
def test_analyze_text_returns_extraction(mock_extract):
    """Pasting text must trigger extraction and return the structured response."""
    mock_extract.return_value = _extraction_with_destination("Qatar")

    response = client.post(
        "/api/analyze",
        data={"text": "Job offer for Qatar", "language": "en"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "caution"           # Phase 1 placeholder
    assert body["score"] == 50                    # Phase 1 placeholder
    assert body["language"] == "en"
    assert "extraction completed" in body["input_summary"]
    assert body["extracted"]["destination"]["value"] == "Qatar"


@patch("app.api.routes_analyze.extract_offer_fields")
def test_analyze_image_returns_extraction(mock_extract):
    """Uploading an image must trigger extraction and return the structured response."""
    mock_extract.return_value = _empty_extraction()

    # Minimal valid JPEG bytes (1x1 white pixel).
    tiny_jpeg = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
        0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
        0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
        0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
        0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
        0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD2,
        0x8A, 0x28, 0x03, 0xFF, 0xD9,
    ])

    response = client.post(
        "/api/analyze",
        files={"files": ("offer.jpg", io.BytesIO(tiny_jpeg), "image/jpeg")},
        data={"language": "bn"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "1 image(s) analyzed" in body["input_summary"]


@patch("app.api.routes_analyze.extract_offer_fields")
def test_analyze_llm_error_returns_502(mock_extract):
    """When the LLM client raises LLMExtractionError, the route must return 502."""
    from app.llm.client import LLMExtractionError
    mock_extract.side_effect = LLMExtractionError("both models failed")

    response = client.post(
        "/api/analyze",
        data={"text": "Some offer text"},
    )

    assert response.status_code == 502
    assert "unavailable" in response.json()["detail"].lower()


@patch("app.api.routes_analyze.extract_offer_fields")
def test_analyze_response_shape(mock_extract):
    """The response must include all required top-level keys."""
    mock_extract.return_value = _empty_extraction()

    response = client.post(
        "/api/analyze",
        data={"text": "Some text"},
    )

    body = response.json()
    for key in ("verdict", "score", "language", "input_summary",
                "extracted", "flags", "unverifiable"):
        assert key in body, f"Missing key: {key}"
