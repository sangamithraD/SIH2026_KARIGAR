import logging
from typing import List
from ai.llm_client import default_llm_client
from ai.prompts.ideas import IDEAS_GEN_SYSTEM_PROMPT, IDEAS_GEN_USER_TEMPLATE
from ai.schemas.generation import IdeasGenerationRequest, IdeasGenerationResponse, IdeaItem

logger = logging.getLogger("kai.ideas_generator")

class IdeasGenerator:
    """
    Generates 3 to 5 realistic, feasible product ideas based on available raw materials.
    """

    def generate(self, req: IdeasGenerationRequest) -> IdeasGenerationResponse:
        mat = req.rawMaterial or "Bamboo"
        qty = req.quantity if req.quantity is not None else 5
        unit = req.unit or "kg"
        skill = req.skillLevel or "Beginner"
        existing = ", ".join(req.existingMaterials) if req.existingMaterials else "None"

        user_prompt = IDEAS_GEN_USER_TEMPLATE.format(
            rawMaterial=mat,
            quantity=qty,
            unit=unit,
            skillLevel=skill,
            existingMaterials=existing
        )

        def fallback_ideas():
            mat_title = mat.title()
            items = [
                IdeaItem(
                    title=f"Woven {mat_title} Storage Basket",
                    description=f"A durable utility basket handwoven from {mat_title.lower()}. Great for home organization.",
                    difficulty="Easy",
                    materials=[f"{mat_title} strips", "Varnish"],
                    estimatedHours=3.5,
                    estimatedPrice=450.0,
                    reason=f"Perfect for using ~1.5 {unit} of {mat_title.lower()} with basic weaving skill."
                ),
                IdeaItem(
                    title=f"Handcrafted {mat_title} Table Mat Set",
                    description=f"Set of 4 heat-resistant dining table mats woven with fine {mat_title.lower()} splints.",
                    difficulty="Beginner",
                    materials=[f"{mat_title} splints", "Cotton thread"],
                    estimatedHours=2.5,
                    estimatedPrice=350.0,
                    reason=f"Utilizes ~1 {unit} of {mat_title.lower()} and offers high market demand."
                ),
                IdeaItem(
                    title=f"Decorative {mat_title} Wall Hanging",
                    description=f"Artisanal wall decor featuring geometric woven lattice patterns from {mat_title.lower()}.",
                    difficulty="Medium",
                    materials=[f"{mat_title} frame", "Hanging cord"],
                    estimatedHours=4.0,
                    estimatedPrice=600.0,
                    reason=f"Requires ~2 {unit} of {mat_title.lower()} and adds high artistic value."
                ),
                IdeaItem(
                    title=f"{mat_title} Pen Stand & Desk Organizer",
                    description=f"Compact cylindrical desk organizer handcrafted from natural {mat_title.lower()}.",
                    difficulty="Easy",
                    materials=[f"{mat_title} section", "Sandpaper", "Eco-polish"],
                    estimatedHours=1.5,
                    estimatedPrice=250.0,
                    reason=f"Small material footprint (~0.5 {unit}) suitable for quick crafting."
                )
            ]
            return IdeasGenerationResponse(ideas=items)

        try:
            return default_llm_client.generate_structured(
                system_prompt=IDEAS_GEN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=IdeasGenerationResponse,
                fallback_factory=fallback_ideas
            )
        except Exception as e:
            logger.warning(f"Ideas generation failed: {e}. Returning fallback ideas.")
            return fallback_ideas()

ideas_generator = IdeasGenerator()
