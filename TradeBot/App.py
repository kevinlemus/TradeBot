from flask import Flask, request, jsonify, render_template_string
import requests
import logging
import os
import urllib.parse
from Config import API_KEYS, OAUTH_CONFIG

# Configure logging to write to the unified app.log file
log_file_path = r"C:\Users\kevin\vscode-projects\trade-bot\TradeBot\Util\logs\app.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
console_handler = logging.StreamHandler()
log_format = "%(asctime)s %(levelname)s: %(message)s"
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)

logging.info("Starting App.py script with unified logging")

# Initialize Flask app
app = Flask(__name__)


@app.route("/")
def health_check():
    """Simple route to check if the server is running"""
    logging.info("Health check endpoint accessed.")
    return "<h1>Server is running!</h1>"


@app.route("/callback")
def callback():
    """Handle the OAuth callback and exchange the code for tokens"""
    try:
        logging.debug("Callback endpoint reached")

        # Get the authorization code from the query string
        auth_code = request.args.get("code")
        if not auth_code:
            logging.error("Authorization code not found in the callback request.")
            return (
                render_template_string("<h1>Error: Authorization code not found!</h1>"),
                400,
            )

        logging.debug(f"Raw authorization code received: {auth_code}")

        # Decode the authorization code (if necessary)
        auth_code = urllib.parse.unquote(auth_code)
        logging.debug(f"Decoded authorization code: {auth_code}")

        # Exchange the authorization code for tokens
        token_url = OAUTH_CONFIG["token_url"]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "client_id": API_KEYS["schwab_app_key_market"],
            "client_secret": API_KEYS["schwab_client_secret"],
            "redirect_uri": OAUTH_CONFIG["redirect_uri"],
            "code": auth_code,
        }

        logging.debug(f"Requesting tokens from token URL: {token_url}")
        logging.debug(f"Payload: {data}")

        # Make the POST request to retrieve tokens
        response = requests.post(token_url, headers=headers, data=data)
        logging.debug(f"Token response status code: {response.status_code}")
        logging.debug(f"Token response text: {response.text}")

        if response.status_code == 200:
            tokens = response.json()
            logging.info(f"Tokens successfully received: {tokens}")
            return jsonify(tokens), 200
        else:
            error_message = response.text
            logging.error(f"Error retrieving tokens: {error_message}")
            return (
                render_template_string(f"<h1>Error: {error_message}</h1>"),
                response.status_code,
            )

    except Exception as e:
        logging.exception("An exception occurred while processing the callback.")
        return render_template_string(f"<h1>Exception: {str(e)}</h1>"), 500


if __name__ == "__main__":
    logging.info("Starting Flask server...")
    app.run(port=5000, debug=True, ssl_context=("cert.pem", "key.pem"))
