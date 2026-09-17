import re
import logging
from ai.llm_client import default_llm_client
from ai.prompts.story import STORY_GEN_SYSTEM_PROMPT, STORY_GEN_USER_TEMPLATE
from ai.schemas.generation import StoryGenerationRequest, StoryGenerationResponse
from ai.translation.translator import translator_service

logger = logging.getLogger("kai.story_generator")

def _contains_indic_script(text: str) -> bool:
    return any(ord(char) > 127 for char in text)

def _strip_indic_script(text: str) -> str:
    """Removes residual Tamil/Hindi script characters leaving clean English text."""
    if not text:
        return ""
    cleaned = re.sub(r'[\u0B80-\u0BFF\u0900-\u097F]', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

class StoryGenerator:
    """
    Transforms artisan reflections into authentic brand stories in English preserving genuine user facts.
    """

    def generate(self, req: StoryGenerationRequest) -> StoryGenerationResponse:
        original_transcript = req.transcript or "Authentic artisan craftsmanship"
        transcript_text = original_transcript
        
        if _contains_indic_script(transcript_text):
            try:
                tr_res = translator_service.translate(transcript_text, source_lang="ta", target_lang="en")
                translated = tr_res.get("translatedText", "")
                if translated and not _contains_indic_script(translated):
                    transcript_text = translated
                else:
                    transcript_text = _strip_indic_script(translated or transcript_text)
            except Exception as err:
                logger.warning(f"Story translation error: {err}")
                transcript_text = _strip_indic_script(transcript_text)

        user_prompt = STORY_GEN_USER_TEMPLATE.format(
            transcript=transcript_text or "Authentic artisan craftsmanship",
            language="en"
        )

        def fallback_story():
            clean_t = _strip_indic_script(transcript_text)
            story_body = "Crafted with dedication and traditional skill."
            if clean_t and len(clean_t) > 5:
                story_body = f"Crafted with dedication and traditional skill: '{clean_t}'."
            
            full_story = f"{story_body} Every piece carries hand-worked detail and authentic skill directly from the artisan."

            return StoryGenerationResponse(
                story=full_story,
                keyElements=["Artisan handcrafting", "Handmade detail", "Personal dedication"]
            )

        try:
            res = default_llm_client.generate_structured(
                system_prompt=STORY_GEN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=StoryGenerationResponse,
                fallback_factory=fallback_story
            )
            res.story = _strip_indic_script(res.story) or fallback_story().story
            return res
        except Exception as e:
            logger.warning(f"Story generation failed: {e}. Returning fallback story.")
            return fallback_story()


story_generator = StoryGenerator()
