import os
import sys
import logging
import requests

# Dynamically adjust sys.path to ensure Python can find the `TradeBot` module
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from TradeBot.Config import API_KEYS, OAUTH_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s"
)

# Direct call to token endpoint
token_url = OAUTH_CONFIG["token_url"]
payload = {
    "grant_type": "refresh_token",
    "refresh_token": "<your-refresh-token>",  # Replace with your refresh token
    "client_id": API_KEYS["schwab_app_key"],
    "client_secret": API_KEYS["schwab_client_secret"],
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}

try:
    logging.info(f"Testing token refresh with payload: {payload}")
    response = requests.post(token_url, data=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
except Exception as e:
    print(f"Error: {e}")
