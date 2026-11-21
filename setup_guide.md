# Universal AI Social Publisher - Setup & Integration Guide

## 1. System Requirements & Architecture
Universal AI Social Publisher is architected to operate on any Linux environment, including **Android (Termux)**, cloud VPS, and local workstations.

- **Backend**: Python 3.10+ (FastAPI, SQLite WAL, Persistent Background Thread Scheduler)
- **Frontend**: React 18, Tailwind CSS, Vite
- **Integrations**: Official Meta Graph API (v21.0), Multi-Provider AI Engine (Gemini, OpenAI, Claude, Groq, OpenRouter, Hugging Face)

---

## 2. Meta Facebook Graph API Setup Guide

To enable 100% automated posting to your Facebook Page without manual intervention, Meta requires specific permissions.

### Step 1: Create a Meta Developer App
1. Go to [developers.facebook.com](https://developers.facebook.com/) and log in with your Facebook account.
2. Click **My Apps** → **Create App**.
3. Select **Other** as the use case, then choose **Business** as the app type.
4. Enter an App Name (e.g., `Universal Auto Publisher`) and complete creation.

### Step 2: Configure Permissions
Under **Graph API Explorer** (`developers.facebook.com/tools/explorer`):
1. In the **User or Page** dropdown, select **User Token**.
2. Under **Permissions**, add:
   - `pages_show_list` (lists pages you manage)
   - `pages_read_engagement` (verifies page engagement)
   - `pages_manage_posts` (allows publishing to page feed and photos)
3. Click **Generate Access Token** and approve the Facebook dialogue.

### Step 3: Obtain a Permanent Page Access Token
A standard user token expires in 1-2 hours. To generate a **Never-Expiring Page Token**:
1. Exchange short-lived token for long-lived user token (60 days) via:
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
   ```
2. Call `/me/accounts?access_token={long-lived-user-token}`.
3. Copy the `access_token` returned for your target Page.
4. **Paste the Page ID and Page Access Token into the Facebook Settings tab** in the publisher dashboard.
5. Click **Validate & Save Connection**.

---

## 3. AI Providers & Free-Tier Disclosures

| AI Provider | Free Tier Available? | Rate Limits & Notes |
| :--- | :--- | :--- |
| **Google Gemini** | ✅ **Yes (Generous)** | 15 RPM, 1,500 requests/day for Gemini 2.5 Flash / Flash Lite. Best default choice. |
| **Groq Cloud** | ✅ **Yes (High Speed)** | Extremely fast Llama 3.3 70B inference with generous free daily token allowances. |
| **OpenRouter** | ✅ **Yes** | Aggregates 100+ models. Several free models (e.g., `:free` suffix) available without cost. |
| **Hugging Face** | ✅ **Yes** | Serverless Inference API is free for supported models with rate throttling. |
| **OpenAI** | ❌ Paid / Credit | Requires paid credit balance. DALL-E 3 costs ~$0.04/image. |
| **Anthropic Claude** | ❌ Paid / Credit | Requires API credits. Exceptional narrative depth. |

---

## 4. Running 24/7 on Android (Termux)

To keep automated posting running 24/7 even when your screen is turned off:
1. Prevent Android from sleeping Termux:
   ```bash
   termux-wake-lock
   ```
2. Disable Android battery optimization for the AntiGem / Termux app in Android Settings → Apps → Battery → Unrestricted.
3. Start the application:
   ```bash
   ./start.sh
   ```

---

## 5. Free Cloud Hosting Options

If you prefer cloud hosting so your phone doesn't run the background worker:
1. **Render.com / Railway.app**:
   - Push repository to GitHub.
   - Deploy as a Web Service running `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   - SQLite database is persisted or connect to a free PostgreSQL database.
2. **Oracle Cloud Free Tier**:
   - Free Always-Free Ampere VM (4 OCPUs, 24 GB RAM).
   - Run via Docker or systemd service for 100% free permanent uptime.
