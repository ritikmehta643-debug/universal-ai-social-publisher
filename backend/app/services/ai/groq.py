from typing import Tuple, Dict, Any
from .openai_provider import OpenAIProvider

class GroqProvider(OpenAIProvider):
    def __init__(self, name: str = "Groq", api_key: str = "", api_endpoint: str = "", model: str = "llama-3.3-70b-versatile"):
        endpoint = api_endpoint.strip() if api_endpoint else "https://api.groq.com/openai/v1"
        super().__init__(name, api_key, endpoint, model or "llama-3.3-70b-versatile")

    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Groq API key is required"
        try:
            url = f"{self.api_endpoint.rstrip('/')}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            self._http_request(url, method="GET", headers=headers, timeout=15)
            return True, f"Successfully connected to Groq Cloud ({self.model})"
        except Exception as e:
            return False, str(e)
