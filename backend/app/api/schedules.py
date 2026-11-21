from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from ..database import get_db

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])

@router.get("/")
def get_schedules():
    with get_db() as conn:
        slots = conn.execute("""
            SELECT s.*, t.name as template_name 
            FROM schedules s
            LEFT JOIN caption_templates t ON s.caption_template_id = t.id
            ORDER BY s.slot_number ASC
        """).fetchall()

        settings = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM system_settings").fetchall()}

    return {
        "slots": slots,
        "settings": settings
    }

@router.put("/slots")
def update_schedule_slots(slots_data: List[Dict[str, Any]] = Body(...)):
    with get_db() as conn:
        for item in slots_data:
            slot_num = item.get("slot_number")
            post_time = item.get("post_time")
            cat_pref = item.get("category_preference", "Any")
            template_id = item.get("caption_template_id")
            is_enabled = 1 if item.get("is_enabled", True) else 0

            conn.execute("""
                UPDATE schedules SET 
                    post_time = ?, category_preference = ?, caption_template_id = ?, is_enabled = ?
                WHERE slot_number = ?
            """, (post_time, cat_pref, template_id, is_enabled, slot_num))

    return {"success": True, "message": "Posting schedules updated."}

@router.post("/toggle-automation")
def toggle_automation(data: Dict[str, Any] = Body(...)):
    enabled = data.get("enabled", True)
    val_str = "true" if enabled else "false"
    with get_db() as conn:
        conn.execute("UPDATE system_settings SET value = ? WHERE key = 'automation_enabled'", (val_str,))
    return {"success": True, "automation_enabled": enabled}

@router.post("/settings")
def update_system_settings(data: Dict[str, Any] = Body(...)):
    with get_db() as conn:
        for k, v in data.items():
            conn.execute("UPDATE system_settings SET value = ? WHERE key = ?", (str(v), k))
    return {"success": True, "message": "System settings updated."}
