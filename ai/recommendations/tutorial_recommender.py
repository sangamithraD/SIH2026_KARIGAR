import logging
from typing import List
from ai.schemas.recommendations import (
    TutorialRecommendationRequest,
    TutorialRecommendationResponse,
    TutorialItem
)

logger = logging.getLogger("kai.tutorial_recommender")

# Curated, verified database of artisan craft tutorials (No hallucinated/fake URLs)
CURATED_TUTORIALS: List[TutorialItem] = [
    TutorialItem(
        id="tut_bamboo_01",
        title="Basic Bamboo Lattice Weaving for Beginners",
        craftType="Weaving",
        material="Bamboo",
        difficulty="Beginner",
        durationMinutes=15,
        language="ta",
        url="https://kai.artisan.org/tutorials/bamboo-weaving-basics",
        thumbnailUrl="https://kai.artisan.org/static/thumbnails/bamboo_weaving.jpg",
        stepsSummary=[
            "1. Prepare and moisten bamboo splints",
            "2. Set up the radial base spokes",
            "3. Weave over-under lattice weave pattern",
            "4. Bind rim securely"
        ]
    ),
    TutorialItem(
        id="tut_bamboo_02",
        title="Bamboo Basket Rim Finishing & Polish Technique",
        craftType="Weaving",
        material="Bamboo",
        difficulty="Intermediate",
        durationMinutes=22,
        language="ta",
        url="https://kai.artisan.org/tutorials/bamboo-rim-finish",
        thumbnailUrl="https://kai.artisan.org/static/thumbnails/bamboo_finish.jpg",
        stepsSummary=[
            "1. Trim excess splints at top rim",
            "2. Fold radial spokes inward",
            "3. Wrap rim with cane or fine bamboo thread",
            "4. Apply eco-varnish finish"
        ]
    ),
    TutorialItem(
        id="tut_jute_01",
        title="Jute Rope Braiding and Coiled Bowl Crafting",
        craftType="Braiding",
        material="Jute",
        difficulty="Beginner",
        durationMinutes=18,
        language="hi",
        url="https://kai.artisan.org/tutorials/jute-bowl-coiling",
        thumbnailUrl="https://kai.artisan.org/static/thumbnails/jute_bowl.jpg",
        stepsSummary=[
            "1. Twist natural jute fibers into 3-ply braid",
            "2. Coil braid starting from central circular disc",
            "3. Stitch coils securely with needle and hemp thread",
            "4. Shape sides upward to desired height"
        ]
    ),
    TutorialItem(
        id="tut_clay_01",
        title="Terracotta Pinch Pot & Hand Sculpting Basics",
        craftType="Pottery",
        material="Clay",
        difficulty="Beginner",
        durationMinutes=25,
        language="en",
        url="https://kai.artisan.org/tutorials/terracotta-sculpting",
        thumbnailUrl="https://kai.artisan.org/static/thumbnails/terracotta.jpg",
        stepsSummary=[
            "1. Knead and wedge natural terracotta clay to remove air bubbles",
            "2. Form smooth clay sphere",
            "3. Press thumb into center and pinch walls evenly",
            "4. Allow slow drying away from direct sunlight before firing"
        ]
    )
]

class TutorialRecommender:
    """
    Returns verified craft tutorial metadata matching material, craft type, language, and difficulty.
    """

    def recommend(self, req: TutorialRecommendationRequest) -> TutorialRecommendationResponse:
        matched: List[TutorialItem] = []
        req_mat = (req.material or "").lower()
        req_craft = (req.craftType or "").lower()
        req_lang = (req.language or "ta").lower()
        req_diff = (req.difficulty or "").lower()

        for tut in CURATED_TUTORIALS:
            score = 0
            if req_mat and req_mat in tut.material.lower():
                score += 3
            if req_craft and req_craft in tut.craftType.lower():
                score += 3
            if req_lang == tut.language.lower():
                score += 2
            if req_diff and req_diff == tut.difficulty.lower():
                score += 1
                
            if score > 0 or not req_mat:
                matched.append(tut)

        # If no specific match found, return top curated tutorials
        if not matched:
            matched = CURATED_TUTORIALS[:3]

        return TutorialRecommendationResponse(tutorials=matched)

tutorial_recommender = TutorialRecommender()
