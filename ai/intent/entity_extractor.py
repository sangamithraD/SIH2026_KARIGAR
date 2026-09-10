import re
import logging
from typing import Dict, Any

logger = logging.getLogger("kai.entity_extractor")

class EntityExtractor:
    """
    Extracts structured action parameters (e.g., name, quantity, unit, price) from transcript text.
    Supports Tamil, Hindi, English, Tanglish, and Hinglish number/unit/material patterns.
    """
    
    UNIT_MAP = {
        "kg": "kg", "kilo": "kg", "kilogram": "kg", "kilograms": "kg", "கிலோ": "kg", "किलोग्राम": "kg", "किग्रा": "kg",
        "g": "g", "gram": "g", "grams": "g", "கிராம்": "g", "ग्राम": "g",
        "m": "meters", "meter": "meters", "meters": "meters", "மீட்டர்": "meters", "मीटर": "meters",
        "piece": "pieces", "pieces": "pieces", "துண்டு": "pieces", "பிஸ்": "pieces", "पीस": "pieces",
        "bundle": "bundles", "bundles": "bundles", "கட்டு": "bundles", "बंडल": "bundles"
    }

    MATERIAL_MAP = {
        "bamboo": "Bamboo", "மூங்கில்": "Bamboo", "बाँस": "Bamboo", "बांस": "Bamboo",
        "jute": "Jute", "சணல்": "Jute", "जूट": "Jute",
        "clay": "Clay", "terracotta": "Clay", "களிமண்": "Clay", "मिट्टी": "Clay",
        "cotton": "Cotton", "பருத்தி": "Cotton", "सूती": "Cotton",
        "wood": "Wood", "மரம்": "Wood", "लकड़ी": "Wood",
        "yarn": "Yarn", "நூல்": "Yarn", "धागा": "Yarn",
        "silk": "Silk", "பட்டு": "Silk", "रेशम": "Silk"
    }

    WORD_TO_NUM = {
        "five": 5, "ஐந்து": 5, "அஞ்சு": 5, "पाँच": 5, "पांच": 5,
        "ten": 10, "பத்து": 10, "दस": 10,
        "two": 2, "இரண்டு": 2, "ரெண்டு": 2, "दो": 2,
        "one": 1, "ஒன்று": 1, "ஒன்னு": 1, "एक": 1,
        "three": 3, "மூன்று": 3, "மூணு": 3, "तीन": 3,
        "four": 4, "நான்கு": 4, "நாலு": 4, "चार": 4,
        "six": 6, "ஆறு": 6, "छह": 6,
        "seven": 7, "ஏழு": 7, "सात": 7,
        "eight": 8, "எட்டு": 8, "आठ": 8,
        "nine": 9, "ஒன்பது": 9, "नौ": 9
    }

    def extract(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract parameters dictionary based on text and classified intent.
        """
        params: Dict[str, Any] = {}
        lowered = text.lower()

        # Extract material name
        for raw_mat, canonical in self.MATERIAL_MAP.items():
            if raw_mat in lowered or raw_mat in text:
                params["name"] = canonical
                params["material"] = canonical
                break

        # Extract numeric quantity and word numbers
        qty_match = re.search(r"(\d+(?:\.\d+)?)", text)
        if qty_match:
            try:
                val = float(qty_match.group(1))
                params["quantity"] = int(val) if val.is_integer() else val
            except ValueError:
                pass
        else:
            for word, num in self.WORD_TO_NUM.items():
                if word in lowered or word in text:
                    params["quantity"] = num
                    break

        # Extract unit
        for raw_unit, canonical_unit in self.UNIT_MAP.items():
            if raw_unit in lowered or raw_unit in text:
                params["unit"] = canonical_unit
                break

        # Extract price if present
        price_match = re.search(r"(?:rs\.?|rupees|₹|ரூபாய்|ரொக்கம்|रुपये)\s*(\d+)", text, re.IGNORECASE)
        if price_match:
            params["price"] = int(price_match.group(1))

        # Sensible defaults if intent is ADD_RAW_MATERIAL and params were missing
        if intent == "ADD_RAW_MATERIAL":
            if "name" not in params:
                params["name"] = "Bamboo"
            if "quantity" not in params:
                params["quantity"] = 5
            if "unit" not in params:
                params["unit"] = "kg"

        return params

entity_extractor = EntityExtractor()
