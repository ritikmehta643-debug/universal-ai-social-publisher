from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from datetime import datetime
from ..database import get_db
from ..services.facebook.client import FacebookGraphClient, mask_token

router = APIRouter(prefix="/api/facebook", tags=["Facebook"])

@router.get("/status")
def get_facebook_status():
    with get_db() as conn:
        row = conn.execute("SELECT * FROM facebook_config WHERE id = 1").fetchone()
    
    if not row:
        return {"is_connected": False, "status": "disconnected"}

    return {
        "page_id": row["page_id"],
        "page_name": row["page_name"],
        "masked_token": mask_token(row.get("page_access_token")),
        "is_connected": bool(row["is_connected"]),
        "status": row["status"],
        "permissions": row.get("permissions"),
        "error_message": row.get("error_message"),
        "last_tested_at": row.get("last_tested_at")
    }

@router.post("/save-config")
def save_facebook_config(data: Dict[str, Any] = Body(...)):
    page_id = data.get("page_id", "").strip()
    page_name = data.get("page_name", "").strip()
    page_access_token = data.get("page_access_token", "").strip()

    if not page_id or not page_access_token:
        raise HTTPException(status_code=400, detail="Page ID and Page Access Token are required.")

    # Validate with Facebook Graph API
    client = FacebookGraphClient(page_id=page_id, page_access_token=page_access_token)
    is_valid, info = client.verify_page_access()

    now = datetime.now().isoformat()
    if not is_valid:
        err_msg = info.get("error", "Failed to verify Facebook Page credentials.")
        with get_db() as conn:
            conn.execute("""
                UPDATE facebook_config SET 
                    page_id = ?, page_access_token = ?, is_connected = 0, status = 'error', error_message = ?, updated_at = ?
                WHERE id = 1
            """, (page_id, page_access_token, err_msg, now))
        raise HTTPException(status_code=400, detail=f"Verification failed: {err_msg}")

    resolved_name = info.get("name", page_name or f"Page {page_id}")
    with get_db() as conn:
        conn.execute("""
            UPDATE facebook_config SET 
                page_id = ?, page_name = ?, page_access_token = ?, is_connected = 1, 
                status = 'connected', error_message = NULL, last_tested_at = ?, updated_at = ?
            WHERE id = 1
        """, (page_id, resolved_name, page_access_token, now, now))

    return {
        "success": True,
        "message": f"Successfully connected to Facebook Page: {resolved_name}",
        "page_name": resolved_name,
        "page_id": page_id
    }

@router.post("/fetch-pages")
def fetch_managed_pages(data: Dict[str, Any] = Body(...)):
    user_token = data.get("user_access_token", "").strip()
    if not user_token:
        raise HTTPException(status_code=400, detail="User Access Token is required.")

    client = FacebookGraphClient()
    try:
        pages = client.fetch_managed_pages(user_token)
        sanitized = []
        for p in pages:
            sanitized.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "category": p.get("category"),
                "access_token": p.get("access_token")
            })
        return {"success": True, "pages": sanitized}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch pages: {str(e)}")

@router.post("/test-publish")
def test_publish_to_facebook(data: Dict[str, Any] = Body(...)):
    message = data.get("message", "🚀 Test post from Universal AI Social Publisher. System is live and ready! #AutoPosting #UniversalAI")
    image_url = data.get("image_url")

    client = FacebookGraphClient.from_database()
    try:
        res = client.publish_post(caption=message, image_url=image_url)
        fb_id = res.get("id") or res.get("post_id") or "ok"
        now = datetime.now().isoformat()
        with get_db() as conn:
            conn.execute("""
                INSERT INTO posts (job_id, category, headline, caption, status, published_at, fb_post_id, created_at, updated_at)
                VALUES (?, 'System Test', 'Meta Graph API Test Publish', ?, 'published', ?, ?, ?, ?)
            """, (f"test_{fb_id}", message, now, str(fb_id), now, now))
        return {"success": True, "post_id": fb_id, "message": "Test post successfully published to Facebook Page!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Publish failed: {str(e)}")

@router.post("/disconnect")
def disconnect_facebook():
    now = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute("""
            UPDATE facebook_config SET 
                page_id = NULL, page_name = NULL, page_access_token = NULL, user_access_token = NULL,
                is_connected = 0, status = 'disconnected', error_message = NULL, updated_at = ?
            WHERE id = 1
        """, (now,))
    return {"success": True, "message": "Facebook Page disconnected."}
