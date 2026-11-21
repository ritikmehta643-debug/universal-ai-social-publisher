from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
import urllib.request
import urllib.error
import json
import logging
from pathlib import Path
import uuid
from ...config import MEDIA_DIR

logger = logging.getLogger(__name__)

class BaseImageProvider(ABC):
    def __init__(self, name: str, api_key: str, api_endpoint: str = "", model: str = "", aspect_ratio: str = "1:1", resolution: str = "1024x1024", style: str = "photorealistic documentary", negative_prompt: str = ""):
        self.name = name
        self.api_key = api_key or ""
        self.api_endpoint = api_endpoint or ""
        self.model = model or ""
        self.aspect_ratio = aspect_ratio or "1:1"
        self.resolution = resolution or "1024x1024"
        self.style = style or "photorealistic documentary"
        self.negative_prompt = negative_prompt or ""

    @abstractmethod
    def generate_image(self, prompt: str) -> Tuple[str, str]:
        """Generates image. Returns (image_url_or_b64, local_file_path)."""
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Tests image provider readiness."""
        pass

    def enhance_prompt(self, user_prompt: str) -> str:
        """Enriches the user prompt with documentary realism, lighting, and camera detail."""
        style_clause = f"{self.style}, historical realism, ultra-detailed 8k photography, dramatic documentary lighting, shot on 35mm lens, authentic colors and atmosphere"
        neg_clause = f" Avoid: {self.negative_prompt}" if self.negative_prompt else ""
        return f"{user_prompt.strip()}. {style_clause}.{neg_clause}"

    def save_bytes_to_file(self, image_bytes: bytes, extension: str = "jpg") -> str:
        """Saves image bytes to MEDIA_DIR and returns local path."""
        file_name = f"img_{uuid.uuid4().hex[:12]}.{extension}"
        file_path = MEDIA_DIR / file_name
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        return str(file_path)

    def download_url_to_file(self, url: str) -> str:
        """Downloads image URL and saves locally."""
        req = urllib.request.Request(url, headers={"User-Agent": "Universal-AI-Publisher/1.0"})
        with urllib.request.urlopen(req, timeout=40) as response:
            content_type = response.headers.get("Content-Type", "")
            ext = "png" if "png" in content_type else "jpg"
            data = response.read()
            return self.save_bytes_to_file(data, extension=ext)
