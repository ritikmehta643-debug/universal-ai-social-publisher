from typing import Tuple, Dict, Any
from .openai_provider import OpenAIProvider

class CustomAIProvider(OpenAIProvider):
    """Custom OpenAI-compatible provider adapter (e.g. Ollama, vLLM, LocalAI, LM Studio)."""
    def __init__(self, name: str = "Custom Provider", api_key: str = "", api_endpoint: str = "", model: str = ""):
        endpoint = api_endpoint.strip() if api_endpoint else "http://localhost:11434/v1"
        super().__init__(name, api_key, endpoint, model or "default")

    def test_connection(self) -> Tuple[bool, str]:
        try:
            url = f"{self.api_endpoint.rstrip('/')}/models"
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._http_request(url, method="GET", headers=headers, timeout=10)
            return True, f"Successfully connected to Custom endpoint ({self.api_endpoint})"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
