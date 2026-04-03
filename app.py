"""
Reddit Automation API
=====================
A Flask-based REST API that automates Reddit interactions using Playwright.

Endpoints:
    POST /create-account   - Automates Reddit account registration
    POST /join-subreddit   - Joins a subreddit using a stored session
    POST /create-post      - Creates a post in a subreddit

Author: Yashraj Singh
"""

from flask import Flask, request, jsonify, render_template
from services.account import create_reddit_account
from services.subreddit import join_subreddit
from services.post import create_post
from utils.logger import get_logger
import os

app = Flask(__name__)
logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    """Serves the Automation Dashboard UI."""
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health_check():
    """Basic health check endpoint."""
    return jsonify({"status": "ok", "message": "Reddit Automation API is running."}), 200


# ──────────────────────────────────────────────
# API 1: Create Reddit Account
# ──────────────────────────────────────────────

@app.route("/create-account", methods=["POST"])
def api_create_account():
    """
    Creates a new Reddit account via browser automation.

    Request Body (JSON):
        username (str): Desired Reddit username
        password (str): Account password (min 8 chars)
        email    (str): Valid email address

    Returns:
        JSON: { success, username, message }

    Example:
        POST /create-account
        {
            "username": "testuser123",
            "password": "SecurePass@1",
            "email": "test@example.com"
        }
    """
    data = request.get_json()

    # Input validation
    required = ["username", "password", "email"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        logger.warning(f"Missing fields: {missing}")
        return jsonify({"success": False, "message": f"Missing fields: {missing}"}), 400

    username = data["username"].strip()
    password = data["password"]
    email    = data["email"].strip()

    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters."}), 400

    logger.info(f"Creating account for username: {username}")
    result = create_reddit_account(username, password, email)
    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code


# ──────────────────────────────────────────────
# API 2: Join Subreddit
# ──────────────────────────────────────────────

@app.route("/join-subreddit", methods=["POST"])
def api_join_subreddit():
    """
    Joins a subreddit using a stored browser session/cookies.

    Request Body (JSON):
        username      (str): Reddit username (used to load saved session)
        subreddit     (str): Subreddit name without 'r/' prefix (e.g. 'startups')

    Returns:
        JSON: { success, joined, subreddit, message }

    Example:
        POST /join-subreddit
        {
            "username": "testuser123",
            "subreddit": "startups"
        }
    """
    data = request.get_json()

    required = ["username", "subreddit"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {missing}"}), 400

    username  = data["username"].strip()
    subreddit = data["subreddit"].strip().lstrip("r/").lstrip("/")

    logger.info(f"User '{username}' joining r/{subreddit}")
    result = join_subreddit(username, subreddit)
    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code


# ──────────────────────────────────────────────
# API 3: Create Post
# ──────────────────────────────────────────────

@app.route("/create-post", methods=["POST"])
def api_create_post():
    """
    Creates a text post in a subreddit using a stored session.

    Request Body (JSON):
        username      (str): Reddit username (used to load saved session)
        subreddit     (str): Target subreddit name (without 'r/')
        title         (str): Post title (max 300 chars)
        content       (str): Post body text

    Returns:
        JSON: { success, post_url, post_id, message }

    Example:
        POST /create-post
        {
            "username": "testuser123",
            "subreddit": "startups",
            "title": "Hello World",
            "content": "This is my first post."
        }
    """
    data = request.get_json()

    required = ["username", "subreddit", "title", "content"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {missing}"}), 400

    username  = data["username"].strip()
    subreddit = data["subreddit"].strip().lstrip("r/").lstrip("/")
    title     = data["title"].strip()
    content   = data["content"].strip()

    if not title:
        return jsonify({"success": False, "message": "Post title cannot be empty."}), 400
    if len(title) > 300:
        return jsonify({"success": False, "message": "Post title exceeds 300 character limit."}), 400
    if not content:
        return jsonify({"success": False, "message": "Post content cannot be empty."}), 400

    logger.info(f"User '{username}' posting to r/{subreddit}: '{title}'")
    result = create_post(username, subreddit, title, content)
    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port,)
