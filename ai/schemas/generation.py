from pydantic import BaseModel, Field
from typing import List, Optional

class StructuredProductFacts(BaseModel):
    product_name: Optional[str] = Field(None, description="Inferred product name")
    category: Optional[str] = Field(None, description="Product category")
    materials: List[str] = Field(default_factory=list, description="List of materials used")
    colour: Optional[str] = Field(None, description="Color of product if mentioned")
    dimensions: Optional[str] = Field(None, description="Dimensions if mentioned")
    weight: Optional[str] = Field(None, description="Weight if mentioned")
    craft_method: Optional[str] = Field(None, description="Craft method used")
    features: List[str] = Field(default_factory=list, description="Key product features")
    uses: List[str] = Field(default_factory=list, description="Intended uses")
    work_duration_days: Optional[float] = Field(None, description="Duration in days if mentioned")


class ProductGenerationRequest(BaseModel):
    transcript: Optional[str] = Field(None, description="Voice transcript or text input")
    language: Optional[str] = Field("en", description="Target output language")
    material: Optional[str] = Field(None, description="Raw material name")
    craftType: Optional[str] = Field(None, description="Type of craft")
    additionalInfo: Optional[str] = Field(None, description="Any extra specs provided by artisan")


class ProductGenerationResponse(BaseModel):
    productName: str = Field(..., description="Marketplace-ready product title")
    category: str = Field(..., description="E-commerce product category")
    material: str = Field(..., description="Primary raw material used")
    craftType: str = Field(..., description="Craft or technique used")
    description: str = Field(..., description="Concise, truthful marketplace description")
    keywords: List[str] = Field(default_factory=list, description="Keywords for search optimization")
    structuredFacts: Optional[StructuredProductFacts] = Field(default=None, description="Extracted product facts")
    originalTranscript: Optional[str] = Field(default=None, description="Original speech transcript")
    detectedLanguage: Optional[str] = Field(default=None, description="Detected source language")
    translatedEnglish: Optional[str] = Field(default=None, description="Translated English meaning")

class StoryGenerationRequest(BaseModel):
    transcript: str = Field(..., description="Artisan's personal experience, tradition, or inspiration text")
    language: Optional[str] = Field("en", description="Output language")

class StoryGenerationResponse(BaseModel):
    story: str = Field(..., description="Refined, authentic craft story preserving original facts")
    keyElements: List[str] = Field(default_factory=list, description="Extracted key story highlights")

class IdeasGenerationRequest(BaseModel):
    rawMaterial: str = Field(..., description="Name of the raw material (e.g., Bamboo, Clay, Jute)")
    quantity: Optional[float] = Field(None, description="Quantity available")
    unit: Optional[str] = Field(None, description="Unit of measurement (kg, meters, pieces)")
    skillLevel: Optional[str] = Field("Beginner", description="Skill level (Beginner, Intermediate, Advanced)")
    existingMaterials: Optional[List[str]] = Field(default_factory=list, description="Other materials available")

class IdeaItem(BaseModel):
    title: str = Field(..., description="Idea name")
    description: str = Field(..., description="What the product is and how to make it")
    difficulty: str = Field(..., description="Difficulty level (Easy, Medium, Hard)")
    materials: List[str] = Field(..., description="Materials required")
    estimatedHours: float = Field(..., description="Estimated hours to complete")
    estimatedPrice: float = Field(..., description="Estimated market value range in INR")
    reason: str = Field(..., description="Why this idea fits the material and quantity")

class IdeasGenerationResponse(BaseModel):
    ideas: List[IdeaItem] = Field(..., description="List of 3 to 5 product ideas")
