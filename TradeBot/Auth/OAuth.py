import logging
import sys
import requests
import base64
import os
import json
import urllib.parse

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from TradeBot.Config import API_KEYS, OAUTH_CONFIG


class OAuth:
    def __init__(self):
        self.tokens_file = os.path.join(current_dir, "tokens_market.json")
        self.access_token = None
        self.refresh_token = None
        self.load_tokens()

    def base64_encode_credentials(self):
        client_id = API_KEYS["schwab_app_key"]
        client_secret = API_KEYS["schwab_client_secret"]
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return encoded_credentials

    def load_tokens(self):
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, "r") as file:
                tokens = json.load(file)
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                logging.info("Tokens loaded successfully.")
        else:
            logging.warning("No tokens file found. Run authorization flow to generate tokens.")

    def save_tokens(self, access_token, refresh_token):
        tokens = {"access_token": access_token, "refresh_token": refresh_token}
        with open(self.tokens_file, "w") as file:
            json.dump(tokens, file)
        logging.info("Tokens saved successfully.")

    def get_access_token(self, authorization_code):
        decoded_code = urllib.parse.unquote(authorization_code)
        token_url = OAUTH_CONFIG["token_url"]
        payload = {
            "grant_type": "authorization_code",
            "code": decoded_code,
            "redirect_uri": OAUTH_CONFIG["redirect_uri"],
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.base64_encode_credentials()}",
        }
        logging.debug(f"Requesting access token with payload: {payload}")
        response = requests.post(token_url, data=payload, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.save_tokens(self.access_token, self.refresh_token)
            logging.info("Access token and refresh token obtained successfully.")
            return tokens
        else:
            logging.error(f"Failed to obtain access token. Response: {response.text}")
            raise Exception("Failed to obtain access token")

    def refresh_access_token(self):
        if not self.refresh_token:
            logging.error("No refresh token available. Run authorization flow to generate tokens.")
            raise Exception("No refresh token available.")

        decoded_refresh_token = urllib.parse.unquote(self.refresh_token)
        token_url = OAUTH_CONFIG["token_url"]
        payload = {"grant_type": "refresh_token", "refresh_token": decoded_refresh_token}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.base64_encode_credentials()}",
        }
        logging.debug(f"Refreshing access token with payload: {payload}")
        response = requests.post(token_url, data=payload, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            self.save_tokens(self.access_token, self.refresh_token)
            logging.info(f"New Access Token: {self.access_token}")
            logging.info(f"New Refresh Token: {self.refresh_token}")
            return tokens
        else:
            logging.error(f"Failed to refresh access token. Response: {response.text}")
            raise Exception("Failed to refresh access token")
