import logging
from typing import Dict, Any
from ai.schemas.pricing import PricingAssistanceRequest, PricingAssistanceResponse

logger = logging.getLogger("kai.complexity_assessor")

class CraftComplexityAssessor:
    """
    Evaluates craft complexity level and labor effort category for backend deterministic pricing.
    Does NOT calculate final selling price (backend owns deterministic price calculation).
    """

    CRAFT_CATEGORIES = {
        "bamboo": "Weaving & Woodwork",
        "jute": "Textiles & Weaving",
        "clay": "Pottery & Ceramics",
        "terracotta": "Pottery & Ceramics",
        "cotton": "Textiles & Apparel",
        "silk": "Textiles & Apparel",
        "wood": "Carving & Carpentry"
    }

    def assess(self, req: PricingAssistanceRequest) -> PricingAssistanceResponse:
        mat_lower = req.material.lower()
        hours = req.productionTimeHours or 3.0

        # Craft category mapping
        craft_cat = "Handicrafts"
        for key, val in self.CRAFT_CATEGORIES.items():
            if key in mat_lower or key in req.craftType.lower():
                craft_cat = val
                break

        # Complexity level calculation based on production hours & description
        complexity = 2
        if hours < 2.0:
            complexity = 1
            effort = "Low"
            multiplier = 1.0
        elif hours <= 4.0:
            complexity = 2
            effort = "Medium"
            multiplier = 1.25
        elif hours <= 8.0:
            complexity = 3
            effort = "High"
            multiplier = 1.50
        elif hours <= 15.0:
            complexity = 4
            effort = "Expert"
            multiplier = 1.85
        else:
            complexity = 5
            effort = "Master Artisan"
            multiplier = 2.25

        notes = [
            f"Assessed complexity rating: {complexity}/5 based on {hours} hours of craftsmanship.",
            f"Effort category classified as '{effort}'.",
            "This complexity rating provides input to the backend's deterministic formula (Material + Labour + Packaging).",
            "The final selling price will be determined deterministically by the backend."
        ]

        return PricingAssistanceResponse(
            complexityLevel=complexity,
            effortCategory=effort,
            craftCategory=craft_cat,
            suggestedComplexityMultiplier=multiplier,
            notes=notes
        )

craft_complexity_assessor = CraftComplexityAssessor()
