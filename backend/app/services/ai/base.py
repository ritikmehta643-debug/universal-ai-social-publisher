from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import urllib.request
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)

def mask_api_key(key: Optional[str]) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "••••••••"
    return f"{key[:4]}••••••••{key[-4:]}"

class BaseAIProvider(ABC):
    def __init__(self, name: str, api_key: str, api_endpoint: str = "", model: str = ""):
        self.name = name
        self.api_key = api_key or ""
        self.api_endpoint = api_endpoint or ""
        self.model = model or ""

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Tests API key and endpoint validity. Returns (is_success, message)."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generates text from the provider."""
        pass

    def _http_request(self, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, data: Optional[Dict[str, Any]] = None, timeout: int = 40) -> Dict[str, Any]:
        """Universal HTTP request helper using standard library urllib."""
        req_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Universal-AI-Publisher/1.0"
        }
        if headers:
            req_headers.update(headers)

        payload = None
        if data is not None:
            payload = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            logger.error(f"HTTPError {e.code} for {self.name} at {url}: {err_body}")
            try:
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message") or err_json.get("message") or err_body
            except Exception:
                err_msg = err_body
            raise RuntimeError(f"[{self.name} Error {e.code}]: {err_msg}")
        except urllib.error.URLError as e:
            logger.error(f"URLError for {self.name}: {e.reason}")
            raise RuntimeError(f"Connection failed to {self.name}: {e.reason}")
