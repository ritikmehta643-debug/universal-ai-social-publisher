from typing import Tuple, Dict, Any
from .openai_provider import OpenAIProvider

class OpenRouterProvider(OpenAIProvider):
    def __init__(self, name: str = "OpenRouter", api_key: str = "", api_endpoint: str = "", model: str = "meta-llama/llama-3.3-70b-instruct"):
        endpoint = api_endpoint.strip() if api_endpoint else "https://openrouter.ai/api/v1"
        super().__init__(name, api_key, endpoint, model or "meta-llama/llama-3.3-70b-instruct")

    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "OpenRouter API key is required"
        try:
            url = f"{self.api_endpoint.rstrip('/')}/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://universal-ai-publisher.local",
                "X-Title": "Universal AI Social Publisher"
            }
            self._http_request(url, method="GET", headers=headers, timeout=15)
            return True, f"Successfully connected to OpenRouter ({self.model})"
        except Exception as e:
            return False, str(e)

    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        url = f"{self.api_endpoint.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://universal-ai-publisher.local",
            "X-Title": "Universal AI Social Publisher"
        }

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
            return res["choices"][0]["message"]["content"].strip()
        except KeyError:
            raise RuntimeError(f"Unexpected response from OpenRouter: {res}")
