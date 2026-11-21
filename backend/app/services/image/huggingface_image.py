import json
import urllib.request
import urllib.error
from typing import Tuple
from .base import BaseImageProvider

class HuggingFaceImageProvider(BaseImageProvider):
    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Hugging Face token is required"
        return True, f"Hugging Face image provider configured ({self.model})"

    def generate_image(self, prompt: str) -> Tuple[str, str]:
        if not self.api_key:
            raise ValueError("Hugging Face API token missing.")

        model_name = self.model or "black-forest-labs/FLUX.1-schnell"
        endpoint = self.api_endpoint.rstrip("/") if self.api_endpoint else "https://api-inference.huggingface.co/models"
        url = f"{endpoint}/{model_name}"
        enhanced = self.enhance_prompt(prompt)

        payload = {"inputs": enhanced}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=80) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    # Model loading or error message
                    res_json = json.loads(resp.read().decode("utf-8"))
                    raise RuntimeError(f"Hugging Face response: {res_json}")
                img_bytes = resp.read()
                local_path = self.save_bytes_to_file(img_bytes, extension="jpg")
                return f"huggingface://{model_name}", local_path
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Hugging Face image error ({e.code}): {err}")
