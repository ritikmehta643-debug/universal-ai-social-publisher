import json
import urllib.request
import urllib.error
from typing import Tuple
from .base import BaseImageProvider

class DalleImageProvider(BaseImageProvider):
    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "OpenAI API key required for DALL-E"
        return True, "OpenAI DALL-E configured"

    def generate_image(self, prompt: str) -> Tuple[str, str]:
        if not self.api_key:
            raise ValueError("OpenAI API key missing for DALL-E.")

        endpoint = self.api_endpoint.rstrip("/") if self.api_endpoint else "https://api.openai.com/v1"
        url = f"{endpoint}/images/generations"
        enhanced = self.enhance_prompt(prompt)

        payload = {
            "model": self.model or "dall-e-3",
            "prompt": enhanced[:1000],
            "n": 1,
            "size": self.resolution if self.resolution in ("1024x1024", "1024x1792", "1792x1024") else "1024x1024",
            "quality": "standard"
        }

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
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                remote_url = data["data"][0]["url"]
                local_path = self.download_url_to_file(remote_url)
                return remote_url, local_path
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DALL-E generation failed ({e.code}): {err}")
