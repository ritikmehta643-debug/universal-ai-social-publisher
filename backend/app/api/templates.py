from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from datetime import datetime
from ..database import get_db

router = APIRouter(prefix="/api/templates", tags=["Caption Templates"])

@router.get("/")
def list_caption_templates():
    with get_db() as conn:
        return conn.execute("SELECT * FROM caption_templates ORDER BY is_default DESC, id ASC").fetchall()

@router.post("/")
def create_caption_template(data: Dict[str, Any] = Body(...)):
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Template name is required.")

    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO caption_templates (
                name, hook_style, caption_length, storytelling_format, language, emoji_usage,
                hashtag_quantity, cta_style, brand_voice, ending_line, is_default, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            name,
            data.get("hook_style", "shocking_fact"),
            data.get("caption_length", "documentary"),
            data.get("storytelling_format", "deep_dive"),
            data.get("language", "en"),
            data.get("emoji_usage", "moderate"),
            int(data.get("hashtag_quantity", 10)),
            data.get("cta_style", "follow_page"),
            data.get("brand_voice", "dramatic"),
            data.get("ending_line", ""),
            now
        ))
        return {"success": True, "id": cursor.lastrowid, "message": f"Template '{name}' created."}

@router.put("/{template_id}")
def update_caption_template(template_id: int, data: Dict[str, Any] = Body(...)):
    with get_db() as conn:
        conn.execute("""
            UPDATE caption_templates SET 
                name = ?, hook_style = ?, caption_length = ?, storytelling_format = ?, 
                language = ?, emoji_usage = ?, hashtag_quantity = ?, cta_style = ?, 
                brand_voice = ?, ending_line = ?
            WHERE id = ?
        """, (
            data.get("name"),
            data.get("hook_style"),
            data.get("caption_length"),
            data.get("storytelling_format"),
            data.get("language"),
            data.get("emoji_usage"),
            int(data.get("hashtag_quantity", 10)),
            data.get("cta_style"),
            data.get("brand_voice"),
            data.get("ending_line"),
            template_id
        ))
    return {"success": True, "message": "Caption template updated."}

@router.post("/{template_id}/set-default")
def set_default_template(template_id: int):
    with get_db() as conn:
        conn.execute("UPDATE caption_templates SET is_default = 0")
        conn.execute("UPDATE caption_templates SET is_default = 1 WHERE id = ?", (template_id,))
    return {"success": True, "message": "Default caption template updated."}

@router.delete("/{template_id}")
def delete_caption_template(template_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM caption_templates WHERE id = ?", (template_id,))
    return {"success": True, "message": "Template deleted."}
