import re
import logging
from typing import Tuple, Dict, Any
from ai.llm_client import default_llm_client
from ai.prompts.intent import INTENT_SYSTEM_PROMPT, INTENT_USER_PROMPT_TEMPLATE
from ai.schemas.intent import IntentResponse

logger = logging.getLogger("kai.intent_classifier")

class IntentClassifier:
    """
    Classifies artisan voice transcripts or typed text into one of the 11 supported KAI intents.
    Supports Tamil, Hindi, English, Tanglish, and Hinglish inputs with pattern rules + LLM fallback.
    """
    
    PATTERNS = {
        "VIEW_RAW_MATERIALS": [
            r"\b(?:view raw materials|show materials|my stock|my materials|raw materials list|list materials)\b",
            r"மூலப்பொருட்கள்|பொருட்கள் இருப்பு|இருப்பு காட்டு|மூலப்பொருட்களைக் காட்டு",
            r"कच्चा माल दिखाएं|कच्चा माल दिखाओ|स्टॉक दिखाएं|स्टॉक दिखाओ|कच्चा माल देखें"
        ],
        "GENERATE_PRODUCT_IDEAS": [
            r"\b(?:what can i make|make with|ideas|suggest|product ideas|what to create|recommend items|what to make)\b",
            r"என்ன செய்யலாம்|தயாரிக்கலாம்|யோசனைகள்|என்ன பண்ணலாம்",
            r"क्या बना सकते हैं|सुझाव|क्या बनाएँ|विचार"
        ],
        "ADD_PRODUCT": [
            r"\b(?:add product|new product|create product|made a basket|crafted a|handmade basket)\b",
            r"புதிய பொருள்|பொருள் சேர்க்க|பொருள் தயாரித்தேன்",
            r"नया उत्पाद|उत्पाद जोड़ें|टोकरी बनाई"
        ],
        "PUBLISH_PRODUCT": [
            r"\b(?:publish|publish this product|put on marketplace|post listing|sell this product|publish product)\b",
            r"வெளியிடு|விற்பனைக்கு வை|பதிவேற்று",
            r"प्रकाशित करें|बेचें|मार्केटप्लेस|पब्लिश"
        ],
        "VIEW_PRODUCTS": [
            r"\b(?:view products|show my products|my products|list products|see products)\b",
            r"என் பொருட்கள்|பொருட்களைக் காட்டு|பொருட்கள் பட்டியல்",
            r"मेरे उत्पाद|उत्पाद दिखाएं|उत्पाद देखें"
        ],
        "ADD_RAW_MATERIAL": [
            r"\b(?:have|got|added|bought|store|stock of|add)\b.*\b(?:bamboo|jute|clay|wood|cotton|yarn|silk|leather|beads|terracotta)\b",
            r"\b(?:kilogram|kilograms|kg|grams|g|meters|m|bundles|pieces)\b.*\b(?:bamboo|jute|clay|wood|cotton|yarn|silk)\b",
            r"மூங்கில்|கிலோ|மரச்சாமான்கள்|களிமண்|சணல்|பருத்தி|மூலப்பொருள் சேர்க்க",
            r"बाँस|बांस|किलोग्राम|किग्रा|मिट्टी|धागा|कच्चा माल जोड़ें",
            r"\b(?:kitta|irukku|iruku|sekka|sertaen|laaya|paas)\b"
        ],
        "FIND_TUTORIAL": [
            r"\b(?:tutorial|how to make|video|learn|guide|teaching|learning)\b",
            r"கற்றுக்கொள்ள|பயிற்சி|வீடியோ|எப்படி செய்வது",
            r"ट्यूटोरियल|सीखें|वीडियो|कैसे बनाएं"
        ],
        "UPDATE_PRICE": [
            r"\b(?:update price|change price|set price|price to)\b",
            r"விலை மாற்ற|விலை அமை|விலை திருத்து",
            r"कीमत बदलें|मूल्य बदलें|कीमत सेट करें"
        ],
        "CREATE_LISTING": [
            r"\b(?:create listing|draft listing|make listing|generate listing)\b",
            r"பட்டியல் உருவாக்கு|லிஸ்டிங்",
            r"लिस्टिंग बनाएं|ड्राफ्ट"
        ],
        "PUBLISH_RAW_MATERIAL": [
            r"\b(?:publish raw material|sell raw material|list material for sale)\b",
            r"மூலப்பொருள் விற்பனை|மூலப்பொருள் வெளியிட",
            r"कच्चा माल बेचें|कच्चा माल प्रकाशित करें"
        ],
        "VIEW_PUBLISHED_PRODUCTS": [
            r"\b(?:view published|published products|live products)\b",
            r"வெளியிடப்பட்ட பொருட்கள்|விற்பனையில் உள்ளவை",
            r"प्रकाशित उत्पाद|लाइव उत्पाद"
        ]
    }

    def classify(self, text: str, language: str = "ta") -> Tuple[str, float]:
        """
        Returns (intent_name, confidence_score).
        """
        clean_text = text.strip()
        lowered = clean_text.lower()

        # 1. Direct Pattern matching for instant high accuracy
        for intent, regex_list in self.PATTERNS.items():
            for regex in regex_list:
                if re.search(regex, lowered, re.IGNORECASE):
                    logger.info(f"Pattern hit for intent '{intent}' from text: '{clean_text}'")
                    return intent, 0.95

        # 2. LLM fallback classifier
        user_prompt = INTENT_USER_PROMPT_TEMPLATE.format(text=clean_text, language=language)
        
        def fallback_intent_obj():
            if any(term in lowered for term in ["kg", "kilo", "kilogram", "5", "10", "மூங்கில்", "बाँस", "समीग्री"]):
                return IntentResponse(intent="ADD_RAW_MATERIAL", confidence=0.85, parameters={"name": "Bamboo", "quantity": 5, "unit": "kg"})
            if any(term in lowered for term in ["make", "ideas", "செய்யலாம்", "बनाएँ"]):
                return IntentResponse(intent="GENERATE_PRODUCT_IDEAS", confidence=0.85, parameters={})
            return IntentResponse(intent="GENERATE_PRODUCT_IDEAS", confidence=0.75, parameters={})

        try:
            res: IntentResponse = default_llm_client.generate_structured(
                system_prompt=INTENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=IntentResponse,
                fallback_factory=fallback_intent_obj
            )
            return res.intent, res.confidence
        except Exception as e:
            logger.warning(f"Intent classification LLM call failed: {e}")
            fallback = fallback_intent_obj()
            return fallback.intent, fallback.confidence

intent_classifier = IntentClassifier()
