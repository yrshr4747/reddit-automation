"""
utils/browser.py
================
Shared Playwright browser setup and session management.

- Launches a Chromium browser in headless mode
- Saves and loads session cookies per user
- Adds human-like headers and user-agent to avoid detection
"""

import os
import json
import asyncio
import random
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# Realistic browser headers to reduce bot detection
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def human_delay(min_sec=1.0, max_sec=3.0):
    """
    Adds a randomized delay to simulate human interaction speed.
    Prevents triggering rate limits or bot detection.

    Args:
        min_sec (float): Minimum wait time in seconds
        max_sec (float): Maximum wait time in seconds
    """
    time.sleep(random.uniform(min_sec, max_sec))


def get_browser_context(playwright, username=None):
    # CRITICAL: headless must be True for Render
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage", # Necessary for Docker memory limits
            "--single-process",        # Forces everything into one process to save RAM
            "--no-zygote",
            "--disable-gpu"
        ]
    )

    session_file = os.path.join(SESSION_DIR, f"{username}.json") if username else None
    storage_state = session_file if (session_file and os.path.exists(session_file)) else None

    context = browser.new_context(
        storage_state=storage_state,
        user_agent=DEFAULT_HEADERS["User-Agent"]
    )

    page = context.new_page()
    return browser, context, page


def save_session(context, username):
    """
    Saves the current browser session cookies to disk for reuse.

    Args:
        context: Playwright browser context
        username (str): Username key for the session file
    """
    cookies = context.cookies()
    session_file = os.path.join(SESSION_DIR, f"{username}.json")
    with open(session_file, "w") as f:
        json.dump(cookies, f)


def session_exists(username):
    """
    Checks if a saved session exists for a given username.

    Args:
        username (str): Reddit username

    Returns:
        bool: True if session file exists
    """
    session_file = os.path.join(SESSION_DIR, f"{username}.json")
    return os.path.exists(session_file)
