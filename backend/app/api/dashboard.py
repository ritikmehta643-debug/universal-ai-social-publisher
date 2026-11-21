from fastapi import APIRouter
from datetime import datetime
from ..database import get_db
from ..services.facebook.client import FacebookGraphClient

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard_summary():
    today_str = datetime.now().strftime("%Y-%m-%d")
    current_time_str = datetime.now().strftime("%H:%M")

    with get_db() as conn:
        # Total counts
        total_published = conn.execute("SELECT count(*) as c FROM posts WHERE status = 'published'").fetchone()["c"]
        today_published = conn.execute(
            "SELECT count(*) as c FROM posts WHERE status = 'published' AND published_at LIKE ?",
            (f"{today_str}%",)
        ).fetchone()["c"]
        scheduled_count = conn.execute("SELECT count(*) as c FROM posts WHERE status in ('ready', 'pending')").fetchone()["c"]
        failed_count = conn.execute("SELECT count(*) as c FROM posts WHERE status = 'failed'").fetchone()["c"]

        # Automation status
        auto_setting = conn.execute("SELECT value FROM system_settings WHERE key = 'automation_enabled'").fetchone()
        automation_enabled = auto_setting["value"].lower() == "true" if auto_setting else False

        # Next publishing slot
        next_slot = conn.execute("""
            SELECT slot_number, post_time, category_preference 
            FROM schedules 
            WHERE is_enabled = 1 AND post_time > ?
            ORDER BY post_time ASC LIMIT 1
        """, (current_time_str,)).fetchone()

        if not next_slot:
            # Wrap around to first slot tomorrow
            next_slot = conn.execute("""
                SELECT slot_number, post_time, category_preference 
                FROM schedules 
                WHERE is_enabled = 1
                ORDER BY post_time ASC LIMIT 1
            """).fetchone()

        # AI Provider status
        active_ai_providers = conn.execute("SELECT count(*) as c FROM ai_providers WHERE is_enabled = 1").fetchone()["c"]
        default_ai = conn.execute("SELECT name, status FROM ai_providers WHERE is_default = 1").fetchone()

        # Image Provider status
        active_img_providers = conn.execute("SELECT count(*) as c FROM image_providers WHERE is_enabled = 1").fetchone()["c"]
        default_img = conn.execute("SELECT name, status FROM image_providers WHERE is_default = 1").fetchone()

        # Facebook Status
        fb_row = conn.execute("SELECT page_id, page_name, is_connected, status, error_message FROM facebook_config WHERE id = 1").fetchone()

        # Recent Posts (last 5)
        recent_posts = conn.execute("""
            SELECT id, headline, category, status, published_at, scheduled_for, ai_provider_used, error_message, created_at
            FROM posts 
            ORDER BY id DESC LIMIT 5
        """).fetchall()

    return {
        "stats": {
            "total_published": total_published,
            "today_published": today_published,
            "scheduled_count": scheduled_count,
            "failed_count": failed_count,
            "automation_enabled": automation_enabled,
            "next_publishing": next_slot
        },
        "services": {
            "ai": {
                "active_count": active_ai_providers,
                "default_provider": default_ai["name"] if default_ai else "None",
                "status": default_ai["status"] if default_ai else "unconfigured"
            },
            "image": {
                "active_count": active_img_providers,
                "default_provider": default_img["name"] if default_img else "None",
                "status": default_img["status"] if default_img else "unconfigured"
            },
            "facebook": {
                "is_connected": bool(fb_row["is_connected"]) if fb_row else False,
                "page_name": fb_row["page_name"] if fb_row and fb_row["page_name"] else "Not configured",
                "page_id": fb_row["page_id"] if fb_row and fb_row["page_id"] else "",
                "status": fb_row["status"] if fb_row else "disconnected",
                "error": fb_row.get("error_message") if fb_row else None
            }
        },
        "recent_posts": recent_posts
    }
