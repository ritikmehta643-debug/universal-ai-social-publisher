from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional
from datetime import datetime
from ..database import get_db
from ..config import CATEGORIES

router = APIRouter(prefix="/api/topics", tags=["Topics"])

@router.get("/categories")
def get_categories():
    return CATEGORIES

@router.get("/")
def list_topics(category: Optional[str] = Query(None)):
    with get_db() as conn:
        if category and category != "All":
            return conn.execute("SELECT * FROM topics WHERE category = ? ORDER BY times_used ASC, id DESC", (category,)).fetchall()
        return conn.execute("SELECT * FROM topics ORDER BY times_used ASC, id DESC").fetchall()

@router.post("/")
def create_topic(data: Dict[str, Any] = Body(...)):
    category = data.get("category", "Custom Topics").strip()
    title = data.get("title", "").strip()
    prompt_seed = data.get("prompt_seed", "").strip()

    if not title:
        raise HTTPException(status_code=400, detail="Topic title is required.")

    now = datetime.now().isoformat()
    with get_db() as conn:
        try:
            cursor = conn.execute("""
                INSERT INTO topics (category, title, prompt_seed, times_used, is_active, created_at)
                VALUES (?, ?, ?, 0, 1, ?)
            """, (category, title, prompt_seed, now))
            return {"success": True, "id": cursor.lastrowid, "message": "Topic added to library."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Topic could not be added: {str(e)}")

@router.put("/{topic_id}")
def update_topic(topic_id: int, data: Dict[str, Any] = Body(...)):
    with get_db() as conn:
        conn.execute("""
            UPDATE topics SET category = ?, title = ?, prompt_seed = ?, is_active = ?
            WHERE id = ?
        """, (
            data.get("category"),
            data.get("title"),
            data.get("prompt_seed"),
            1 if data.get("is_active", True) else 0,
            topic_id
        ))
    return {"success": True, "message": "Topic updated."}

@router.delete("/{topic_id}")
def delete_topic(topic_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    return {"success": True, "message": "Topic deleted."}
