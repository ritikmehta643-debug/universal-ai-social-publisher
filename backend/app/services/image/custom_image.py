import json
import urllib.request
import urllib.error
from typing import Tuple
from .base import BaseImageProvider

class CustomImageProvider(BaseImageProvider):
    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_endpoint:
            return False, "Custom image API endpoint URL is required"
        return True, f"Custom Image endpoint configured ({self.api_endpoint})"

    def generate_image(self, prompt: str) -> Tuple[str, str]:
        if not self.api_endpoint:
            raise ValueError("Custom image API endpoint is not set.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "prompt": self.enhance_prompt(prompt),
            "model": self.model,
            "size": self.resolution
        }

        req = urllib.request.Request(
            self.api_endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = json.loads(resp.read().decode("utf-8"))
                    url = data.get("url") or (data.get("data", [{}])[0].get("url") if "data" in data else None)
                    if url:
                        local_path = self.download_url_to_file(url)
                        return url, local_path
                    raise ValueError(f"No image URL in custom response: {data}")
                else:
                    data = resp.read()
                    local_path = self.save_bytes_to_file(data, extension="jpg")
                    return self.api_endpoint, local_path
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Custom image error ({e.code}): {err}")
