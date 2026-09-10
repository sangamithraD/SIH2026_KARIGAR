import logging
from typing import Dict, Any, Optional

from ai.schemas.speech import TranscriptionResponse, TranscriptionRequest
from ai.schemas.intent import IntentRequest, IntentResponse, VoiceCommandPipelineResponse
from ai.schemas.generation import (
    ProductGenerationRequest, ProductGenerationResponse,
    StoryGenerationRequest, StoryGenerationResponse,
    IdeasGenerationRequest, IdeasGenerationResponse
)
from ai.schemas.image import ImageAnalysisResponse, ImageEnhanceRequest, ImageEnhanceResponse
from ai.schemas.pricing import PricingAssistanceRequest, PricingAssistanceResponse
from ai.schemas.recommendations import TutorialRecommendationRequest, TutorialRecommendationResponse

from ai.speech.whisper_service import speech_service
from ai.translation.translator import translator_service
from ai.intent.intent_classifier import intent_classifier
from ai.intent.entity_extractor import entity_extractor
from ai.intent.action_mapper import action_mapper
from ai.generation.product_generator import product_generator
from ai.generation.story_generator import story_generator
from ai.generation.ideas_generator import ideas_generator
from ai.image.quality_analyzer import photo_quality_analyzer
from ai.image.enhancer import image_enhancer_pipeline
from ai.pricing.complexity_assessor import craft_complexity_assessor
from ai.recommendations.tutorial_recommender import tutorial_recommender

logger = logging.getLogger("kai.service")

class AIService:
    """
    Unified AI Service Facade for KAI.
    Combines speech-to-text, translation, intent understanding, product & story generation,
    computer vision photo pipeline, pricing assistance, and tutorial recommendations.
    """

    def transcribe(self, audio_data: Any, language_hint: Optional[str] = None) -> TranscriptionResponse:
        return speech_service.transcribe_audio(audio_data, language_hint=language_hint)

    def classify_intent(self, text: str, language: str = "ta") -> IntentResponse:
        intent_name, confidence = intent_classifier.classify(text, language=language)
        parameters = entity_extractor.extract(text, intent_name)
        return action_mapper.build_action_contract(intent_name, confidence, parameters)

    def process_voice_command(
        self,
        transcript_text: Optional[str] = None,
        audio_data: Optional[Any] = None,
        language_hint: str = "ta"
    ) -> VoiceCommandPipelineResponse:
        """
        Complete Voice Command Pipeline:
        Voice -> Speech-to-text -> Language -> Intent -> Entities -> Validation -> Action Contract
        """
        # Step 1: Speech to Text (if audio provided)
        if audio_data is not None:
            stt_res = self.transcribe(audio_data, language_hint=language_hint)
            text = stt_res.text
            lang = stt_res.language
            stt_conf = stt_res.confidence
        else:
            text = transcript_text or "I have five kilograms of bamboo"
            lang = language_hint
            stt_conf = 0.95

        # Step 2: Intent Classification & Parameter Extraction
        action_contract = self.classify_intent(text, language=lang)
        
        # Step 3: Trigger downstream generation if intent requires it
        generated_product = None
        recommended_ideas = None
        msg = f"Understood intent '{action_contract.intent}'."

        if action_contract.intent == "ADD_RAW_MATERIAL":
            qty = action_contract.parameters.get("quantity", 5)
            unit = action_contract.parameters.get("unit", "kg")
            mat = action_contract.parameters.get("name", "Bamboo")
            msg = f"Action proposal: Add {qty} {unit} of {mat} to your inventory."

        elif action_contract.intent == "GENERATE_PRODUCT_IDEAS":
            mat = action_contract.parameters.get("name", "Bamboo")
            ideas_req = IdeasGenerationRequest(rawMaterial=mat)
            ideas_res = self.generate_ideas(ideas_req)
            recommended_ideas = ideas_res.model_dump()
            msg = f"Generated {len(ideas_res.ideas)} product ideas for {mat}."

        elif action_contract.intent in ["ADD_PRODUCT", "CREATE_LISTING"]:
            mat = action_contract.parameters.get("name", "Bamboo")
            prod_req = ProductGenerationRequest(transcript=text, material=mat)
            prod_res = self.generate_product(prod_req)
            generated_product = prod_res.model_dump()
            msg = f"Generated product listing proposal for '{prod_res.productName}'."

        elif action_contract.intent == "PUBLISH_PRODUCT":
            msg = "Action proposal: Publish product listing to marketplace."

        return VoiceCommandPipelineResponse(
            transcript=text,
            language=lang,
            intent=action_contract.intent,
            confidence=action_contract.confidence,
            parameters=action_contract.parameters,
            requires_confirmation=action_contract.requires_confirmation,
            message=msg,
            generated_product=generated_product,
            recommended_ideas=recommended_ideas
        )

    def generate_product(self, req: ProductGenerationRequest) -> ProductGenerationResponse:
        return product_generator.generate(req)

    def generate_story(self, req: StoryGenerationRequest) -> StoryGenerationResponse:
        return story_generator.generate(req)

    def generate_ideas(self, req: IdeasGenerationRequest) -> IdeasGenerationResponse:
        return ideas_generator.generate(req)

    def analyze_image(self, image_data: Any) -> ImageAnalysisResponse:
        return photo_quality_analyzer.analyze(image_data)

    def enhance_image(self, image_path: str, remove_bg: bool = True) -> ImageEnhanceResponse:
        return image_enhancer_pipeline.enhance(image_path, remove_background=remove_bg)

    def assess_pricing(self, req: PricingAssistanceRequest) -> PricingAssistanceResponse:
        return craft_complexity_assessor.assess(req)

    def recommend_tutorials(self, req: TutorialRecommendationRequest) -> TutorialRecommendationResponse:
        return tutorial_recommender.recommend(req)

# Global unified service instance
kai_ai_service = AIService()
