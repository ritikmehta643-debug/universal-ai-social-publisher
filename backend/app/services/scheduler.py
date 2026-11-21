import threading
import time
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ..database import get_db
from .content_engine import ContentEngine
from .facebook.client import FacebookGraphClient

logger = logging.getLogger(__name__)

class PublishingScheduler:
    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._is_running = False
        self._stop_event = threading.Event()
        self.content_engine = ContentEngine()

    def start(self):
        if self._is_running:
            logger.info("Scheduler already active.")
            return
        self._is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="AutoPostingScheduler")
        self._thread.start()
        logger.info("Background Auto-Posting Scheduler started successfully.")

    def stop(self):
        self._is_running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Background Auto-Posting Scheduler stopped.")

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self.check_and_execute_schedules()
                self.check_future_scheduled_posts()
            except Exception as e:
                logger.error(f"Error in scheduler tick: {e}", exc_info=True)
            # Sleep 30 seconds between checks
            self._stop_event.wait(30)

    def is_automation_enabled(self) -> bool:
        with get_db() as conn:
            setting = conn.execute("SELECT value FROM system_settings WHERE key = 'automation_enabled'").fetchone()
            return setting["value"].lower() == "true" if setting else False

    def get_current_time_str(self) -> str:
        """Returns current time in HH:MM format."""
        return datetime.now().strftime("%H:%M")

    def get_current_date_str(self) -> str:
        """Returns current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")

    def check_and_execute_schedules(self):
        if not self.is_automation_enabled():
            return

        current_time = self.get_current_time_str()
        today_date = self.get_current_date_str()

        with get_db() as conn:
            slots = conn.execute("SELECT * FROM schedules WHERE is_enabled = 1 ORDER BY slot_number ASC").fetchall()

        for slot in slots:
            slot_id = slot["id"]
            slot_num = slot["slot_number"]
            post_time = slot["post_time"]
            job_id = f"auto_slot{slot_num}_{today_date}"

            # If current time has reached or passed scheduled slot time today
            if current_time >= post_time:
                # Check if this slot was already processed today
                with get_db() as conn:
                    existing = conn.execute(
                        "SELECT id, status FROM posts WHERE job_id = ?", (job_id,)
                    ).fetchone()

                if not existing:
                    logger.info(f"Triggering scheduled post for Slot #{slot_num} ({post_time}) with Job ID: {job_id}")
                    self.execute_slot_publishing(slot, job_id)

    def execute_slot_publishing(self, slot: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Runs complete generation and publishing workflow for a specific schedule slot."""
        now_iso = datetime.now().isoformat()
        slot_id = slot["id"]
        category = slot.get("category_preference") or "Any"
        template_id = slot.get("caption_template_id")

        # Create initial post entry with 'generating' status
        with get_db() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO posts (
                    schedule_id, job_id, category, headline, caption, status, scheduled_for, created_at, updated_at
                ) VALUES (?, ?, ?, 'Generating content...', 'AI is crafting documentary post...', 'generating', ?, ?, ?)
            """, (slot_id, job_id, category, now_iso, now_iso, now_iso))
            conn.commit()

        try:
            # 1. Content Generation
            logger.info(f"Generating content for slot {slot['slot_number']} ({category})")
            post_data = self.content_engine.generate_full_post(
                category=category if category != "Any" else None,
                template_id=template_id
            )

            # Update post with generated details
            with get_db() as conn:
                conn.execute("""
                    UPDATE posts SET 
                        topic_id = ?,
                        headline = ?,
                        caption = ?,
                        language = ?,
                        hashtags = ?,
                        image_url = ?,
                        image_local_path = ?,
                        ai_provider_used = ?,
                        image_provider_used = ?,
                        status = ?,
                        error_message = ?,
                        updated_at = ?
                    WHERE job_id = ?
                """, (
                    post_data.get("topic_id"),
                    post_data["headline"],
                    post_data["caption"],
                    post_data["language"],
                    post_data["hashtags"],
                    post_data.get("image_url"),
                    post_data.get("image_local_path"),
                    post_data.get("ai_provider_used"),
                    post_data.get("image_provider_used"),
                    post_data["status"],
                    post_data.get("error_message"),
                    datetime.now().isoformat(),
                    job_id
                ))

            # If image failed or post is pending, do not publish yet
            if post_data["status"] == "pending":
                logger.warning(f"Post {job_id} remains pending: {post_data.get('error_message')}")
                return {"success": False, "status": "pending", "reason": post_data.get("error_message")}

            # 2. Publish to Meta Graph API
            fb_client = FacebookGraphClient.from_database()
            is_valid, _ = fb_client.verify_page_access()
            if not is_valid:
                err_msg = "Facebook Page is not connected or access token expired."
                with get_db() as conn:
                    conn.execute(
                        "UPDATE posts SET status = 'failed', error_message = ?, updated_at = ? WHERE job_id = ?",
                        (err_msg, datetime.now().isoformat(), job_id)
                    )
                logger.error(err_msg)
                return {"success": False, "error": err_msg}

            # Call Meta Graph API
            pub_res = fb_client.publish_post(
                caption=post_data["caption"],
                image_local_path=post_data.get("image_local_path"),
                image_url=post_data.get("image_url")
            )
            fb_post_id = pub_res.get("id") or pub_res.get("post_id") or "published_ok"

            # Update post to published
            with get_db() as conn:
                conn.execute("""
                    UPDATE posts SET 
                        status = 'published',
                        published_at = ?,
                        fb_post_id = ?,
                        error_message = NULL,
                        updated_at = ?
                    WHERE job_id = ?
                """, (datetime.now().isoformat(), str(fb_post_id), datetime.now().isoformat(), job_id))

                conn.execute(
                    "UPDATE schedules SET last_run_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), slot_id)
                )

            logger.info(f"Successfully published post {job_id} to Facebook Page. Post ID: {fb_post_id}")
            return {"success": True, "fb_post_id": fb_post_id}

        except Exception as e:
            err_str = str(e)
            logger.error(f"Failed to publish scheduled post {job_id}: {err_str}", exc_info=True)
            with get_db() as conn:
                conn.execute("""
                    UPDATE posts SET 
                        status = 'failed',
                        error_message = ?,
                        retry_count = retry_count + 1,
                        updated_at = ?
                    WHERE job_id = ?
                """, (err_str, datetime.now().isoformat(), job_id))
            return {"success": False, "error": err_str}

    def check_future_scheduled_posts(self):
        """Checks for posts with explicit scheduled_for timestamps that have reached due time."""
        now_iso = datetime.now().isoformat()
        with get_db() as conn:
            due_posts = conn.execute("""
                SELECT * FROM posts 
                WHERE status = 'ready' 
                AND scheduled_for IS NOT NULL 
                AND scheduled_for <= ?
                LIMIT 5
            """, (now_iso,)).fetchall()

        for post in due_posts:
            logger.info(f"Publishing due scheduled post: {post['id']} - {post['headline']}")
            try:
                fb_client = FacebookGraphClient.from_database()
                res = fb_client.publish_post(
                    caption=post["caption"],
                    image_local_path=post.get("image_local_path"),
                    image_url=post.get("image_url")
                )
                fb_id = res.get("id") or res.get("post_id") or "ok"
                with get_db() as conn:
                    conn.execute("""
                        UPDATE posts SET 
                            status = 'published',
                            published_at = ?,
                            fb_post_id = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), str(fb_id), datetime.now().isoformat(), post["id"]))
            except Exception as e:
                logger.error(f"Failed to publish scheduled post {post['id']}: {e}")
                with get_db() as conn:
                    conn.execute("""
                        UPDATE posts SET 
                            status = 'failed',
                            error_message = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (str(e), datetime.now().isoformat(), post["id"]))

    def publish_immediately(self, post_id: Optional[int] = None, generate_new: bool = False, category: Optional[str] = None) -> Dict[str, Any]:
        """Allows instant on-demand publishing."""
        if generate_new:
            job_id = f"manual_{uuid.uuid4().hex[:8]}_{self.get_current_date_str()}"
            slot_mock = {"id": None, "slot_number": 0, "category_preference": category or "Any", "caption_template_id": None}
            return self.execute_slot_publishing(slot_mock, job_id)

        if post_id:
            with get_db() as conn:
                post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
            if not post:
                return {"success": False, "error": f"Post #{post_id} not found"}

            fb_client = FacebookGraphClient.from_database()
            try:
                res = fb_client.publish_post(
                    caption=post["caption"],
                    image_local_path=post.get("image_local_path"),
                    image_url=post.get("image_url")
                )
                fb_id = res.get("id") or res.get("post_id") or "ok"
                with get_db() as conn:
                    conn.execute("""
                        UPDATE posts SET 
                            status = 'published',
                            published_at = ?,
                            fb_post_id = ?,
                            error_message = NULL,
                            updated_at = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), str(fb_id), datetime.now().isoformat(), post["id"]))
                return {"success": True, "fb_post_id": fb_id}
            except Exception as e:
                with get_db() as conn:
                    conn.execute("""
                        UPDATE posts SET status = 'failed', error_message = ?, updated_at = ? WHERE id = ?
                    """, (str(e), datetime.now().isoformat(), post["id"]))
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "Invalid request"}
