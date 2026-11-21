import urllib.request
import urllib.parse
import urllib.error
import json
import mimetypes
import uuid
import logging
from typing import Dict, Any, Tuple, Optional, List
from ...config import FB_GRAPH_BASE_URL
from ...database import get_db

logger = logging.getLogger(__name__)

def mask_token(token: Optional[str]) -> str:
    if not token:
        return ""
    if len(token) <= 10:
        return "••••••••••"
    return f"{token[:6]}••••••••••{token[-4:]}"

class FacebookGraphClient:
    def __init__(self, page_id: str = "", page_access_token: str = ""):
        self.page_id = page_id.strip()
        self.page_access_token = page_access_token.strip()

    @classmethod
    def from_database(cls) -> "FacebookGraphClient":
        with get_db() as conn:
            row = conn.execute("SELECT page_id, page_access_token FROM facebook_config WHERE id = 1").fetchone()
            if row:
                return cls(page_id=row.get("page_id") or "", page_access_token=row.get("page_access_token") or "")
        return cls()

    def _graph_get(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        qs = urllib.parse.urlencode(params)
        url = f"{FB_GRAPH_BASE_URL}/{endpoint.lstrip('/')}?{qs}"
        req = urllib.request.Request(url, headers={"User-Agent": "Universal-AI-Publisher/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            logger.error(f"Meta Graph API error ({e.code}) GET {endpoint}: {raw}")
            try:
                err_dict = json.loads(raw).get("error", {})
                msg = err_dict.get("message", raw)
                err_code = err_dict.get("code", e.code)
                subcode = err_dict.get("error_subcode", "")
                raise RuntimeError(f"Meta API Error ({err_code}/{subcode}): {msg}")
            except (json.JSONDecodeError, KeyError):
                raise RuntimeError(f"Meta Graph API HTTP {e.code}: {raw}")

    def _graph_post_form(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{FB_GRAPH_BASE_URL}/{endpoint.lstrip('/')}"
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Universal-AI-Publisher/1.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            logger.error(f"Meta Graph API error ({e.code}) POST {endpoint}: {raw}")
            try:
                err_dict = json.loads(raw).get("error", {})
                msg = err_dict.get("message", raw)
                err_code = err_dict.get("code", e.code)
                raise RuntimeError(f"Meta API Error ({err_code}): {msg}")
            except (json.JSONDecodeError, KeyError):
                raise RuntimeError(f"Meta Graph API HTTP {e.code}: {raw}")

    def _graph_post_multipart(self, endpoint: str, fields: Dict[str, str], filepath: str) -> Dict[str, Any]:
        """Uploads local image binary directly to Meta Graph API using multipart/form-data."""
        url = f"{FB_GRAPH_BASE_URL}/{endpoint.lstrip('/')}"
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
        c_type, _ = mimetypes.guess_type(filepath)
        c_type = c_type or "image/jpeg"
        filename = filepath.split("/")[-1]

        body = bytearray()
        # Add text fields
        for name, value in fields.items():
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            body.extend(f"{value}\r\n".encode("utf-8"))

        # Add image file
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="source"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(f"Content-Type: {c_type}\r\n\r\n".encode("utf-8"))
        with open(filepath, "rb") as f:
            body.extend(f.read())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        req = urllib.request.Request(
            url,
            data=bytes(body),
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "Universal-AI-Publisher/1.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            logger.error(f"Meta Graph API multipart error ({e.code}): {raw}")
            try:
                err_dict = json.loads(raw).get("error", {})
                msg = err_dict.get("message", raw)
                raise RuntimeError(f"Meta API Error ({err_dict.get('code', e.code)}): {msg}")
            except (json.JSONDecodeError, KeyError):
                raise RuntimeError(f"Meta Graph API HTTP {e.code}: {raw}")

    def verify_page_access(self) -> Tuple[bool, Dict[str, Any]]:
        """Verifies if the current page token and ID are valid and have publishing rights."""
        if not self.page_id or not self.page_access_token:
            return False, {"error": "Facebook Page ID and Page Access Token are required"}
        try:
            res = self._graph_get(
                self.page_id,
                {"fields": "id,name,verification_status,category", "access_token": self.page_access_token}
            )
            return True, res
        except Exception as e:
            return False, {"error": str(e)}

    def fetch_managed_pages(self, user_access_token: str) -> List[Dict[str, Any]]:
        """Given a User Access Token from OAuth or Graph Explorer, fetches the user's Facebook Pages with Page Access Tokens."""
        if not user_access_token:
            raise ValueError("User access token is required to fetch managed pages.")
        res = self._graph_get(
            "me/accounts",
            {"fields": "id,name,access_token,category,tasks", "access_token": user_access_token}
        )
        return res.get("data", [])

    def publish_post(self, caption: str, image_local_path: Optional[str] = None, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes post to the Facebook Page.
        Uses /photos endpoint for photo posts or /feed for text posts.
        """
        if not self.page_id or not self.page_access_token:
            raise RuntimeError("Facebook Page is not connected. Configure credentials in Facebook Settings.")

        # If local image file exists and is accessible, upload binary directly
        if image_local_path:
            import os
            if os.path.isfile(image_local_path):
                logger.info(f"Uploading local photo binary to Facebook Page {self.page_id}")
                return self._graph_post_multipart(
                    f"{self.page_id}/photos",
                    {"caption": caption, "access_token": self.page_access_token},
                    image_local_path
                )

        # If remote image URL provided, tell Meta to fetch the URL
        if image_url and (image_url.startswith("http://") or image_url.startswith("https://")):
            logger.info(f"Publishing photo via remote URL to Facebook Page {self.page_id}")
            return self._graph_post_form(
                f"{self.page_id}/photos",
                {"caption": caption, "url": image_url, "access_token": self.page_access_token}
            )

        # Text-only post fallback
        logger.info(f"Publishing text post to Facebook Page {self.page_id}/feed")
        return self._graph_post_form(
            f"{self.page_id}/feed",
            {"message": caption, "access_token": self.page_access_token}
        )
