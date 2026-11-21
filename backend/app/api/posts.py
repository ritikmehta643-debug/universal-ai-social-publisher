from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from ..database import get_db
from ..services.content_engine import ContentEngine
from ..services.facebook.client import FacebookGraphClient

router = APIRouter(prefix="/api/posts", tags=["Posts"])
content_engine = ContentEngine()

@router.get("/")
def list_posts(status: Optional[str] = Query(None), limit: int = 50):
    with get_db() as conn:
        if status and status != "all":
            return conn.execute("SELECT * FROM posts WHERE status = ? ORDER BY id DESC LIMIT ?", (status, limit)).fetchall()
        return conn.execute("SELECT * FROM posts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

@router.get("/{post_id}")
def get_post(post_id: int):
    with get_db() as conn:
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

@router.post("/generate")
def generate_post_now(data: Dict[str, Any] = Body(...)):
    category = data.get("category")
    topic = data.get("topic")
    language = data.get("language", "en")
    template_id = data.get("template_id")
    ai_provider_id = data.get("ai_provider_id")
    image_provider_id = data.get("image_provider_id")
    publish_now = data.get("publish_now", False)

    now_iso = datetime.now().isoformat()
    job_id = f"manual_{uuid.uuid4().hex[:8]}"

    try:
        post_data = content_engine.generate_full_post(
            category=category,
            custom_topic=topic,
            language=language,
            template_id=template_id,
            ai_provider_id=ai_provider_id,
            image_provider_id=image_provider_id
        )

        initial_status = post_data["status"]
        fb_post_id = None
        published_at = None

        if publish_now and initial_status == "ready":
            fb_client = FacebookGraphClient.from_database()
            pub_res = fb_client.publish_post(
                caption=post_data["caption"],
                image_local_path=post_data.get("image_local_path"),
                image_url=post_data.get("image_url")
            )
            fb_post_id = pub_res.get("id") or pub_res.get("post_id") or "ok"
            initial_status = "published"
            published_at = now_iso

        with get_db() as conn:
            cursor = conn.execute("""
                INSERT INTO posts (
                    job_id, topic_id, category, headline, caption, language, hashtags,
                    image_url, image_local_path, ai_provider_used, image_provider_used,
                    status, scheduled_for, published_at, fb_post_id, error_message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                post_data.get("topic_id"),
                post_data["category"],
                post_data["headline"],
                post_data["caption"],
                post_data["language"],
                post_data["hashtags"],
                post_data.get("image_url"),
                post_data.get("image_local_path"),
                post_data.get("ai_provider_used"),
                post_data.get("image_provider_used"),
                initial_status,
                now_iso if not publish_now else None,
                published_at,
                str(fb_post_id) if fb_post_id else None,
                post_data.get("error_message"),
                now_iso,
                now_iso
            ))
            new_id = cursor.lastrowid

        return {
            "success": True,
            "post_id": new_id,
            "status": initial_status,
            "fb_post_id": fb_post_id,
            "data": post_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/{post_id}/publish")
def publish_existing_post(post_id: int):
    with get_db() as conn:
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

    fb_client = FacebookGraphClient.from_database()
    try:
        res = fb_client.publish_post(
            caption=post["caption"],
            image_local_path=post.get("image_local_path"),
            image_url=post.get("image_url")
        )
        fb_id = res.get("id") or res.get("post_id") or "published_ok"
        now_iso = datetime.now().isoformat()
        with get_db() as conn:
            conn.execute("""
                UPDATE posts SET 
                    status = 'published', published_at = ?, fb_post_id = ?, error_message = NULL, updated_at = ?
                WHERE id = ?
            """, (now_iso, str(fb_id), now_iso, post_id))
        return {"success": True, "fb_post_id": fb_id, "message": "Post published to Facebook Page!"}
    except Exception as e:
        now_iso = datetime.now().isoformat()
        err_msg = str(e)
        with get_db() as conn:
            conn.execute("""
                UPDATE posts SET status = 'failed', error_message = ?, updated_at = ? WHERE id = ?
            """, (err_msg, now_iso, post_id))
        raise HTTPException(status_code=400, detail=f"Publish failed: {err_msg}")

@router.put("/{post_id}")
def update_post(post_id: int, data: Dict[str, Any] = Body(...)):
    now_iso = datetime.now().isoformat()
    with get_db() as conn:
        existing = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Post not found")

        conn.execute("""
            UPDATE posts SET 
                headline = ?, caption = ?, hashtags = ?, image_url = ?, status = ?, updated_at = ?
            WHERE id = ?
        """, (
            data.get("headline", existing["headline"]),
            data.get("caption", existing["caption"]),
            data.get("hashtags", existing["hashtags"]),
            data.get("image_url", existing["image_url"]),
            data.get("status", existing["status"]),
            now_iso,
            post_id
        ))

    return {"success": True, "message": "Post updated successfully."}

@router.delete("/{post_id}")
def delete_post(post_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    return {"success": True, "message": "Post deleted."}

@router.post("/{post_id}/retry")
def retry_failed_post(post_id: int):
    return publish_existing_post(post_id)
