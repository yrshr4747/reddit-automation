import requests
import json

# We'll use a fresh, random username for this test
test_user = "yash_test_77"
test_domain = "1secmail.com"
url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={test_user}&domain={test_domain}"

# These headers are the "key" to bypassing the 403 error
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

print(f"🚀 Testing connection to 1secmail for {test_user}@{test_domain}...")

try:
    # We send the request with the headers
    response = requests.get(url, headers=headers, timeout=15)

    print(f"📡 Status Code: {response.status_code}")

    if response.status_code == 200:
        print("✅ SUCCESS: The API is accessible!")
        # If the inbox is empty, it returns an empty list []
        print(f"📩 Inbox Data: {response.json()}")
    else:
        print("❌ FAILED: Still getting blocked.")
        print(f"📄 Server Message: {response.text[:200]}")  # Only print the first 200 chars

except Exception as e:
    print(f"💥 Network Error: {e}")