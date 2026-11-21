import sqlite3
import json
import logging
from datetime import datetime
from contextlib import contextmanager
from .config import DB_PATH, DEFAULT_DAILY_SLOTS, CATEGORIES

logger = logging.getLogger(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def init_db():
    """Initializes tables and seeds default data."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. AI Providers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                provider_type TEXT NOT NULL,
                api_endpoint TEXT,
                api_key TEXT,
                model TEXT NOT NULL,
                image_model TEXT,
                is_enabled INTEGER DEFAULT 1,
                is_default INTEGER DEFAULT 0,
                is_fallback INTEGER DEFAULT 0,
                status TEXT DEFAULT 'untested',
                error_message TEXT,
                last_tested_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 2. Image Providers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                provider_type TEXT NOT NULL,
                api_endpoint TEXT,
                api_key TEXT,
                model TEXT,
                aspect_ratio TEXT DEFAULT '1:1',
                resolution TEXT DEFAULT '1024x1024',
                style TEXT DEFAULT 'photorealistic documentary',
                negative_prompt TEXT,
                is_enabled INTEGER DEFAULT 1,
                is_default INTEGER DEFAULT 0,
                is_fallback INTEGER DEFAULT 0,
                status TEXT DEFAULT 'untested',
                error_message TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 3. Facebook Configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facebook_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id TEXT,
                page_name TEXT,
                page_access_token TEXT,
                user_access_token TEXT,
                token_expires_at TEXT,
                is_connected INTEGER DEFAULT 0,
                permissions TEXT,
                status TEXT DEFAULT 'disconnected',
                error_message TEXT,
                last_tested_at TEXT,
                updated_at TEXT NOT NULL
            )
        """)

        # 4. Caption Templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caption_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                hook_style TEXT DEFAULT 'shocking_fact',
                caption_length TEXT DEFAULT 'documentary',
                storytelling_format TEXT DEFAULT 'deep_dive',
                language TEXT DEFAULT 'en',
                emoji_usage TEXT DEFAULT 'moderate',
                hashtag_quantity INTEGER DEFAULT 10,
                cta_style TEXT DEFAULT 'follow_page',
                brand_voice TEXT DEFAULT 'dramatic',
                ending_line TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # 5. Topics Library
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL UNIQUE,
                prompt_seed TEXT,
                times_used INTEGER DEFAULT 0,
                last_used_at TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        # 6. Schedules (Fixed Posting Times)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_number INTEGER NOT NULL UNIQUE,
                post_time TEXT NOT NULL,
                category_preference TEXT DEFAULT 'Any',
                caption_template_id INTEGER,
                is_enabled INTEGER DEFAULT 1,
                last_run_at TEXT,
                next_run_at TEXT,
                FOREIGN KEY (caption_template_id) REFERENCES caption_templates (id) ON DELETE SET NULL
            )
        """)

        # 7. Posts (Scheduled, Published, Failed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                job_id TEXT UNIQUE NOT NULL,
                topic_id INTEGER,
                category TEXT NOT NULL,
                headline TEXT NOT NULL,
                caption TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                hashtags TEXT,
                image_url TEXT,
                image_local_path TEXT,
                ai_provider_used TEXT,
                image_provider_used TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                scheduled_for TEXT,
                published_at TEXT,
                fb_post_id TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE SET NULL,
                FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE SET NULL
            )
        """)

        # 8. System Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT
            )
        """)

        # Seed Defaults if empty
        _seed_defaults(cursor)

def _seed_defaults(cursor):
    now = datetime.now().isoformat()

    # Seed System Settings
    settings = [
        ("automation_enabled", "true", "Global automation master toggle"),
        ("daily_post_target", "5", "Daily automated publishing target"),
        ("timezone", "Asia/Kolkata", "Default operational timezone"),
        ("duplicate_window_days", "30", "Window in days to prevent repeating topics"),
        ("auto_retry_failed", "true", "Auto retry failed posts once"),
    ]
    for key, val, desc in settings:
        cursor.execute("""
            INSERT OR IGNORE INTO system_settings (key, value, description)
            VALUES (?, ?, ?)
        """, (key, val, desc))

    # Seed Default AI Providers
    default_providers = [
        ("Google Gemini", "gemini", "https://generativelanguage.googleapis.com", "", "gemini-2.5-flash", "imagen-3.0-generate-002", 1, 1, 0),
        ("OpenAI", "openai", "https://api.openai.com/v1", "", "gpt-4o", "dall-e-3", 0, 0, 1),
        ("Anthropic Claude", "claude", "https://api.anthropic.com/v1", "", "claude-3-5-sonnet-20241022", "", 0, 0, 0),
        ("Groq", "groq", "https://api.groq.com/openai/v1", "", "llama-3.3-70b-versatile", "", 0, 0, 0),
        ("OpenRouter", "openrouter", "https://openrouter.ai/api/v1", "", "meta-llama/llama-3.3-70b-instruct", "", 0, 0, 0),
        ("Hugging Face", "huggingface", "https://api-inference.huggingface.co/models", "", "meta-llama/Llama-3.2-3B-Instruct", "black-forest-labs/FLUX.1-schnell", 0, 0, 0),
        ("Custom OpenAI-Compatible", "custom", "http://localhost:11434/v1", "", "llama3", "", 0, 0, 0)
    ]
    for name, ptype, ep, key, model, imodel, enabled, is_def, is_fall in default_providers:
        cursor.execute("""
            INSERT OR IGNORE INTO ai_providers (name, provider_type, api_endpoint, api_key, model, image_model, is_enabled, is_default, is_fallback, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, ptype, ep, key, model, imodel, enabled, is_def, is_fall, now, now))

    # Seed Default Image Providers
    image_providers = [
        ("Gemini Imagen 3", "gemini", "https://generativelanguage.googleapis.com", "", "imagen-3.0-generate-002", "1:1", "1024x1024", "photorealistic documentary", "blurry, low quality, distorted, cartoon", 1, 1, 0),
        ("OpenAI DALL-E 3", "dalle", "https://api.openai.com/v1", "", "dall-e-3", "1:1", "1024x1024", "photorealistic cinematic documentary", "text, watermark, unrealistic, oversaturated", 0, 0, 1),
        ("HuggingFace FLUX", "huggingface", "https://api-inference.huggingface.co/models", "", "black-forest-labs/FLUX.1-schnell", "1:1", "1024x1024", "documentary photograph", "drawing, CGI, fake, text", 0, 0, 0),
        ("Custom Image Endpoint", "custom", "", "", "", "1:1", "1024x1024", "photorealistic documentary", "blurry, cartoon", 0, 0, 0)
    ]
    for name, ptype, ep, key, model, ar, res, style, neg, enabled, is_def, is_fall in image_providers:
        cursor.execute("""
            INSERT OR IGNORE INTO image_providers (name, provider_type, api_endpoint, api_key, model, aspect_ratio, resolution, style, negative_prompt, is_enabled, is_default, is_fallback, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, ptype, ep, key, model, ar, res, style, neg, enabled, is_def, is_fall, now))

    # Seed Default Facebook Config Row
    cursor.execute("""
        INSERT OR IGNORE INTO facebook_config (id, status, is_connected, updated_at)
        VALUES (1, 'disconnected', 0, ?)
    """, (now,))

    # Seed Default Caption Templates
    templates = [
        ("Documentary Deep Dive (English)", "shocking_fact", "documentary", "deep_dive", "en", "moderate", 12, "follow_page", "dramatic", "👉 Follow our page for unforgettable stories and untold history.", 1),
        ("Real Soldier Heroics (Hindi/English)", "dramatic_statement", "long", "emotional_biography", "hi", "moderate", 10, "comment_opinion", "inspiring", "🇮🇳 भारतीय सेना के वीर शहीदों को हमारा कोटि-कोटि नमन। जय हिन्द!", 0),
        ("Mysterious Events & Secrets", "intriguing_question", "documentary", "mystery_reveal", "en", "moderate", 15, "comment_opinion", "mysterious", "💬 What do you think really happened? Drop your theories below!", 0),
        ("Auto & Supercar Legends", "shocking_fact", "long", "chronological", "en", "moderate", 10, "share_story", "authoritative", "🏎️ Share this with fellow gearheads who appreciate engineering marvels.", 0),
    ]
    for name, hook, length, fmt, lang, emoji, hashtags, cta, voice, ending, is_def in templates:
        cursor.execute("""
            INSERT OR IGNORE INTO caption_templates (name, hook_style, caption_length, storytelling_format, language, emoji_usage, hashtag_quantity, cta_style, brand_voice, ending_line, is_default, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, hook, length, fmt, lang, emoji, hashtags, cta, voice, ending, is_def, now))

    # Seed Default 5 Daily Schedules
    for slot_item in DEFAULT_DAILY_SLOTS:
        cursor.execute("""
            INSERT OR IGNORE INTO schedules (slot_number, post_time, category_preference, is_enabled)
            VALUES (?, ?, 'Any', 1)
        """, (slot_item["slot"], slot_item["time"]))

    # Seed Core Topics Library
    sample_topics = [
        ("History", "The Lost City of Atlantis: Myth or Ancient Engineering Marvel?", "Examine ancient archaeological clues and historical theories about Atlantis."),
        ("History", "The Battle of Saragarhi: 21 Sikhs Against 10,000 Warriors", "Tell the heroic story of Havildar Ishar Singh and the 21 soldiers at Saragarhi."),
        ("Mysterious Events", "The Dyatlov Pass Incident: 9 Hikers and an Unsolved Mountain Tragedy", "Documentary narrative on what truly transpired on Kholat Syakhl in 1959."),
        ("Mysterious Events", "The Voynich Manuscript: The Unbreakable 600-Year-Old Code", "Explore the mystery of the world's most mysterious illustrated book."),
        ("Real Soldier Stories", "Major Somnath Sharma: Param Vir Chakra of Badgam 1947", "Inspiring chronicle of India's first PVC recipient who defended Srinagar airport."),
        ("Real Soldier Stories", "Captain Vikram Batra: Yeh Dil Maange More in Kargil 1999", "Heroic documentary on Point 5140 and Point 4875 during the Kargil War."),
        ("Cars and Automobile Stories", "The Birth of the Ford GT40: Henry Ford II vs Enzo Ferrari at Le Mans", "The legendary racing rivalry that birthed the American supercar champion."),
        ("Cars and Automobile Stories", "The Unkillable Toyota Hilux: Engineering That Defied Physics", "How an everyday Japanese truck became an indestructible global icon."),
        ("Cricket and Sports", "The 1983 World Cup Miracle: Kapil Dev's Underdogs Shook Lord's", "The historic tournament that transformed Indian cricket forever."),
        ("Cricket and Sports", "Dhyan Chand: The Hockey Wizard Who Left Adolf Hitler Speechless", "The Berlin 1936 Olympics and the legacy of the greatest hockey player."),
        ("Science and Technology", "James Webb Space Telescope: Peering into the Cosmic Dawn", "How infrared astronomy is rewriting our understanding of the early universe."),
        ("Science and Technology", "The Voyager 1 Golden Record: Humanity's Message in a Cosmic Bottle", "The journey of the farthest human-made object traveling across interstellar space."),
        ("Biography", "Nikola Tesla: The Eccentric Genius Who Lit Up the Modern World", "The triumphs, eccentricities, and wireless energy dreams of Tesla."),
        ("Biography", "APJ Abdul Kalam: The Missile Man Who Won a Billion Hearts", "From selling newspapers in Rameswaram to President of India."),
        ("Interesting Facts", "Why the Sahara Desert Was Once Green, Lush and Full of Lakes", "The geological cycle of the African humid period and its implications."),
        ("Business Stories", "The Fall of Kodak: How the Inventor of Digital Cameras Destroyed Itself", "A powerful business case study in technological disruption and denial.")
    ]
    for cat, title, seed in sample_topics:
        cursor.execute("""
            INSERT OR IGNORE INTO topics (category, title, prompt_seed, times_used, is_active, created_at)
            VALUES (?, ?, ?, 0, 1, ?)
        """, (cat, title, seed, now))
