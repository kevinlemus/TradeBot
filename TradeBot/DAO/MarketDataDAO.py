import requests
import time
import logging
from TradeBot.Config import API_KEYS, MARKET_DATA_API_CONFIG
from TradeBot.Auth.OAuth import OAuth


class MarketDataDAO:
    def __init__(self):
        # Initialize the MarketDataDAO with the Schwab App Key and OAuth
        self.app_key = API_KEYS["schwab_app_key"]
        self.oauth = OAuth()  # Use OAuth to manage token retrieval

    def get_access_token(self):
        """
        Retrieve the current access token. Automatically refresh if needed.
        """
        if not self.oauth.access_token:
            logging.warning("Access token is missing. Attempting to refresh...")
            self.oauth.refresh_access_token()

        logging.info("Access token retrieved successfully.")
        return self.oauth.access_token

    def get_instruments(self, params=None, retries=3, delay=2):
        """
        Fetch instruments with specific filtering parameters using the Schwab API.
        """
        endpoint = f"{MARKET_DATA_API_CONFIG['base_url']}/instruments"
        headers = {"Authorization": f"Bearer {self.get_access_token()}"}

        for attempt in range(retries):
            try:
                logging.debug(
                    f"Requesting instruments from: {endpoint} (Attempt {attempt + 1})"
                )
                response = requests.get(endpoint, headers=headers, params=params)
                response.raise_for_status()
                logging.debug(f"Response Content: {response.json()}")
                return response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch instruments: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise Exception(
                        f"Failed to fetch instruments after {retries} attempts"

                    )
