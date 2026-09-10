from pydantic import BaseModel, Field
from typing import List, Optional

class TutorialRecommendationRequest(BaseModel):
    material: Optional[str] = Field(None, description="Raw material name (e.g. Bamboo, Clay)")
    craftType: Optional[str] = Field(None, description="Craft type (e.g. Weaving, Pottery)")
    product: Optional[str] = Field(None, description="Product title or idea name")
    language: Optional[str] = Field("ta", description="Preferred language (ta, hi, en)")
    difficulty: Optional[str] = Field(None, description="Target difficulty (Beginner, Intermediate, Advanced)")

class TutorialItem(BaseModel):
    id: str = Field(..., description="Unique tutorial ID")
    title: str = Field(..., description="Tutorial title in preferred language")
    craftType: str = Field(..., description="Target craft type")
    material: str = Field(..., description="Target material")
    difficulty: str = Field(..., description="Skill difficulty")
    durationMinutes: int = Field(..., description="Estimated tutorial duration in minutes")
    language: str = Field(..., description="Language of tutorial")
    url: str = Field(..., description="Curated/Verified tutorial resource URL")
    thumbnailUrl: str = Field(..., description="Thumbnail image URL")
    stepsSummary: List[str] = Field(default_factory=list, description="Key steps in tutorial")

class TutorialRecommendationResponse(BaseModel):
    tutorials: List[TutorialItem] = Field(..., description="List of matching tutorial resources")
