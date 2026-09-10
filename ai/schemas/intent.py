from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class IntentRequest(BaseModel):
    text: str = Field(..., description="Transcript or text input from artisan")
    language: Optional[str] = Field("ta", description="Input language code (ta, hi, en)")

class IntentResponse(BaseModel):
    intent: str = Field(..., description="Detected intent name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters (name, quantity, unit, price, material, etc.)")
    requires_confirmation: bool = Field(False, description="Flag indicating if artisan confirmation is required")

class VoiceCommandPipelineResponse(BaseModel):
    transcript: str = Field(..., description="Transcribed audio text")
    language: str = Field(..., description="Detected language code")
    intent: str = Field(..., description="Detected intent name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted action parameters")
    requires_confirmation: bool = Field(False, description="Whether confirmation is required before execution")
    message: str = Field(..., description="Friendly response message for the artisan")
    generated_product: Optional[Dict[str, Any]] = Field(None, description="Product data if intent triggered generation")
    recommended_ideas: Optional[Any] = Field(None, description="Ideas data if intent requested product ideas")
