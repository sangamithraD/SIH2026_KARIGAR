import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import numpy as np
import cv2

from ai.service import kai_ai_service
from ai.schemas.intent import IntentRequest, IntentResponse
from ai.schemas.generation import (
    ProductGenerationRequest,
    StoryGenerationRequest,
    IdeasGenerationRequest
)
from ai.schemas.pricing import PricingAssistanceRequest
from ai.schemas.recommendations import TutorialRecommendationRequest
from ai.config import TEMP_DIR

class TestKAIAILayer(unittest.TestCase):

    def test_01_tamil_speech_and_intent(self):
        # Artisan says in Tamil: "என்னிடம் ஐந்து கிலோ மூங்கில் இருக்கிறது"
        transcript = "என்னிடம் ஐந்து கிலோ மூங்கில் இருக்கிறது"
        res = kai_ai_service.classify_intent(transcript, language="ta")
        self.assertEqual(res.intent, "ADD_RAW_MATERIAL")
        self.assertGreaterEqual(res.confidence, 0.70)
        self.assertEqual(res.parameters.get("name"), "Bamboo")
        self.assertEqual(res.parameters.get("quantity"), 5)
        self.assertEqual(res.parameters.get("unit"), "kg")
        self.assertFalse(res.requires_confirmation)

    def test_02_hindi_speech_and_intent(self):
        # Artisan says in Hindi: "मेरे पास पाँच किलोग्राम बाँस है"
        transcript = "मेरे पास पाँच किलोग्राम बाँस है"
        res = kai_ai_service.classify_intent(transcript, language="hi")
        self.assertEqual(res.intent, "ADD_RAW_MATERIAL")
        self.assertEqual(res.parameters.get("name"), "Bamboo")
        self.assertEqual(res.parameters.get("quantity"), 5)

    def test_03_english_speech_and_intent(self):
        # Artisan says in English: "I have five kilograms of bamboo"
        transcript = "I have five kilograms of bamboo"
        res = kai_ai_service.classify_intent(transcript, language="en")
        self.assertEqual(res.intent, "ADD_RAW_MATERIAL")
        self.assertEqual(res.parameters.get("name"), "Bamboo")
        self.assertEqual(res.parameters.get("quantity"), 5)
        self.assertEqual(res.parameters.get("unit"), "kg")

    def test_04_low_confidence_and_confirmation(self):
        # Ambiguous input should trigger low confidence or confirmation
        transcript = "maybe check something later"
        res = kai_ai_service.classify_intent(transcript, language="en")
        self.assertTrue(res.requires_confirmation or res.confidence < 0.85)

    def test_05_product_generation_structure_and_truthfulness(self):
        req = ProductGenerationRequest(
            transcript="I want to make a bamboo basket",
            material="Bamboo",
            craftType="Weaving",
            language="en"
        )
        res = kai_ai_service.generate_product(req)
        self.assertIsNotNone(res.productName)
        self.assertEqual(res.material, "Bamboo")
        self.assertEqual(res.craftType, "Weaving")
        self.assertIsInstance(res.keywords, list)
        # Ensure no hallucinated awards/certifications in description
        self.assertNotIn("award winning", res.description.lower())
        self.assertNotIn("1000 year old", res.description.lower())

    def test_06_story_generation(self):
        req = StoryGenerationRequest(
            transcript="I learned this bamboo weaving from my grandmother and it takes me two days to make.",
            language="en"
        )
        res = kai_ai_service.generate_story(req)
        self.assertIn("grandmother", res.story.lower())
        self.assertIsInstance(res.keyElements, list)

    def test_07_raw_material_product_ideas(self):
        req = IdeasGenerationRequest(
            rawMaterial="Bamboo",
            quantity=5,
            unit="kg",
            skillLevel="Beginner"
        )
        res = kai_ai_service.generate_ideas(req)
        self.assertGreaterEqual(len(res.ideas), 3)
        self.assertLessEqual(len(res.ideas), 5)
        for idea in res.ideas:
            self.assertIsNotNone(idea.title)
            self.assertGreater(idea.estimatedHours, 0)
            self.assertGreater(idea.estimatedPrice, 0)

    def test_08_image_analysis_and_enhancement(self):
        # Generate dummy test image
        img = np.ones((600, 800, 3), dtype=np.uint8) * 120
        cv2.putText(img, "Test Product", (250, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        test_img_path = str(TEMP_DIR / "test_photo.jpg")
        cv2.imwrite(test_img_path, img)

        # Quality Analysis
        analysis = kai_ai_service.analyze_image(test_img_path)
        self.assertGreaterEqual(analysis.score, 0)
        self.assertLessEqual(analysis.score, 100)

        # Enhancement
        enhancement = kai_ai_service.enhance_image(test_img_path, remove_bg=False)
        self.assertEqual(enhancement.status, "success")
        self.assertTrue(os.path.exists(enhancement.enhancedImageUrl))

    def test_09_pricing_complexity_assistance(self):
        req = PricingAssistanceRequest(
            productName="Handwoven Bamboo Basket",
            material="Bamboo",
            craftType="Weaving",
            productionTimeHours=4.0
        )
        res = kai_ai_service.assess_pricing(req)
        self.assertEqual(res.complexityLevel, 2)
        self.assertEqual(res.effortCategory, "Medium")
        self.assertGreater(res.suggestedComplexityMultiplier, 1.0)

    def test_10_tutorial_recommendation(self):
        req = TutorialRecommendationRequest(
            material="Bamboo",
            craftType="Weaving",
            language="ta"
        )
        res = kai_ai_service.recommend_tutorials(req)
        self.assertGreaterEqual(len(res.tutorials), 1)
        self.assertEqual(res.tutorials[0].material, "Bamboo")

    def test_11_multilingual_intents(self):
        # 1. Tamil: "இதை வைத்து என்ன செய்யலாம்" -> GENERATE_PRODUCT_IDEAS
        res_ta = kai_ai_service.classify_intent("இதை வைத்து என்ன செய்யலாம்", language="ta")
        self.assertEqual(res_ta.intent, "GENERATE_PRODUCT_IDEAS")

        # 2. Hindi: "कच्चा माल दिखाएं" -> VIEW_RAW_MATERIALS
        res_hi = kai_ai_service.classify_intent("कच्चा माल दिखाएं", language="hi")
        self.assertEqual(res_hi.intent, "VIEW_RAW_MATERIALS")

        # 3. Tanglish: "kitta 5 kg bamboo iruku" -> ADD_RAW_MATERIAL
        res_tanglish = kai_ai_service.classify_intent("kitta 5 kg bamboo iruku", language="ta")
        self.assertEqual(res_tanglish.intent, "ADD_RAW_MATERIAL")
        self.assertEqual(res_tanglish.parameters.get("quantity"), 5)

        # 4. Hinglish: "mere paas 5 kg bamboo hai" -> ADD_RAW_MATERIAL
        res_hinglish = kai_ai_service.classify_intent("mere paas 5 kg bamboo hai", language="hi")
        self.assertEqual(res_hinglish.intent, "ADD_RAW_MATERIAL")
        self.assertEqual(res_hinglish.parameters.get("quantity"), 5)

if __name__ == "__main__":
    unittest.main()
