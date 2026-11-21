from typing import Tuple, Dict, Any
from .base import BaseAIProvider

class AnthropicClaudeProvider(BaseAIProvider):
    def __init__(self, name: str = "Anthropic Claude", api_key: str = "", api_endpoint: str = "", model: str = "claude-3-5-sonnet-20241022"):
        endpoint = api_endpoint.strip() if api_endpoint else "https://api.anthropic.com/v1"
        super().__init__(name, api_key, endpoint, model or "claude-3-5-sonnet-20241022")

    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Anthropic API key is required"
        try:
            # Send a tiny 1-token query to verify credentials
            self.generate_text("Hi", system_prompt="Reply with 'OK'", temperature=0.0)
            return True, f"Successfully connected to Anthropic Claude ({self.model})"
        except Exception as e:
            return False, str(e)

    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key is missing.")

        url = f"{self.api_endpoint.rstrip('/')}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": 2048,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        if system_prompt:
            payload["system"] = system_prompt

        res = self._http_request(url, method="POST", headers=headers, data=payload, timeout=60)
        try:
            content = res.get("content", [])
            if not content:
                raise ValueError("Empty content returned from Anthropic.")
            text = "".join([c.get("text", "") for c in content if c.get("type") == "text"])
            return text.strip()
        except KeyError:
            raise RuntimeError(f"Unexpected response structure from Anthropic: {res}")
