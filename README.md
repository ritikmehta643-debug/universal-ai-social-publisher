# UNIVERSAL AI SOCIAL PUBLISHER

> **Autonomous AI-Powered Facebook Page Publishing Platform**
> Fully automated documentary generation, photorealistic image creation, and multi-slot fixed-time publishing via the official Meta Graph API.

---

## 🌟 Key Features

1. **Universal AI Provider Integration**:
   - Native adapters for **Google Gemini**, **OpenAI**, **Anthropic Claude**, **Groq**, **OpenRouter**, **Hugging Face**, and **Custom OpenAI-compatible endpoints** (e.g. Ollama, vLLM).
   - Dynamic failover: automatically falls back to secondary provider if primary fails or rate-limits.
   - Zero key leakage: API keys are masked and never exposed to the frontend or logs.

2. **AI Content & Storytelling Engine**:
   - Deep documentary storytelling with verified historical facts, emotional hooks, and compelling narratives.
   - Dual-language support: **English**, **Hindi (हिंदी)**, and **Hinglish**.
   - 10 pre-configured content genres: History, Mysterious Events, Soldier Heroics, Supercars & Auto, Cricket & Sports, Science & Tech, Biographies, Facts, and Business.
   - 30-day duplicate avoidance window and topic exhaustion protection.

3. **Photorealistic Image Engine**:
   - Support for **Google Imagen 3**, **OpenAI DALL-E 3**, **Hugging Face FLUX.1**, and custom image endpoints.
   - Automatic documentary prompt enhancement (8k resolution, historical lighting, camera lens specifications, negative prompt filters).
   - Graceful fallback: marks post in pending status if image engine is unavailable instead of crashing.

4. **Official Meta Graph API Integration**:
   - Official Facebook Page integration with permission verification (`pages_show_list`, `pages_read_engagement`, `pages_manage_posts`).
   - One-click Page Auto-Discovery from User Access Tokens.
   - Binary multipart photo upload and long-form caption support.
   - Post ID tracking and error diagnostics.

5. **Fixed-Time Background Scheduler**:
   - **5 Daily Publishing Slots** (Default: 06:00 AM, 10:00 AM, 02:00 PM, 06:00 PM, 09:00 PM).
   - Timezone customizable (Default: `Asia/Kolkata`).
   - Idempotency guarantees: unique job IDs prevent duplicate publishing.
   - Background thread execution with persistent SQLite WAL database.

---

## 📁 Repository Structure

```
universal-ai-publisher/
├── backend/
│   ├── app/
│   │   ├── api/             # REST Routers (dashboard, providers, facebook, schedules, posts)
│   │   ├── models/          # Data schemas
│   │   ├── services/
│   │   │   ├── ai/          # Universal AI Adapters (Gemini, OpenAI, Claude, Groq, HF, Custom)
│   │   │   ├── image/       # Image Engine Adapters (Imagen 3, DALL-E 3, FLUX, Custom)
│   │   │   ├── facebook/    # Meta Graph API Client
│   │   │   ├── content_engine.py # Topic Discovery & Caption Assembler
│   │   │   └── scheduler.py # Background Persistent Scheduler
│   │   ├── config.py        # Central configuration
│   │   ├── database.py      # SQLite WAL connection & schema migrations
│   │   └── main.py          # FastAPI application
│   ├── tests/               # 15 automated unit tests
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Backend entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/      # UI Modules (Dashboard, Providers, Facebook, Scheduler, Templates)
│   │   ├── services/api.js  # REST API client
│   │   ├── App.jsx          # Main React Application
│   │   └── index.css        # Modern glassmorphism & Tailwind design
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── setup_guide.md           # Step-by-step Meta & Cloud Deployment Guide
├── .env.example             # Environment template
└── start.sh                 # Launcher script
```

---

## 🚀 Quick Start Guide

### Step 1: Backend Installation
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Unit Tests
```bash
python3 tests/run_tests.py
```

### Step 3: Start Server
```bash
python3 run.py
# Backend starts at http://0.0.0.0:8000
```

### Step 4: Frontend Development
```bash
cd ../frontend
pnpm install
pnpm dev
# Frontend runs at http://localhost:5173 with proxy to backend
```

---

## 🔒 Security Best Practices
- **API Keys**: Never shared or printed in plaintext.
- **Tokens**: Stored in a local database with file permission restrictions.
- **Meta Policy**: Uses only official Graph API endpoints; does not perform unauthorized scraping.
