"""AI Assistant Module for grounded natural-language merchant analytics and Q&A."""

from app.modules.ai_assistant.routes import router as ai_assistant_router
from app.modules.ai_assistant.service import AIAssistantService

__all__ = ["ai_assistant_router", "AIAssistantService"]
