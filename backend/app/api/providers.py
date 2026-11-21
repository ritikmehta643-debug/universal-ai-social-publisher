from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from datetime import datetime
from ..database import get_db
from ..services.ai.base import mask_api_key
from ..services.ai.factory import create_provider_instance
from ..services.image.factory import create_image_provider_instance

router = APIRouter(prefix="/api/providers", tags=["AI Providers"])

@router.get("/")
def list_ai_providers():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM ai_providers ORDER BY id ASC").fetchall()
    
    sanitized = []
    for r in rows:
        item = dict(r)
        item["masked_key"] = mask_api_key(item.get("api_key"))
        item["has_key"] = bool(item.get("api_key"))
        del item["api_key"]  # Never expose raw key in frontend
        sanitized.append(item)
    return sanitized

@router.post("/")
def create_custom_provider(data: Dict[str, Any] = Body(...)):
    name = data.get("name", "").strip()
    provider_type = data.get("provider_type", "custom").strip()
    api_endpoint = data.get("api_endpoint", "").strip()
    api_key = data.get("api_key", "").strip()
    model = data.get("model", "").strip()
    image_model = data.get("image_model", "").strip()

    if not name or not model:
        raise HTTPException(status_code=400, detail="Name and Model are required.")

    now = datetime.now().isoformat()
    with get_db() as conn:
        try:
            cursor = conn.execute("""
                INSERT INTO ai_providers (name, provider_type, api_endpoint, api_key, model, image_model, is_enabled, is_default, is_fallback, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, 0, 0, ?, ?)
            """, (name, provider_type, api_endpoint, api_key, model, image_model, now, now))
            new_id = cursor.lastrowid
            return {"success": True, "id": new_id, "message": f"Provider '{name}' created."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create provider: {str(e)}")

@router.put("/{provider_id}")
def update_provider(provider_id: int, data: Dict[str, Any] = Body(...)):
    now = datetime.now().isoformat()
    with get_db() as conn:
        existing = conn.execute("SELECT * FROM ai_providers WHERE id = ?", (provider_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Provider not found")

        name = data.get("name", existing["name"])
        endpoint = data.get("api_endpoint", existing["api_endpoint"])
        model = data.get("model", existing["model"])
        image_model = data.get("image_model", existing["image_model"])
        is_enabled = 1 if data.get("is_enabled", existing["is_enabled"]) else 0
        
        # Only update key if user supplied a non-masked new key
        api_key = existing["api_key"]
        if "api_key" in data and data["api_key"] and not data["api_key"].startswith("••"):
            api_key = data["api_key"].strip()

        conn.execute("""
            UPDATE ai_providers SET 
                name = ?, api_endpoint = ?, api_key = ?, model = ?, image_model = ?, is_enabled = ?, updated_at = ?
            WHERE id = ?
        """, (name, endpoint, api_key, model, image_model, is_enabled, now, provider_id))

    return {"success": True, "message": "Provider updated successfully."}

@router.post("/{provider_id}/test")
def test_provider_connection(provider_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM ai_providers WHERE id = ?", (provider_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Provider not found")

    provider = create_provider_instance(row)
    now = datetime.now().isoformat()
    try:
        success, message = provider.test_connection()
        status = "connected" if success else "failed"
        with get_db() as conn:
            conn.execute("""
                UPDATE ai_providers SET status = ?, error_message = ?, last_tested_at = ? WHERE id = ?
            """, (status, message if not success else None, now, provider_id))
        return {"success": success, "status": status, "message": message}
    except Exception as e:
        err_msg = str(e)
        with get_db() as conn:
            conn.execute("""
                UPDATE ai_providers SET status = 'failed', error_message = ?, last_tested_at = ? WHERE id = ?
            """, (err_msg, now, provider_id))
        return {"success": False, "status": "failed", "message": err_msg}

@router.post("/{provider_id}/set-default")
def set_default_provider(provider_id: int):
    with get_db() as conn:
        conn.execute("UPDATE ai_providers SET is_default = 0")
        conn.execute("UPDATE ai_providers SET is_default = 1, is_enabled = 1 WHERE id = ?", (provider_id,))
    return {"success": True, "message": "Default AI provider updated."}

@router.post("/{provider_id}/set-fallback")
def set_fallback_provider(provider_id: int):
    with get_db() as conn:
        conn.execute("UPDATE ai_providers SET is_fallback = 0")
        conn.execute("UPDATE ai_providers SET is_fallback = 1, is_enabled = 1 WHERE id = ?", (provider_id,))
    return {"success": True, "message": "Fallback AI provider updated."}

@router.delete("/{provider_id}")
def delete_provider(provider_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM ai_providers WHERE id = ?", (provider_id,))
    return {"success": True, "message": "Provider deleted."}

# Image Providers Endpoints
@router.get("/image/list")
def list_image_providers():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM image_providers ORDER BY id ASC").fetchall()
    sanitized = []
    for r in rows:
        item = dict(r)
        item["masked_key"] = mask_api_key(item.get("api_key"))
        item["has_key"] = bool(item.get("api_key"))
        del item["api_key"]
        sanitized.append(item)
    return sanitized

@router.put("/image/{provider_id}")
def update_image_provider(provider_id: int, data: Dict[str, Any] = Body(...)):
    with get_db() as conn:
        existing = conn.execute("SELECT * FROM image_providers WHERE id = ?", (provider_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Image provider not found")

        name = data.get("name", existing["name"])
        endpoint = data.get("api_endpoint", existing["api_endpoint"])
        model = data.get("model", existing["model"])
        aspect_ratio = data.get("aspect_ratio", existing["aspect_ratio"])
        resolution = data.get("resolution", existing["resolution"])
        style = data.get("style", existing["style"])
        negative_prompt = data.get("negative_prompt", existing["negative_prompt"])
        is_enabled = 1 if data.get("is_enabled", existing["is_enabled"]) else 0

        api_key = existing["api_key"]
        if "api_key" in data and data["api_key"] and not data["api_key"].startswith("••"):
            api_key = data["api_key"].strip()

        conn.execute("""
            UPDATE image_providers SET 
                name = ?, api_endpoint = ?, api_key = ?, model = ?, aspect_ratio = ?, 
                resolution = ?, style = ?, negative_prompt = ?, is_enabled = ?
            WHERE id = ?
        """, (name, endpoint, api_key, model, aspect_ratio, resolution, style, negative_prompt, is_enabled, provider_id))

    return {"success": True, "message": "Image provider updated."}

@router.post("/image/{provider_id}/test")
def test_image_provider(provider_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM image_providers WHERE id = ?", (provider_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image provider not found")

    provider = create_image_provider_instance(row)
    try:
        success, message = provider.test_connection()
        status = "connected" if success else "failed"
        with get_db() as conn:
            conn.execute("UPDATE image_providers SET status = ?, error_message = ? WHERE id = ?", (status, message if not success else None, provider_id))
        return {"success": success, "message": message}
    except Exception as e:
        with get_db() as conn:
            conn.execute("UPDATE image_providers SET status = 'failed', error_message = ? WHERE id = ?", (str(e), provider_id))
        return {"success": False, "message": str(e)}

@router.post("/image/{provider_id}/set-default")
def set_default_image_provider(provider_id: int):
    with get_db() as conn:
        conn.execute("UPDATE image_providers SET is_default = 0")
        conn.execute("UPDATE image_providers SET is_default = 1, is_enabled = 1 WHERE id = ?", (provider_id,))
    return {"success": True, "message": "Default image provider set."}
