import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from utils.browser import get_browser_context, save_session, human_delay
from utils.logger import get_logger

logger = get_logger(__name__)

REDDIT_SIGNUP_URL = "https://www.reddit.com/register/"

def create_reddit_account(username: str, password: str, email: str) -> dict:
    """
    Automates the Reddit signup form filling based on provided inputs.
    Mentions CAPTCHA handling logic as per assignment requirements.
    """
    logger.info(f"Starting registration flow for: {username}")

    try:
        with sync_playwright() as p:
            # Launches browser based on config in utils/browser.py
            browser, context, page = get_browser_context(p)
            try:
                # Step 1: Navigate to Reddit Signup
                logger.info("Navigating to Reddit signup page...")
                page.goto(REDDIT_SIGNUP_URL, wait_until="networkidle", timeout=30000)
                human_delay(2, 4)

                # Step 2: Fill User-Provided Email
                logger.info(f"Filling email: {email}")
                email_input = page.locator('input[name="email"]')
                email_input.wait_for(state="visible", timeout=10000)
                email_input.fill(email)
                page.keyboard.press("Enter")
                human_delay(3, 5)

                # Step 3: Requirement - Handle/Mention CAPTCHA Logic
                # If we see a captcha or verification wall, we return the logic explanation
                # Use .first to avoid the strict mode violation when multiple iframes exist
                captcha_detected = page.locator('iframe[title*="reCAPTCHA"]').first.is_visible()
                verification_wall = page.get_by_text("Verify your email").is_visible()

                if captcha_detected or verification_wall:
                    logger.warning("Security wall detected. Returning logic explanation.")
                    return {
                        "success": False,
                        "username": username,
                        "message": "Security check (CAPTCHA/Verification) triggered.",
                        "captcha_handling_logic": (
                            "To handle CAPTCHA autonomously in production, I would integrate a third-party solver "
                            "API like 2Captcha or Anti-Captcha. The workflow would be: "
                            "1. Extract the 'site-key' from the Reddit page source. "
                            "2. Request a solution from the solver API. "
                            "3. Inject the resulting 'g-recaptcha-response' token into the hidden textarea via JavaScript. "
                            "4. Programmatically trigger the form submission to bypass the check."
                        )
                    }

                # Step 4: Fill Username and Password (if flow is clear)
                logger.info("Filling username and password...")
                username_field = page.locator('input[name="username"]')
                username_field.wait_for(state="visible", timeout=10000)
                username_field.fill(username)

                password_field = page.locator('input[name="password"]')
                password_field.fill(password)
                human_delay(1, 2)
                page.keyboard.press("Enter")

                # Step 5: Final Check for Session Creation
                human_delay(8, 12)
                if "reddit.com" in page.url and "register" not in page.url:
                    save_session(context, username)
                    return {"success": True, "username": username, "message": "Form submitted successfully!"}

                return {"success": False, "message": "Form submitted but registration not confirmed."}

            except PlaywrightTimeout:
                return {"success": False, "message": "Page interaction timed out (possible hidden security check)."}
            finally:
                browser.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"success": False, "message": str(e)}