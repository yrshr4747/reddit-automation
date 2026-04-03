"""
services/post.py
================
Handles creating a text post in a subreddit using a stored session.

Flow:
    1. Load saved session cookies for the given username
    2. Navigate to the subreddit's submit page
    3. Fill in post title and content
    4. Submit the post
    5. Return the post URL and ID

Spam Detection Avoidance Strategy:
    - Use randomized delays between interactions (human-like timing)
    - Realistic browser headers and user-agent
    - Avoid posting identical content repeatedly
    - Post from aged, active accounts where possible
    - Respect subreddit posting rules and rate limits
"""

import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from utils.browser import get_browser_context, session_exists, human_delay
from utils.logger import get_logger

logger = get_logger(__name__)

REDDIT_BASE = "https://www.reddit.com"


def create_post(username: str, subreddit: str, title: str, content: str) -> dict:
    """
    Creates a text post in a subreddit using the user's saved session.

    Args:
        username  (str): Reddit username (used to load saved session)
        subreddit (str): Target subreddit name (without r/)
        title     (str): Post title (max 300 characters)
        content   (str): Post body text

    Returns:
        dict: {
            success  (bool): Whether the post was created,
            post_url (str):  URL of the created post,
            post_id  (str):  Reddit post ID,
            message  (str):  Status or error description
        }
    """
    logger.info(f"Creating post in r/{subreddit} as {username}")

    # Check session exists
    if not session_exists(username):
        logger.warning(f"No saved session found for: {username}")
        return {
            "success": False,
            "post_url": None,
            "post_id": None,
            "message": f"No saved session for '{username}'. Please create an account first."
        }

    submit_url = f"{REDDIT_BASE}/r/{subreddit}/submit"

    try:
        with sync_playwright() as p:
            browser, context, page = get_browser_context(p, username=username)

            try:
                # Navigate to submit page
                logger.info(f"Navigating to submit page: {submit_url}")
                page.goto(submit_url, wait_until="networkidle", timeout=30000)
                human_delay(2, 4)

                page_content = page.content().lower()

                # Handle restricted posting (karma/age requirements)
                if "you don't have permission" in page_content or \
                   "not allowed to post" in page_content:
                    return {
                        "success": False,
                        "post_url": None,
                        "post_id": None,
                        "message": f"Permission denied to post in r/{subreddit}. Account may lack karma or age requirement."
                    }

                # Ensure "Text" post tab is selected
                text_tab = page.locator('[data-testid="post-content-type-text"], button:has-text("Text")')
                if text_tab.count() > 0:
                    text_tab.first.click()
                    human_delay(1, 2)

                # Fill in the title
                logger.info("Filling post title...")
                title_input = page.locator('textarea[placeholder*="Title"], input[placeholder*="Title"]').first
                title_input.wait_for(state="visible", timeout=10000)
                title_input.click()
                human_delay(0.5, 1.5)
                title_input.fill(title)
                human_delay(1, 2)

                # Fill in the content body
                logger.info("Filling post content...")
                content_area = page.locator(
                    '.public-DraftEditor-content, '
                    'div[contenteditable="true"], '
                    'textarea[placeholder*="text"]'
                ).first
                content_area.wait_for(state="visible", timeout=10000)
                content_area.click()
                human_delay(0.5, 1.5)
                content_area.type(content, delay=50)  # Simulate typing speed
                human_delay(1, 2)

                # Submit the post
                logger.info("Submitting post...")
                submit_btn = page.locator('button:has-text("Post"), button[type="submit"]:has-text("Post")').last
                submit_btn.wait_for(state="visible", timeout=10000)
                submit_btn.click()

                # Wait for redirect to the post page
                page.wait_for_url(re.compile(r"reddit\.com/r/.+/comments/"), timeout=20000)
                human_delay(2, 3)

                # Extract post URL and ID
                post_url = page.url
                post_id_match = re.search(r"/comments/([a-z0-9]+)/", post_url)
                post_id = post_id_match.group(1) if post_id_match else "unknown"

                logger.info(f"Post created: {post_url}")
                return {
                    "success": True,
                    "post_url": post_url,
                    "post_id": post_id,
                    "message": "Post created successfully."
                }

            except PlaywrightTimeout as e:
                logger.error(f"Timeout while creating post: {e}")
                return {
                    "success": False,
                    "post_url": None,
                    "post_id": None,
                    "message": f"Timeout: {str(e)}"
                }

            finally:
                browser.close()

    except Exception as e:
        logger.error(f"Unexpected error creating post: {e}")
        return {
            "success": False,
            "post_url": None,
            "post_id": None,
            "message": str(e)
        }
