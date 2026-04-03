import os
import json
from playwright.sync_api import sync_playwright

# Ensures the sessions directory exists
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)


def capture_session(username):
    """
    Opens a browser for manual login and saves the authenticated state.
    Uses storage_state to capture both cookies and local storage for better persistence.
    """
    with sync_playwright() as p:
        # Launch a visible browser so you can interact with it
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print(f"🚀 Opening Reddit login for user: {username}")
        page.goto("https://www.reddit.com/login")

        print("\n🛑 ACTION REQUIRED:")
        print("1. Manually enter your username and password in the browser window.")
        print("2. Solve any CAPTCHAs that appear.")
        print("3. Once you see your Home Feed or the 'Create' button, the script will auto-save.")

        try:
            # FIX: We wait for the 'Create' button to appear instead of a specific URL.
            # This is the most reliable way to detect you are actually logged in.
            page.wait_for_selector('a[href="/submit"], [aria-label="Create Post"]', timeout=0)

            # Give Reddit 2 seconds to finish loading background session data
            print("⏳ Finalizing session data...")
            page.wait_for_timeout(2000)

            # Save the full authentication state (cookies + local storage)
            session_path = os.path.join(SESSION_DIR, f"{username}.json")
            context.storage_state(path=session_path)

            print(f"\n✨ SUCCESS! Session saved to: {session_path}")
            print("You can now close the browser (if it doesn't close automatically).")

        except Exception as e:
            print(f"💥 Error during session capture: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    # IMPORTANT: Ensure this matches the 'username' you use in your curl commands
    target_username = "ath_Test_Bot"
    capture_session(target_username)