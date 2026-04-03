"""
services/subreddit.py
=====================
Handles joining a subreddit using a stored browser session.

Flow:
    1. Load saved session cookies for the given username
    2. Navigate to the subreddit page
    3. Detect subreddit type (public / private / restricted / banned)
    4. Click the Join button if available
    5. Confirm join status
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from utils.browser import get_browser_context, session_exists, human_delay
from utils.logger import get_logger

logger = get_logger(__name__)

REDDIT_BASE = "https://www.reddit.com"


def join_subreddit(username: str, subreddit: str) -> dict:
    """
    Joins a subreddit using the user's saved browser session.

    Args:
        username  (str): Reddit username (used to load saved session)
        subreddit (str): Subreddit name without 'r/' prefix

    Returns:
        dict: {
            success   (bool): Whether the operation succeeded,
            joined    (bool): Whether the subreddit was joined,
            subreddit (str):  Subreddit name,
            message   (str):  Status or error description
        }
    """
    logger.info(f"Attempting to join r/{subreddit} as {username}")

    # Check session exists
    if not session_exists(username):
        logger.warning(f"No saved session found for: {username}")
        return {
            "success": False,
            "joined": False,
            "subreddit": subreddit,
            "message": f"No saved session for '{username}'. Please create an account first."
        }

    subreddit_url = f"{REDDIT_BASE}/r/{subreddit}/"

    try:
        with sync_playwright() as p:
            browser, context, page = get_browser_context(p, username=username)

            try:
                # Navigate to subreddit
                logger.info(f"Navigating to {subreddit_url}")
                page.goto(subreddit_url, wait_until="networkidle", timeout=30000)
                human_delay(2, 3)

                page_content = page.content().lower()

                # Handle private subreddit
                if "this community is private" in page_content or \
                   "you must be invited" in page_content:
                    logger.warning(f"r/{subreddit} is private.")
                    return {
                        "success": True,
                        "joined": False,
                        "subreddit": subreddit,
                        "message": f"r/{subreddit} is a private community. Cannot join without an invitation."
                    }

                # Handle banned subreddit
                if "this community has been banned" in page_content or \
                   "banned" in page_content:
                    logger.warning(f"r/{subreddit} is banned.")
                    return {
                        "success": True,
                        "joined": False,
                        "subreddit": subreddit,
                        "message": f"r/{subreddit} has been banned."
                    }

                # Handle non-existent subreddit
                if "page not found" in page_content or \
                   "there's nothing here" in page_content:
                    return {
                        "success": False,
                        "joined": False,
                        "subreddit": subreddit,
                        "message": f"r/{subreddit} does not exist."
                    }

                # Check if already joined
                joined_btn = page.locator('button:has-text("Joined"), button:has-text("Leave")')
                if joined_btn.count() > 0:
                    logger.info(f"Already a member of r/{subreddit}")
                    return {
                        "success": True,
                        "joined": True,
                        "subreddit": subreddit,
                        "message": f"Already a member of r/{subreddit}."
                    }

                # Click the Join button
                join_btn = page.locator('button:has-text("Join")')
                join_btn.wait_for(state="visible", timeout=10000)
                human_delay(1, 2)
                join_btn.click()
                human_delay(2, 3)

                # Verify join succeeded
                joined_confirm = page.locator('button:has-text("Joined"), button:has-text("Leave")')
                if joined_confirm.count() > 0:
                    logger.info(f"Successfully joined r/{subreddit}")
                    return {
                        "success": True,
                        "joined": True,
                        "subreddit": subreddit,
                        "message": f"Successfully joined r/{subreddit}."
                    }

                return {
                    "success": False,
                    "joined": False,
                    "subreddit": subreddit,
                    "message": "Join button clicked but confirmation not detected."
                }

            except PlaywrightTimeout as e:
                logger.error(f"Timeout while joining r/{subreddit}: {e}")
                return {
                    "success": False,
                    "joined": False,
                    "subreddit": subreddit,
                    "message": f"Timeout: {str(e)}"
                }

            finally:
                browser.close()

    except Exception as e:
        logger.error(f"Unexpected error joining r/{subreddit}: {e}")
        return {
            "success": False,
            "joined": False,
            "subreddit": subreddit,
            "message": str(e)
        }
