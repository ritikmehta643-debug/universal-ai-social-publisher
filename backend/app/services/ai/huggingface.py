from typing import Tuple, Dict, Any, List
from .base import BaseAIProvider

class HuggingFaceProvider(BaseAIProvider):
    def __init__(self, name: str = "Hugging Face", api_key: str = "", api_endpoint: str = "", model: str = "meta-llama/Llama-3.2-3B-Instruct"):
        endpoint = api_endpoint.strip() if api_endpoint else "https://api-inference.huggingface.co/models"
        super().__init__(name, api_key, endpoint, model or "meta-llama/Llama-3.2-3B-Instruct")

    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Hugging Face User Access Token is required"
        try:
            url = f"{self.api_endpoint.rstrip('/')}/{self.model}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            # Test payload
            payload = {"inputs": "Test connection. Respond with OK.", "parameters": {"max_new_tokens": 5}}
            self._http_request(url, method="POST", headers=headers, data=payload, timeout=20)
            return True, f"Successfully connected to Hugging Face model ({self.model})"
        except Exception as e:
            return False, str(e)

    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        if not self.api_key:
            raise ValueError("Hugging Face API token is required.")

        url = f"{self.api_endpoint.rstrip('/')}/{self.model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        formatted_prompt = prompt
        if system_prompt:
            formatted_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": max(0.1, temperature),
                "return_full_text": False
            }
        }

        res = self._http_request(url, method="POST", headers=headers, data=payload, timeout=60)
        if isinstance(res, list) and len(res) > 0 and "generated_text" in res[0]:
            return res[0]["generated_text"].strip()
        elif isinstance(res, dict) and "error" in res:
            raise RuntimeError(f"Hugging Face error: {res['error']}")
        return str(res)
