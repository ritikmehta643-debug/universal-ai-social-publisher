import json
import base64
import urllib.request
import urllib.error
from typing import Tuple
from .base import BaseImageProvider

class GeminiImagenProvider(BaseImageProvider):
    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Gemini API key is required for Imagen 3"
        return True, "Gemini Imagen 3 configured"

    def generate_image(self, prompt: str) -> Tuple[str, str]:
        if not self.api_key:
            raise ValueError("Gemini API key is missing for Imagen.")

        model_name = self.model or "imagen-3.0-generate-002"
        endpoint = self.api_endpoint.rstrip("/") if self.api_endpoint else "https://generativelanguage.googleapis.com"
        url = f"{endpoint}/v1beta/models/{model_name}:predict?key={self.api_key}"
        enhanced = self.enhance_prompt(prompt)

        ar = "1:1"
        if self.aspect_ratio in ("1:1", "3:4", "4:3", "9:16", "16:9"):
            ar = self.aspect_ratio

        payload = {
            "instances": [
                {"prompt": enhanced}
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": ar,
                "personGeneration": "ALLOW_ADULT",
                "safetySetting": "BLOCK_MEDIUM_AND_ABOVE"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                predictions = data.get("predictions", [])
                if not predictions:
                    raise ValueError("No image predictions returned by Imagen.")
                b64_str = predictions[0].get("bytesBase64Encoded")
                if not b64_str:
                    raise ValueError("Empty image data in Imagen response.")
                image_bytes = base64.b64decode(b64_str)
                local_path = self.save_bytes_to_file(image_bytes, extension="jpg")
                return f"data:image/jpeg;base64,{b64_str[:50]}...", local_path
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Imagen 3 error ({e.code}): {err}")
