import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.facebook.client import FacebookGraphClient, mask_token
from app.services.ai.base import mask_api_key
from app.services.ai.factory import create_provider_instance
from app.services.image.factory import create_image_provider_instance

class TestFacebookAndProviders(unittest.TestCase):
    def test_token_masking(self):
        self.assertEqual(mask_token(""), "")
        self.assertEqual(mask_token("short"), "••••••••••")
        token = "EAAQWERTYUIOPASDFGHJKLZXCVBNM123456"
        masked = mask_token(token)
        self.assertTrue(masked.startswith("EAAQWE"))
        self.assertTrue(masked.endswith("3456"))
        self.assertIn("••••••••••", masked)

    def test_api_key_masking(self):
        self.assertEqual(mask_api_key(""), "")
        self.assertEqual(mask_api_key("1234"), "••••••••")
        key = "AIzaSyAbcdEfghIjklMnop1234"
        masked = mask_api_key(key)
        self.assertTrue(masked.startswith("AIza"))
        self.assertTrue(masked.endswith("1234"))

    def test_facebook_client_verify_unconnected(self):
        client = FacebookGraphClient(page_id="", page_access_token="")
        is_valid, info = client.verify_page_access()
        self.assertFalse(is_valid)
        self.assertIn("error", info)

    def test_provider_factory_instantiation(self):
        configs = [
            {"provider_type": "gemini", "name": "Google Gemini", "api_key": "dummy", "model": "gemini-2.5-flash"},
            {"provider_type": "openai", "name": "OpenAI", "api_key": "dummy", "model": "gpt-4o"},
            {"provider_type": "claude", "name": "Anthropic Claude", "api_key": "dummy", "model": "claude-3-5-sonnet-20241022"},
            {"provider_type": "groq", "name": "Groq", "api_key": "dummy", "model": "llama-3.3-70b-versatile"},
            {"provider_type": "openrouter", "name": "OpenRouter", "api_key": "dummy", "model": "meta-llama/llama-3.3-70b-instruct"},
            {"provider_type": "huggingface", "name": "Hugging Face", "api_key": "dummy", "model": "meta-llama/Llama-3.2-3B-Instruct"},
            {"provider_type": "custom", "name": "Custom Ollama", "api_key": "", "api_endpoint": "http://localhost:11434/v1", "model": "llama3"}
        ]
        for cfg in configs:
            inst = create_provider_instance(cfg)
            self.assertEqual(inst.name, cfg["name"])
            self.assertEqual(inst.model, cfg["model"])

    def test_image_provider_factory_instantiation(self):
        img_cfg = {
            "provider_type": "gemini",
            "name": "Gemini Imagen 3",
            "api_key": "dummy",
            "model": "imagen-3.0-generate-002",
            "aspect_ratio": "1:1",
            "style": "photorealistic documentary"
        }
        inst = create_image_provider_instance(img_cfg)
        self.assertEqual(inst.name, "Gemini Imagen 3")
        enhanced = inst.enhance_prompt("A 1965 Le Mans race car")
        self.assertIn("photorealistic documentary", enhanced)
        self.assertIn("1965 Le Mans race car", enhanced)

if __name__ == "__main__":
    unittest.main()
