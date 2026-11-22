#Defines the initial request/response models for /api/health and /api/analyze.
from typing import Literal, Optional
from pydantic import BaseModel, Field

VerdictType = Literal["danger", "caution", "fewer_concerns"]

class HealthResponse(BaseModel):
    status: str = "ok"
    env: str

class ExtractedField(BaseModel):
    value: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_snippet: str = ""

class AnalyzeResponse(BaseModel):
    verdict: VerdictType = "caution"
    score: int = Field(default=50, ge=0, le=100)
    language: str = "bn"
    input_summary: str
    extracted: dict[str, ExtractedField] = Field(default_factory=dict)
    flags: list[dict] = Field(default_factory=list)
    missing_clauses: list[str] = Field(default_factory=list)
    questions_to_ask: list[dict[str, str]] = Field(default_factory=list)
    unverifiable: list[str] = Field(default_factory=list)
    helplines: list[dict[str, str]] = Field(default_factory=list)
    audio_script_bn: str = ""