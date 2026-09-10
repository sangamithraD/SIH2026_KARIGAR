import logging
from typing import Optional
from ai.llm_client import default_llm_client
from ai.prompts.product import PRODUCT_GEN_SYSTEM_PROMPT, PRODUCT_GEN_USER_TEMPLATE
from ai.schemas.generation import ProductGenerationRequest, ProductGenerationResponse

logger = logging.getLogger("kai.product_generator")

from ai.translation.translator import translator_service

def _contains_indic_script(text: str) -> bool:
    return any(ord(char) > 127 for char in text)

class ProductGenerator:
    """
    Generates structured e-commerce product listings in English from transcript, material, craft type, or manual inputs.
    Automatically translates Tamil/Indic voice input into English before saving to DB.
    """

    def generate(self, req: ProductGenerationRequest) -> ProductGenerationResponse:
        transcript_text = req.transcript or "Handcrafted product creation"
        
        # Translate Tamil / Indic script transcript into English for DB storage
        if _contains_indic_script(transcript_text):
            try:
                translated_res = translator_service.translate(transcript_text, target_lang="en")
                transcript_text = translated_res.get("translatedText", transcript_text)
            except Exception as tr_err:
                logger.warning(f"Translation before product generation error: {tr_err}")

        mat = req.material or "Natural Material"
        craft = req.craftType or "Handicrafts"
        extra = req.additionalInfo or "Handmade by local artisan"
        
        # Infer material and craft type from English text if default
        txt_lower = transcript_text.lower()
        if "palm" in txt_lower or "leaf" in txt_lower:
            mat = "Palm Leaf"
            craft = "Basketry"
        elif "clay" in txt_lower or "pot" in txt_lower or "terracotta" in txt_lower:
            mat = "Terracotta Clay"
            craft = "Pottery"
        elif "bamboo" in txt_lower or "cane" in txt_lower:
            mat = "Bamboo"
            craft = "Weaving"
        elif "silk" in txt_lower or "saree" in txt_lower or "cotton" in txt_lower:
            mat = "Handloom Silk"
            craft = "Textile Weaving"
        elif "wood" in txt_lower or "toy" in txt_lower:
            mat = "Natural Wood"
            craft = "Wood Carving"

        user_prompt = PRODUCT_GEN_USER_TEMPLATE.format(
            transcript=transcript_text,
            material=mat,
            craftType=craft,
            additionalInfo=extra,
            language="en"
        )

        def fallback_product():
            name = f"Handcrafted {mat.title()} {craft.title()} Product"
            if "basket" in txt_lower:
                name = f"Handwoven {mat.title()} Basket"
            elif "pot" in txt_lower or "clay" in txt_lower:
                name = f"Handcrafted {mat.title()} Pot"
            elif "saree" in txt_lower or "silk" in txt_lower:
                name = f"Traditional {mat.title()} Saree"
            elif "toy" in txt_lower or "wood" in txt_lower:
                name = f"Artisan {mat.title()} Craft"

            return ProductGenerationResponse(
                productName=name,
                category="Home Decor & Crafts" if "pot" not in txt_lower else "Pottery & Kitchenware",
                material=mat.title(),
                craftType=craft.title(),
                description=f"Authentic handcrafted {mat.lower()} product carefully made by local heritage artisans. {transcript_text}",
                keywords=[mat.lower(), craft.lower(), "handmade", "artisan", "authentic-craft"]
            )

        try:
            return default_llm_client.generate_structured(
                system_prompt=PRODUCT_GEN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=ProductGenerationResponse,
                fallback_factory=fallback_product
            )
        except Exception as e:
            logger.warning(f"Product generation failed: {e}. Returning fallback.")
            return fallback_product()

product_generator = ProductGenerator()
