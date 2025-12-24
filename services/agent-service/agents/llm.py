import os
from typing import List, Dict, Any
from shared.shared.logging import configure_logging

logger = configure_logging("llm")

class LLMProvider:
    async def complete(self, system: str, messages: List[Dict[str, str]], **kwargs) -> str:
        raise NotImplementedError

class MockLLM(LLMProvider):
    async def complete(self, system: str, messages: List[Dict[str, str]], **kwargs) -> str:
        user = messages[-1]["content"] if messages else ""
        return (
            "MOCK_RESPONSE: I can help with UPS logistics questions. "
            f"You said: {user}. "
            "If you connect Vertex AI, I will generate real responses."
        )

class VertexGeminiLLM(LLMProvider):
    """Minimal Vertex AI Gemini wrapper.
    Uses google-cloud-aiplatform's vertexai.generative_models API.
    """
    def __init__(self):
        from vertexai import init
        from vertexai.generative_models import GenerativeModel

        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        model_name = os.getenv("VERTEX_MODEL", "gemini-1.5-pro")

        if not project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT must be set for VertexGeminiLLM")

        init(project=project, location=location)
        self.model = GenerativeModel(model_name)

    async def complete(self, system: str, messages: List[Dict[str, str]], **kwargs) -> str:
        # simple: concatenate. For production, use structured messages + tool calling.
        prompt = system + "\n\n"
        for m in messages:
            prompt += f"{m['role'].upper()}: {m['content']}\n"
        resp = self.model.generate_content(prompt)
        return getattr(resp, "text", str(resp))

def get_llm() -> LLMProvider:
    try:
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            return VertexGeminiLLM()
    except Exception as e:
        logger.warning("Falling back to MockLLM. Vertex init failed: %s", e)
    return MockLLM()
