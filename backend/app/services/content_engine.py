import json
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from ..database import get_db
from .ai.factory import generate_with_fallback
from .image.factory import generate_image_with_fallback
from ..config import CATEGORIES

logger = logging.getLogger(__name__)

class ContentEngine:
    def __init__(self):
        pass

    def get_or_discover_topic(self, category_preference: str = "Any") -> Dict[str, Any]:
        """
        Picks the best topic to write about, prioritizing unposted or least-recently-posted topics.
        Prevents duplicate posting within the duplicate window.
        """
        with get_db() as conn:
            # Check duplicate window setting
            window_setting = conn.execute("SELECT value FROM system_settings WHERE key = 'duplicate_window_days'").fetchone()
            window_days = int(window_setting["value"]) if window_setting else 30
            cutoff = (datetime.now() - timedelta(days=window_days)).isoformat()

            query = """
                SELECT * FROM topics 
                WHERE is_active = 1
                AND (last_used_at IS NULL OR last_used_at < ?)
            """
            params: List[Any] = [cutoff]

            if category_preference and category_preference != "Any":
                query += " AND category = ?"
                params.append(category_preference)

            query += " ORDER BY times_used ASC, RANDOM() LIMIT 1"
            topic = conn.execute(query, params).fetchone()

            # If all topics within preferred category were recently used, relax cutoff
            if not topic:
                relax_query = "SELECT * FROM topics WHERE is_active = 1"
                relax_params: List[Any] = []
                if category_preference and category_preference != "Any":
                    relax_query += " AND category = ?"
                    relax_params.append(category_preference)
                relax_query += " ORDER BY times_used ASC, RANDOM() LIMIT 1"
                topic = conn.execute(relax_query, relax_params).fetchone()

            # If still nothing (e.g. empty table), generate a default topic
            if not topic:
                cat = category_preference if category_preference != "Any" else random.choice(CATEGORIES)
                return {
                    "id": None,
                    "category": cat,
                    "title": f"Untold Stories of {cat}",
                    "prompt_seed": f"Generate a profound documentary story about an extraordinary event in {cat}."
                }

            return topic

    def get_template(self, template_id: Optional[int] = None) -> Dict[str, Any]:
        with get_db() as conn:
            if template_id:
                t = conn.execute("SELECT * FROM caption_templates WHERE id = ?", (template_id,)).fetchone()
                if t:
                    return t
            # Default template
            t = conn.execute("SELECT * FROM caption_templates WHERE is_default = 1 LIMIT 1").fetchone()
            if t:
                return t
            return {
                "name": "Default Documentary",
                "hook_style": "shocking_fact",
                "caption_length": "documentary",
                "storytelling_format": "deep_dive",
                "language": "en",
                "emoji_usage": "moderate",
                "hashtag_quantity": 10,
                "cta_style": "follow_page",
                "brand_voice": "dramatic",
                "ending_line": "👉 Follow our page for unforgettable stories and untold history."
            }

    def build_generation_prompts(self, topic: Dict[str, Any], template: Dict[str, Any], custom_language: Optional[str] = None) -> Tuple[str, str]:
        language = custom_language or template.get("language", "en")
        lang_instruction = "English" if language == "en" else ("Hindi (Devanagari script with engaging Hindi narrative)" if language == "hi" else "Hinglish (Hindi written in Roman English script)")
        
        system_prompt = f"""You are an elite historical documentary writer, investigative researcher, and viral social media storytelling architect.
Your objective is to craft deep, fact-checked, captivating, long-form documentary captions for Facebook that command complete reader attention.

Guidelines:
1. Tone & Voice: {template.get('brand_voice', 'dramatic and authoritative')}.
2. Hook Style: {template.get('hook_style', 'shocking_fact')} - Open with a magnetic first sentence.
3. Story Format: {template.get('storytelling_format', 'deep_dive')} - Structure the story with gripping narrative arcs, concrete names, years, emotional resonance, and factual authenticity.
4. Language: Write the headline, hook, and story strictly in {lang_instruction}.
5. Emojis: {template.get('emoji_usage', 'moderate')} (use strategic, tasteful emojis to separate sections).
6. Fact Verification: Provide strictly verified historical facts; do not hallucinate fake dates or fake names.
7. Length: {template.get('caption_length', 'documentary')} (thorough, rich multi-paragraph storytelling that reads like a mini-documentary).

Output strictly valid JSON with the following keys:
{{
    "headline": "A bold, captivating title for the post",
    "hook": "An unforgettable opening hook line",
    "body_paragraphs": [
        "Paragraph 1 setting the scene...",
        "Paragraph 2 unveiling the conflict or discovery...",
        "Paragraph 3 the climax or historical significance..."
    ],
    "takeaway": "The lasting historical lesson or profound moral",
    "image_prompt": "A highly detailed, photorealistic visual scene description for an AI image generator (e.g., camera angle, 1940s lighting, 8k documentary photograph, dramatic atmosphere). Write the image_prompt in English.",
    "hashtags": ["#tag1", "#tag2", "#tag3"]
}}"""

        user_prompt = f"""Create an in-depth documentary feature about:
Category: {topic.get('category')}
Title: {topic.get('title')}
Background Context / Prompt Seed: {topic.get('prompt_seed', topic.get('title'))}

Target hashtags count: {template.get('hashtag_quantity', 10)}.
Ensure all requirements from your instructions are met. Output raw JSON only."""

        return system_prompt, user_prompt

    def parse_ai_response(self, raw_text: str) -> Dict[str, Any]:
        """Extracts JSON from AI response safely."""
        text = raw_text.strip()
        # Remove markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        # Find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            clean_json = text[start:end+1]
            try:
                return json.loads(clean_json)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}. Attempting fallback parser.")

        # Fallback if raw text isn't clean JSON
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        headline = lines[0] if lines else "Untold Historical Story"
        body = "\n\n".join(lines[1:]) if len(lines) > 1 else raw_text
        return {
            "headline": headline,
            "hook": headline,
            "body_paragraphs": [body],
            "takeaway": "",
            "image_prompt": f"Documentary photo representing {headline}, dramatic lighting, 8k resolution",
            "hashtags": ["#UntoldStories", "#Documentary", "#History", "#ViralPost"]
        }

    def assemble_final_caption(self, content: Dict[str, Any], template: Dict[str, Any]) -> Tuple[str, str]:
        """Combines headline, hook, body, CTA, ending line and hashtags into full Facebook post text."""
        headline = content.get("headline", "").strip()
        hook = content.get("hook", "").strip()
        paragraphs = content.get("body_paragraphs", [])
        takeaway = content.get("takeaway", "").strip()
        ending_line = template.get("ending_line", "").strip()
        hashtags = content.get("hashtags", [])

        # Limit or pad hashtags
        target_tags_count = template.get("hashtag_quantity", 10)
        formatted_tags = []
        for t in hashtags:
            cleaned = "#" + re.sub(r"[^a-zA-Z0-9_\u0900-\u097F]", "", t.replace("#", ""))
            if len(cleaned) > 1 and cleaned not in formatted_tags:
                formatted_tags.append(cleaned)
        formatted_tags = formatted_tags[:target_tags_count]
        hashtags_str = " ".join(formatted_tags)

        # Assemble
        parts = []
        if headline:
            parts.append(f"🔴 {headline.upper()}\n━━━━━━━━━━━━━━━━━━")
        if hook:
            parts.append(f"⚡ {hook}")
        for p in paragraphs:
            if p.strip():
                parts.append(p.strip())
        if takeaway:
            parts.append(f"💡 {takeaway}")
        if ending_line:
            parts.append(f"\n{ending_line}")
        if hashtags_str:
            parts.append(f"\n{hashtags_str}")

        full_caption = "\n\n".join(parts)
        return full_caption, hashtags_str

    def generate_full_post(
        self,
        category: Optional[str] = None,
        custom_topic: Optional[str] = None,
        language: Optional[str] = None,
        template_id: Optional[int] = None,
        ai_provider_id: Optional[int] = None,
        image_provider_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end post generation:
        1. Select topic
        2. Fetch template
        3. Generate content via AI
        4. Assemble caption
        5. Generate image via Image Engine
        6. Return complete post payload
        """
        template = self.get_template(template_id)

        if custom_topic:
            topic = {
                "id": None,
                "category": category or "Custom Topics",
                "title": custom_topic,
                "prompt_seed": custom_topic
            }
        else:
            topic = self.get_or_discover_topic(category_preference=category or "Any")

        logger.info(f"Generating post for topic: {topic.get('title')} in category: {topic.get('category')}")

        # 1. Generate text
        sys_prompt, user_prompt = self.build_generation_prompts(topic, template, custom_language=language)
        raw_ai_text, ai_provider_name = generate_with_fallback(user_prompt, system_prompt=sys_prompt, provider_id=ai_provider_id)
        parsed_content = self.parse_ai_response(raw_ai_text)

        full_caption, hashtags_str = self.assemble_final_caption(parsed_content, template)
        headline = parsed_content.get("headline", topic.get("title", "Social Post"))
        img_prompt = parsed_content.get("image_prompt", f"Photorealistic documentary scene of {headline}")

        # 2. Generate Image
        img_url, img_local_path, img_provider_name, img_error = generate_image_with_fallback(img_prompt, provider_id=image_provider_id)

        # 3. Update topic usage if it came from DB
        if topic.get("id"):
            with get_db() as conn:
                conn.execute(
                    "UPDATE topics SET times_used = times_used + 1, last_used_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), topic["id"])
                )

        status = "ready"
        error_msg = None
        if img_error:
            # If image failed, post is marked pending per requirements
            status = "pending"
            error_msg = f"Image pending: {img_error}"

        return {
            "topic_id": topic.get("id"),
            "category": topic.get("category", "General"),
            "headline": headline,
            "caption": full_caption,
            "language": language or template.get("language", "en"),
            "hashtags": hashtags_str,
            "image_url": img_url,
            "image_local_path": img_local_path,
            "image_prompt": img_prompt,
            "ai_provider_used": ai_provider_name,
            "image_provider_used": img_provider_name,
            "status": status,
            "error_message": error_msg
        }
