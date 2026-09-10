import logging
from ai.llm_client import default_llm_client
from ai.prompts.story import STORY_GEN_SYSTEM_PROMPT, STORY_GEN_USER_TEMPLATE
from ai.schemas.generation import StoryGenerationRequest, StoryGenerationResponse

logger = logging.getLogger("kai.story_generator")

class StoryGenerator:
    """
    Transforms artisan reflections into authentic brand stories preserving genuine user facts.
    """

    def generate(self, req: StoryGenerationRequest) -> StoryGenerationResponse:
        user_prompt = STORY_GEN_USER_TEMPLATE.format(
            transcript=req.transcript,
            language=req.language or "en"
        )

        def fallback_story():
            return StoryGenerationResponse(
                story=f"Crafted with dedication and traditional skill: '{req.transcript}'. Every piece carries the artisan's personal journey, hand-worked detail, and authentic mastery.",
                keyElements=["Artisan handcrafting", "Traditional skill", "Personal dedication"]
            )

        try:
            return default_llm_client.generate_structured(
                system_prompt=STORY_GEN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=StoryGenerationResponse,
                fallback_factory=fallback_story
            )
        except Exception as e:
            logger.warning(f"Story generation failed: {e}. Returning fallback story.")
            return fallback_story()

story_generator = StoryGenerator()
