import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

MEDIA_DIR = DATA_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True, parents=True)

DB_PATH = DATA_DIR / "publisher.db"

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

# Default Timezone
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")

# Meta Facebook Graph API version
FB_GRAPH_API_VERSION = os.getenv("FB_GRAPH_API_VERSION", "v21.0")
FB_GRAPH_BASE_URL = f"https://graph.facebook.com/{FB_GRAPH_API_VERSION}"

# Daily publishing defaults
DEFAULT_DAILY_SLOTS = [
    {"slot": 1, "time": "06:00", "label": "Morning Kickoff (06:00 AM)"},
    {"slot": 2, "time": "10:00", "label": "Mid-Morning Feature (10:00 AM)"},
    {"slot": 3, "time": "14:00", "label": "Afternoon Deep Dive (02:00 PM)"},
    {"slot": 4, "time": "18:00", "label": "Evening Highlight (06:00 PM)"},
    {"slot": 5, "time": "21:00", "label": "Night Documentary (09:00 PM)"},
]

# Supported Categories
CATEGORIES = [
    "History",
    "Mysterious Events",
    "Real Soldier Stories",
    "Cars and Automobile Stories",
    "Cricket and Sports",
    "Science and Technology",
    "Biography",
    "Interesting Facts",
    "Business Stories",
    "Custom Topics"
]
