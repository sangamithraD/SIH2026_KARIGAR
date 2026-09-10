from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ImageAnalysisResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Overall image quality score (0-100)")
    issues: List[str] = Field(default_factory=list, description="Identified photo issues (e.g. underexposed, blurry)")
    suggestions: List[str] = Field(default_factory=list, description="Actionable improvement suggestions for artisan")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Technical photo metrics (brightness, blur score, resolution)")

class ImageEnhanceRequest(BaseModel):
    removeBackground: bool = Field(True, description="Whether to perform background removal")
    autoCrop: bool = Field(True, description="Whether to auto-crop whitespace/clutter")

class ImageEnhanceResponse(BaseModel):
    originalImageUrl: str = Field(..., description="Path/URL to preserved original image")
    enhancedImageUrl: str = Field(..., description="Path/URL to enhanced product image")
    backgroundRemovedImageUrl: Optional[str] = Field(None, description="Path/URL to background-removed product image")
    status: str = Field("success", description="Status of image processing")
    appliedEnhancements: List[str] = Field(default_factory=list, description="List of applied operations (e.g. brightness correction, sharpening, background removal)")
