import logging
from typing import Dict, Any
from ai.config import HIGH_CONFIDENCE_THRESHOLD, DESTRUCTIVE_INTENTS, CONFIRMATION_REQUIRED_INTENTS
from ai.schemas.intent import IntentResponse

logger = logging.getLogger("kai.action_mapper")

class ActionMapper:
    """
    Builds the clean action contract for the FastAPI backend.
    Evaluates safety rules and determines if requires_confirmation is True or False.
    """
    
    def build_action_contract(
        self,
        intent: str,
        confidence: float,
        parameters: Dict[str, Any]
    ) -> IntentResponse:
        
        requires_confirmation = False

        # 1. Low confidence rule
        if confidence < HIGH_CONFIDENCE_THRESHOLD:
            requires_confirmation = True

        # 2. Destructive or sensitive action rule
        if intent in DESTRUCTIVE_INTENTS or intent in CONFIRMATION_REQUIRED_INTENTS:
            requires_confirmation = True

        # 3. Missing critical parameters rule
        if intent == "ADD_RAW_MATERIAL" and not parameters.get("name"):
            requires_confirmation = True

        return IntentResponse(
            intent=intent,
            confidence=round(confidence, 2),
            parameters=parameters,
            requires_confirmation=requires_confirmation
        )

action_mapper = ActionMapper()
