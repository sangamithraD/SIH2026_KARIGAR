from pydantic import BaseModel, Field
from typing import Optional

class TranscriptionRequest(BaseModel):
    language: Optional[str] = Field(None, description="Optional target language hint (ta, hi, en)")

class TranscriptionResponse(BaseModel):
    text: str = Field(..., description="Transcribed text from speech")
    language: str = Field(..., description="Detected language code (ta, hi, en, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
