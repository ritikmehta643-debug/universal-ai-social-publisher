import unittest
import os
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db, init_db

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_tables_exist(self):
        with get_db() as conn:
            tables = [r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            expected = ["ai_providers", "image_providers", "facebook_config", "caption_templates", "topics", "schedules", "posts", "system_settings"]
            for table in expected:
                self.assertIn(table, tables)

    def test_default_schedules_seeded(self):
        with get_db() as conn:
            slots = conn.execute("SELECT * FROM schedules ORDER BY slot_number ASC").fetchall()
            self.assertEqual(len(slots), 5)
            self.assertEqual(slots[0]["post_time"], "06:00")
            self.assertEqual(slots[1]["post_time"], "10:00")
            self.assertEqual(slots[2]["post_time"], "14:00")
            self.assertEqual(slots[3]["post_time"], "18:00")
            self.assertEqual(slots[4]["post_time"], "21:00")

    def test_default_ai_providers_seeded(self):
        with get_db() as conn:
            providers = conn.execute("SELECT name, provider_type FROM ai_providers").fetchall()
            names = [p["name"] for p in providers]
            self.assertIn("Google Gemini", names)
            self.assertIn("OpenAI", names)
            self.assertIn("Anthropic Claude", names)
            self.assertIn("Groq", names)

    def test_caption_templates_seeded(self):
        with get_db() as conn:
            templates = conn.execute("SELECT name FROM caption_templates").fetchall()
            self.assertGreaterEqual(len(templates), 2)

if __name__ == "__main__":
    unittest.main()
