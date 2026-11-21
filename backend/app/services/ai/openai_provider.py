from typing import Tuple, Dict, Any
from .base import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self, name: str = "OpenAI", api_key: str = "", api_endpoint: str = "", model: str = "gpt-4o"):
        endpoint = api_endpoint.strip() if api_endpoint else "https://api.openai.com/v1"
        super().__init__(name, api_key, endpoint, model or "gpt-4o")

    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key and "localhost" not in self.api_endpoint and "127.0.0.1" not in self.api_endpoint:
            return False, "API key is required"
        try:
            url = f"{self.api_endpoint.rstrip('/')}/models"
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._http_request(url, method="GET", headers=headers, timeout=15)
            return True, f"Successfully connected to {self.name} API"
        except Exception as e:
            return False, str(e)

    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        url = f"{self.api_endpoint.rstrip('/')}/chat/completions"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048
        }

        res = self._http_request(url, method="POST", headers=headers, data=payload, timeout=60)
        try:
            choices = res.get("choices", [])
            if not choices:
                raise ValueError(f"No choices returned by {self.name}.")
            return choices[0]["message"]["content"].strip()
        except KeyError:
            raise RuntimeError(f"Unexpected response structure from {self.name}: {res}")
