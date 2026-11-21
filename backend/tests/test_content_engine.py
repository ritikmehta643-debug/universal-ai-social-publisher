import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.content_engine import ContentEngine
from app.database import init_db

class TestContentEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.engine = ContentEngine()

    def test_get_topic_discovery(self):
        topic = self.engine.get_or_discover_topic("History")
        self.assertIsNotNone(topic)
        self.assertIn("category", topic)
        self.assertEqual(topic["category"], "History")

    def test_build_prompts_en_and_hi(self):
        topic = {"category": "History", "title": "The Battle of Saragarhi", "prompt_seed": "21 Sikh soldiers"}
        template_en = {"language": "en", "hook_style": "dramatic", "storytelling_format": "deep_dive", "hashtag_quantity": 10}
        sys_p, user_p = self.engine.build_generation_prompts(topic, template_en)
        self.assertIn("English", sys_p)
        self.assertIn("Battle of Saragarhi", user_p)

        template_hi = {"language": "hi", "hook_style": "emotional", "storytelling_format": "emotional_biography", "hashtag_quantity": 8}
        sys_hi, user_hi = self.engine.build_generation_prompts(topic, template_hi)
        self.assertIn("Hindi", sys_hi)

    def test_parse_ai_response_valid_json(self):
        raw = """```json
        {
            "headline": "The Mystery of the Mary Celeste",
            "hook": "In 1872, a ship was found sailing completely unharmed with no soul on board.",
            "body_paragraphs": [
                "The Mary Celeste was discovered adrift in choppy Atlantic waters.",
                "All cargo was intact, six months of food remained, yet the crew had vanished forever."
            ],
            "takeaway": "Some maritime enigmas remain forever locked in ocean silence.",
            "image_prompt": "A ghost ship Mary Celeste adrift in misty Atlantic waters at dusk, cinematic documentary photograph",
            "hashtags": ["#MaryCeleste", "#UnsolvedMysteries", "#GhostShip", "#MaritimeHistory"]
        }
        ```"""
        parsed = self.engine.parse_ai_response(raw)
        self.assertEqual(parsed["headline"], "The Mystery of the Mary Celeste")
        self.assertEqual(len(parsed["body_paragraphs"]), 2)
        self.assertEqual(len(parsed["hashtags"]), 4)

    def test_assemble_final_caption(self):
        content = {
            "headline": "The Unsung Hero",
            "hook": "He faced 100 adversaries alone.",
            "body_paragraphs": ["On a freezing winter morning, destiny called.", "He held the line until reinforcements arrived."],
            "takeaway": "Courage is resistance to fear.",
            "hashtags": ["#Hero", "#Bravery", "#Courage"]
        }
        template = {
            "hashtag_quantity": 5,
            "ending_line": "👉 Follow for more true heroic stories."
        }
        caption, hashtags = self.engine.assemble_final_caption(content, template)
        self.assertIn("🔴 THE UNSUNG HERO", caption)
        self.assertIn("⚡ He faced 100 adversaries alone.", caption)
        self.assertIn("👉 Follow for more true heroic stories.", caption)
        self.assertIn("#Hero", hashtags)

if __name__ == "__main__":
    unittest.main()
