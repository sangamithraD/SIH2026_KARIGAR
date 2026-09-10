import os
import tempfile
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from ai.schemas.speech import TranscriptionResponse, TranscriptionRequest
from ai.schemas.intent import IntentRequest, IntentResponse, VoiceCommandPipelineResponse
from ai.schemas.generation import (
    ProductGenerationRequest, ProductGenerationResponse,
    StoryGenerationRequest, StoryGenerationResponse,
    IdeasGenerationRequest, IdeasGenerationResponse
)
from ai.schemas.image import ImageAnalysisResponse, ImageEnhanceResponse
from ai.schemas.pricing import PricingAssistanceRequest, PricingAssistanceResponse
from ai.schemas.recommendations import TutorialRecommendationRequest, TutorialRecommendationResponse
from ai.service import kai_ai_service

logger = logging.getLogger("kai.api")

router = APIRouter()

@router.get("/api/ai/health", summary="AI Service Health Check")
async def health_check():
    return {
        "status": "healthy",
        "service": "KAI AI Engine",
        "supported_languages": ["ta", "hi", "en"]
    }

@router.post("/api/ai/transcribe", response_model=TranscriptionResponse, summary="Speech-to-Text Transcription")
async def transcribe_audio(
    file: Optional[UploadFile] = File(None),
    language: Optional[str] = Form(None)
):
    """
    Transcribe audio file (WAV, MP3, M4A, OGG) using faster-whisper.
    """
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "audio.wav")[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        try:
            result = kai_ai_service.transcribe(tmp_path, language_hint=language)
            return result
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        # Fallback demonstration if called without file upload
        return kai_ai_service.transcribe(None, language_hint=language)

@router.post("/api/ai/intent", response_model=IntentResponse, summary="Voice Command Intent Understanding")
async def classify_voice_intent(request: IntentRequest):
    """
    Classify artisan text or voice transcript into one of 11 KAI intents and extract action parameters.
    """
    return kai_ai_service.classify_intent(request.text, language=request.language or "ta")

@router.post("/api/voice/command", response_model=VoiceCommandPipelineResponse, summary="Full Voice Command Pipeline")
async def voice_command_pipeline(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: Optional[str] = Form("ta")
):
    """
    Complete Voice Pipeline: Audio -> STT -> Intent -> Entities -> Action Contract.
    """
    tmp_path = None
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "audio.wav")[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    
    try:
        res = kai_ai_service.process_voice_command(
            transcript_text=text,
            audio_data=tmp_path,
            language_hint=language or "ta"
        )
        return res
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/api/ai/generate-product", response_model=ProductGenerationResponse, summary="Generate E-commerce Product Listing")
async def generate_product(request: ProductGenerationRequest):
    """
    Generate structured, truthful product listing JSON from transcript and specs.
    """
    return kai_ai_service.generate_product(request)

@router.post("/api/ai/generate-story", response_model=StoryGenerationResponse, summary="Generate Craft Story")
async def generate_story(request: StoryGenerationRequest):
    """
    Transform artisan experience into a truthful brand story without fabricating cultural history.
    """
    return kai_ai_service.generate_story(request)

@router.post("/api/ai/generate-ideas", response_model=IdeasGenerationResponse, summary="Generate Product Ideas from Raw Material")
async def generate_ideas(request: IdeasGenerationRequest):
    """
    Suggest 3 to 5 realistic product ideas based on available raw material, quantity, and skill.
    """
    return kai_ai_service.generate_ideas(request)

@router.post("/api/ai/analyze-image", response_model=ImageAnalysisResponse, summary="Photo Quality Computer Vision Analysis")
async def analyze_image(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None)
):
    """
    Analyze photo lighting, focus blur, background clutter, framing, and resolution using OpenCV.
    """
    tmp_path = None
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        target_path = tmp_path
    elif image_path and os.path.exists(image_path):
        target_path = image_path
    else:
        # Create a sample default image for demonstration if none provided
        from ai.config import TEMP_DIR
        import numpy as np, cv2
        demo_img = np.ones((600, 800, 3), dtype=np.uint8) * 180
        cv2.putText(demo_img, "KAI Demo Product", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (50, 50, 50), 2)
        demo_path = os.path.join(TEMP_DIR, "demo_input.jpg")
        cv2.imwrite(demo_path, demo_img)
        target_path = demo_path

    try:
        return kai_ai_service.analyze_image(target_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/api/ai/enhance-image", response_model=ImageEnhanceResponse, summary="Image Enhancement & Background Removal")
async def enhance_image(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None),
    remove_background: bool = Form(True)
):
    """
    Enhance contrast/brightness/sharpness and perform rembg background removal.
    """
    target_path = None
    tmp_created = False
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            target_path = tmp.name
            tmp_created = True
    elif image_path and os.path.exists(image_path):
        target_path = image_path
    else:
        from ai.config import TEMP_DIR
        import numpy as np, cv2
        demo_img = np.ones((600, 800, 3), dtype=np.uint8) * 200
        cv2.circle(demo_img, (400, 300), 150, (100, 150, 50), -1)
        demo_path = os.path.join(TEMP_DIR, "demo_enhance_input.jpg")
        cv2.imwrite(demo_path, demo_img)
        target_path = demo_path

    return kai_ai_service.enhance_image(target_path, remove_bg=remove_background)

@router.post("/api/ai/assess-pricing", response_model=PricingAssistanceResponse, summary="Pricing Complexity Assistance")
async def assess_pricing(request: PricingAssistanceRequest):
    """
    Classify craft complexity rating (1-5) and effort category for backend pricing calculations.
    """
    return kai_ai_service.assess_pricing(request)

@router.post("/api/ai/recommend-tutorials", response_model=TutorialRecommendationResponse, summary="Recommend Craft Tutorials")
async def recommend_tutorials(request: TutorialRecommendationRequest):
    """
    Retrieve matching artisan tutorial metadata based on material, craft, and language.
    """
    return kai_ai_service.recommend_tutorials(request)
