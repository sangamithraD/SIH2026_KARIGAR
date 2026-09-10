from pydantic import BaseModel, Field
from typing import Optional, List

class PricingAssistanceRequest(BaseModel):
    productName: str = Field(..., description="Product title")
    material: str = Field(..., description="Raw material name")
    craftType: str = Field(..., description="Craft or technique used")
    productionTimeHours: Optional[float] = Field(None, description="Time taken to produce in hours")
    description: Optional[str] = Field(None, description="Product description")

class PricingAssistanceResponse(BaseModel):
    complexityLevel: int = Field(..., ge=1, le=5, description="Craft complexity rating from 1 (Simple) to 5 (Intricate)")
    effortCategory: str = Field(..., description="Effort classification (Low, Medium, High, Expert)")
    craftCategory: str = Field(..., description="Category classification (e.g. Weaving, Pottery, Carving)")
    suggestedComplexityMultiplier: float = Field(..., description="Recommended labor multiplier for backend calculation")
    notes: List[str] = Field(default_factory=list, description="Guidance notes for artisan regarding fair pricing factors")
