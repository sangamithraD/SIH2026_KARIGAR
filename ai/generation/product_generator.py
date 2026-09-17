import logging
from typing import Optional
from ai.llm_client import default_llm_client
from ai.prompts.product import PRODUCT_GEN_SYSTEM_PROMPT, PRODUCT_GEN_USER_TEMPLATE
from ai.schemas.generation import ProductGenerationRequest, ProductGenerationResponse, StructuredProductFacts

logger = logging.getLogger("kai.product_generator")

from ai.translation.translator import translator_service

import re
import logging
from typing import Optional
from ai.llm_client import default_llm_client
from ai.prompts.product import PRODUCT_GEN_SYSTEM_PROMPT, PRODUCT_GEN_USER_TEMPLATE
from ai.schemas.generation import ProductGenerationRequest, ProductGenerationResponse
from ai.translation.translator import translator_service

logger = logging.getLogger("kai.product_generator")

def _contains_indic_script(text: str) -> bool:
    return any(ord(char) > 127 for char in text)

def _strip_indic_script(text: str) -> str:
    """Removes residual Tamil/Hindi script characters leaving clean English text."""
    if not text:
        return ""
    cleaned = re.sub(r'[\u0B80-\u0BFF\u0900-\u097F]', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

class ProductGenerator:
    """
    Generates structured e-commerce product listings in English from transcript, material, craft type, or manual inputs.
    Automatically translates Tamil/Indic voice input into English before saving to DB.
    Guarantees 100% English marketplace content.
    """

    def generate(self, req: ProductGenerationRequest) -> ProductGenerationResponse:
        original_transcript = req.transcript or "Handcrafted product creation"
        transcript_text = original_transcript
        
        # Translate Tamil / Indic script transcript into English
        if _contains_indic_script(transcript_text):
            try:
                src_lang = "hi" if any("\u0900" <= c <= "\u097F" for c in transcript_text) else "ta"
                translated_res = translator_service.translate(transcript_text, source_lang=src_lang, target_lang="en")
                translated = translated_res.get("translatedText", "")
                if translated and not _contains_indic_script(translated):
                    transcript_text = translated
                else:
                    # Strip any non-translated Indic words
                    transcript_text = _strip_indic_script(translated or transcript_text)
            except Exception as tr_err:
                logger.warning(f"Translation before product generation error: {tr_err}")
                transcript_text = _strip_indic_script(transcript_text)

        mat = req.material or "Natural Material"
        craft = req.craftType or "Handicrafts"
        extra = req.additionalInfo or "Handmade by local artisan"
        
        # Infer material, craft type, and specific product from English/translated text
        combined_text = (original_transcript + " " + transcript_text).lower()
        
        # Indic number word mapping
        indic_num_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "ஒன்று": 1, "இரண்டு": 2, "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5,
            "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5
        }

        # Infer material and craft type from English, Tamil, and Hindi
        if "புத்தர்" in combined_text or "buddha" in combined_text or "பொம்மை" in combined_text or "idol" in combined_text or "statue" in combined_text:
            craft = "Sculpture & Figurines"
            if "பீங்கான்" in combined_text or "ceramic" in combined_text or "terracotta" in combined_text:
                mat = "Ceracotta & Clay"
            elif "wood" in combined_text or "மரம்" in combined_text:
                mat = "Carved Wood"

        elif "palm" in combined_text or "leaf" in combined_text or "பனை" in combined_text:
            mat = "Palm Leaf"
            craft = "Basketry"
        elif "clay" in combined_text or "pot" in combined_text or "terracotta" in combined_text or "களிமண்" in combined_text:
            mat = "Terracotta Clay"
            craft = "Pottery"
        elif "bamboo" in combined_text or "cane" in combined_text or "மூங்கில்" in combined_text or "बांस" in combined_text:
            mat = "Bamboo"
            craft = "Weaving"
        elif "silk" in combined_text or "saree" in combined_text or "cotton" in combined_text or "பட்டு" in combined_text:
            mat = "Handloom Silk"
            craft = "Textile Weaving"

        user_prompt = PRODUCT_GEN_USER_TEMPLATE.format(
            transcript=transcript_text or "Handcrafted heritage artisan product",
            material=mat,
            craftType=craft,
            additionalInfo=extra,
            language="en"
        )

        det_lang = "Tamil" if _contains_indic_script(original_transcript) else ("Hindi" if any("\u0900" <= c <= "\u097F" for c in original_transcript) else "English")

        # Extract structured facts from verified speech
        duration_val = None
        days_match = re.search(r'(\d+(?:\.\d+)?|one|two|three|four|five|ஒன்று|இரண்டு|மூன்று|நான்கு|ஐந்து|एक|दो|तीन|चार|पांच)\s*(?:days|day|நாட்கள்|நாள்|दिन|தினங்கள்)', combined_text, re.IGNORECASE)
        if days_match:
            d_str = days_match.group(1).lower()
            duration_val = indic_num_map.get(d_str) if d_str in indic_num_map else float(d_str)

        dim_match = re.search(r'\b(\d+(?:\.\d+)?\s*(?:cm|mm|m|inch|inches|ft|feet)(?:\s*(?:width|height|length|wide|tall|long))?)\b', combined_text, re.IGNORECASE)
        dim_val = dim_match.group(1).strip() if dim_match else None

        weight_match = re.search(r'\b(\d+(?:\.\d+)?\s*(?:kg|g|grams|kilograms|lbs|pound|pounds))\b', combined_text, re.IGNORECASE)
        weight_val = weight_match.group(1).strip() if weight_match else None

        colour_match = re.search(r'\b(red|blue|green|black|white|yellow|brown|natural|golden|silver|terracotta)\b', combined_text, re.IGNORECASE)
        colour_val = colour_match.group(1).capitalize() if colour_match else None

        struct_facts = StructuredProductFacts(
            product_name=mat.title() + " Craft",
            category="Home Decor & Crafts",
            materials=[mat.title()],
            craft_method=craft.title(),
            colour=colour_val,
            dimensions=dim_val,
            weight=weight_val,
            work_duration_days=duration_val
        )

        def fallback_product():
            clean_trans = _strip_indic_script(transcript_text)
            
            # Formulate product name based directly on the thing/item used in description
            item_name = None
            if "buddha" in combined_text or "புத்தர்" in combined_text or "idol" in combined_text or "statue" in combined_text:
                item_name = "Buddha Idol"
            elif "basket" in combined_text or "கூடை" in combined_text or "टोकरी" in combined_text:
                item_name = "Storage Basket"
            elif "saree" in combined_text or "silk" in combined_text or "புடவை" in combined_text or "பட்டு" in combined_text:
                item_name = "Handloom Saree"
            elif "pot" in combined_text or "pitcher" in combined_text or "clay" in combined_text or "களிமண்" in combined_text or "பானை" in combined_text:
                item_name = "Earthen Vessel"
            elif "diya" in combined_text or "lamp" in combined_text or "விளக்கு" in combined_text:
                item_name = "Decorative Diya"
            elif "toy" in combined_text or "பொம்மை" in combined_text or "खिलौना" in combined_text:
                item_name = "Stacking Toy"
            elif "bag" in combined_text or "tote" in combined_text or "பை" in combined_text:
                item_name = "Artisan Tote Bag"
            elif "necklace" in combined_text or "choker" in combined_text or "மாலை" in combined_text:
                item_name = "Artisan Choker Necklace"
            else:
                # Extract main noun from translated text if available
                clean_words = [w.capitalize() for w in clean_trans.split() if len(w) > 3 and w.lower() not in ['this', 'made', 'with', 'cost', 'days', 'work', 'price', 'rupees', 'took', 'they', 'were', 'paid', 'artisan', 'product', 'material', 'craft', 'have', 'using', 'from']]
                if clean_words:
                    item_name = " ".join(clean_words[:2])
                else:
                    item_name = f"{mat.title()} Craft"

            name = f"Handcrafted {mat.title()} {item_name}".strip()
            # Clean up duplicates in title like "Handcrafted Bamboo Storage Basket"
            name = re.sub(rf'\b{re.escape(mat.title())}\s+{re.escape(mat.title())}\b', mat.title(), name, flags=re.IGNORECASE)

            struct_facts.product_name = name

            # Formulate 100% full-sentence English description without omitting any line
            if clean_trans and len(clean_trans) > 5:
                # Use complete full-sentence translation directly
                full_desc = clean_trans
                if not full_desc.endswith('.'):
                    full_desc += '.'
            else:
                full_desc = f"Authentic handcrafted {mat.lower()} {item_name.lower()} carefully made by local heritage artisans using traditional {craft.lower()} techniques."

            # Generate clean normalized tags strictly from facts
            tags = [
                f"{mat.lower()} craft",
                f"handcrafted {mat.lower()}",
                f"{craft.lower()}",
                name.lower()
            ]
            unique_tags = list(dict.fromkeys([t.strip().lower() for t in tags if t.strip()]))

            return ProductGenerationResponse(
                productName=name,
                category="Home Decor & Crafts",
                material=mat.title(),
                craftType=craft.title(),
                description=full_desc,
                keywords=unique_tags,
                structuredFacts=struct_facts,
                originalTranscript=original_transcript,
                detectedLanguage=det_lang,
                translatedEnglish=transcript_text
            )

        try:
            res = default_llm_client.generate_structured(
                system_prompt=PRODUCT_GEN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=ProductGenerationResponse,
                fallback_factory=fallback_product
            )
            res.productName = _strip_indic_script(res.productName) or fallback_product().productName
            res.description = _strip_indic_script(res.description) or fallback_product().description
            res.material = _strip_indic_script(res.material) or mat.title()
            res.structuredFacts = res.structuredFacts or struct_facts
            res.originalTranscript = original_transcript
            res.detectedLanguage = det_lang
            res.translatedEnglish = transcript_text
            return res
        except Exception as e:
            logger.warning(f"Product generation failed: {e}. Returning fallback.")
            return fallback_product()

product_generator = ProductGenerator()
