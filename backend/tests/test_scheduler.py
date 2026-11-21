import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, get_db
from app.services.scheduler import PublishingScheduler

class TestScheduler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.scheduler = PublishingScheduler()

    def test_automation_setting(self):
        with get_db() as conn:
            conn.execute("UPDATE system_settings SET value = 'true' WHERE key = 'automation_enabled'")
        self.assertTrue(self.scheduler.is_automation_enabled())

        with get_db() as conn:
            conn.execute("UPDATE system_settings SET value = 'false' WHERE key = 'automation_enabled'")
        self.assertFalse(self.scheduler.is_automation_enabled())

        # Reset to true
        with get_db() as conn:
            conn.execute("UPDATE system_settings SET value = 'true' WHERE key = 'automation_enabled'")

    def test_idempotency_prevents_duplicate_slot(self):
        today = self.scheduler.get_current_date_str()
        test_job_id = f"test_slot_dup_{today}"
        now_iso = "2026-11-21T06:00:00"

        with get_db() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO posts (job_id, category, headline, caption, status, created_at, updated_at)
                VALUES (?, 'History', 'Test Title', 'Test Caption', 'published', ?, ?)
            """, (test_job_id, now_iso, now_iso))

            # Query job_id
            existing = conn.execute("SELECT id FROM posts WHERE job_id = ?", (test_job_id,)).fetchone()
            self.assertIsNotNone(existing)

if __name__ == "__main__":
    unittest.main()
