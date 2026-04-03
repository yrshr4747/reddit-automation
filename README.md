# Reddit Automation API

A production-ready REST API built with **Flask** and **Playwright** that automates Reddit interactions — account creation, subreddit joining, and post creation.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
  - [POST /create-account](#1-post-create-account)
  - [POST /join-subreddit](#2-post-join-subreddit)
  - [POST /create-post](#3-post-create-post)
- [CAPTCHA Handling](#captcha-handling)
- [Spam Detection Avoidance](#spam-detection-avoidance)
- [Session Management](#session-management)
- [Logging](#logging)
- [Docker Deployment](#docker-deployment)
- [Deploying to Render](#deploying-to-render)
- [Bonus Features Implemented](#bonus-features-implemented)

---

## Project Structure

```
reddit-automation/
├── app.py                  # Flask app — all 3 API route handlers
├── services/
│   ├── account.py          # Reddit account creation logic
│   ├── subreddit.py        # Subreddit joining logic
│   └── post.py             # Post creation logic
├── utils/
│   ├── browser.py          # Shared Playwright browser setup + session management
│   └── logger.py           # Centralized logging configuration
├── sessions/               # Auto-created — stores per-user cookie sessions
├── logs/                   # Auto-created — rotating log files
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| API Framework | Flask 3.0 | Lightweight, fast to set up, Python-native |
| Browser Automation | Playwright | Modern, async-capable, better than Selenium for headless work |
| Production Server | Gunicorn | WSGI server for production Flask deployment |
| Containerisation | Docker | Ensures consistent environment across machines |
| Logging | Python logging + RotatingFileHandler | Persistent, rotating log files |

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/reddit-automation.git
cd reddit-automation

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binary
playwright install chromium
playwright install-deps chromium
```

---

## Running the API

### Development

```bash
python app.py
```

API will be available at: `http://localhost:5000`

### Production (Gunicorn)

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
```

---

## API Endpoints

### 1. POST `/create-account`

Creates a new Reddit account via browser automation.

**Request Body:**

```json
{
  "username": "testuser123",
  "password": "SecurePass@1",
  "email": "test@example.com"
}
```

**Success Response:**

```json
{
  "success": true,
  "username": "testuser123",
  "message": "Account created successfully."
}
```

**Failure Response:**

```json
{
  "success": false,
  "username": "testuser123",
  "message": "CAPTCHA detected. Integrate 2captcha API to handle."
}
```

**Validation Rules:**
- All fields are required
- Password must be at least 8 characters

---

### 2. POST `/join-subreddit`

Joins a subreddit using a stored browser session.

**Request Body:**

```json
{
  "username": "testuser123",
  "subreddit": "startups"
}
```

**Success Response:**

```json
{
  "success": true,
  "joined": true,
  "subreddit": "startups",
  "message": "Successfully joined r/startups."
}
```

**Handles these subreddit states:**
- ✅ Public — joins normally
- 🔒 Private — returns descriptive error
- ⛔ Banned — returns descriptive error
- ❌ Non-existent — returns descriptive error
- ✅ Already joined — returns success without re-joining

---

### 3. POST `/create-post`

Creates a text post in a subreddit using a stored session.

**Request Body:**

```json
{
  "username": "testuser123",
  "subreddit": "startups",
  "title": "Hello from the API",
  "content": "This post was created programmatically using Flask + Playwright."
}
```

**Success Response:**

```json
{
  "success": true,
  "post_url": "https://www.reddit.com/r/startups/comments/abc123/hello_from_the_api/",
  "post_id": "abc123",
  "message": "Post created successfully."
}
```

**Validation Rules:**
- All fields are required
- Title cannot be empty or exceed 300 characters
- Content cannot be empty

---

## CAPTCHA Handling

Reddit uses **reCAPTCHA v2/v3** on its signup page.

### Current Approach (Detection Avoidance)

1. **Realistic User-Agent** — mimics Chrome 122 on Windows 10
2. **Override `navigator.webdriver`** — hides Playwright's automation flag
3. **Randomized delays** — human-like timing between interactions (1–4 seconds)
4. **Realistic viewport** — 1280×800 browser window
5. **Custom HTTP headers** — Accept-Language and Accept headers matching real browsers

### Production CAPTCHA Solving

For full CAPTCHA solving in production, integrate **2captcha**:

```python
# Example integration sketch
import requests

API_KEY = "YOUR_2CAPTCHA_KEY"
SITE_KEY = "REDDIT_RECAPTCHA_SITE_KEY"
PAGE_URL = "https://www.reddit.com/register/"

# Submit CAPTCHA task
response = requests.post("https://2captcha.com/in.php", data={
    "key": API_KEY,
    "method": "userrecaptcha",
    "googlekey": SITE_KEY,
    "pageurl": PAGE_URL,
    "json": 1
})
task_id = response.json()["request"]

# Poll for result
import time
time.sleep(20)
result = requests.get(f"https://2captcha.com/res.php?key={API_KEY}&action=get&id={task_id}&json=1")
captcha_token = result.json()["request"]

# Inject token into page
page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_token}"')
```

---

## Spam Detection Avoidance

The API implements several measures to simulate human behaviour:

| Technique | Implementation |
|-----------|----------------|
| **Random delays** | `human_delay(min, max)` adds 0.5–4s random waits between actions |
| **Simulated typing** | `page.type(text, delay=50)` — types character by character |
| **Realistic headers** | Chrome-like User-Agent, Accept-Language headers |
| **Webdriver hiding** | `navigator.webdriver` overridden to `undefined` |
| **Session reuse** | Cookies saved and reloaded — avoids repeated logins |

---

## Session Management

After account creation or first login, browser cookies are saved to:

```
sessions/<username>.json
```

These cookies are loaded for subsequent API calls (`/join-subreddit`, `/create-post`), avoiding the need to re-login and making requests appear as an organic returning user.

---

## Logging

All actions are logged to both console and `logs/app.log`.

Log format:
```
2026-04-03 14:22:01 | INFO | services.account | Creating account for username: testuser123
2026-04-03 14:22:05 | INFO | services.account | Account created successfully: testuser123
```

Log files rotate at 5MB with 3 backups kept.

---

## Docker Deployment

### Build and Run Locally

```bash
# Build image
docker build -t reddit-automation .

# Run container
docker run -p 5000:5000 reddit-automation
```

### Test

```bash
curl -X POST http://localhost:5000/create-account \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "Pass@1234", "email": "test@example.com"}'
```

---

## Deploying to Render

1. Push your code to a GitHub repository
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set the following:

| Setting | Value |
|---------|-------|
| **Runtime** | Docker |
| **Build Command** | *(auto-detected from Dockerfile)* |
| **Start Command** | *(auto-detected from Dockerfile)* |
| **Port** | 5000 |

5. Click **Deploy** — Render gives you a live URL like:
   ```
   https://reddit-automation.onrender.com
   ```

> **Note:** Free tier on Render spins down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds to wake up.

---

## Bonus Features Implemented

- ✅ **Human-like delays** — randomized waits between every interaction
- ✅ **Logging system** — rotating file + console logs with timestamps
- ✅ **Docker setup** — full Dockerfile with Chromium dependencies
- ✅ **Session persistence** — cookies saved per user to disk
- ✅ **Retry-ready architecture** — each service is isolated and independently retryable
- ✅ **Graceful error handling** — all edge cases return descriptive JSON responses
