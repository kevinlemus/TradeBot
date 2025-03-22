# DAO/TradeExecutionDAO.py

import requests
from Config import API_KEYS, TRADE_API_CONFIG

class TradeExecutionDAO:
    def __init__(self):
        # Initialize the TradeExecutionDAO with the Schwab API key
        self.api_key = API_KEYS["schwab_app_key"]

    def execute_buy(self, trade_request):
        # Construct the endpoint URL for executing a buy order
        endpoint = TRADE_API_CONFIG["endpoint"].format(account_id=trade_request["account_id"])
        # Get the headers with the API key for authentication
        headers = TRADE_API_CONFIG["headers"](self.api_key)
        # Make a POST request to the API to execute the buy order
        response = requests.post(endpoint, headers=headers, json=trade_request)
        if response.status_code == 200:
            # Return the response as JSON if the request is successful
            return response.json()
        else:
            # Raise an exception if the request fails
            raise Exception(f"Failed to execute buy order: {response.text}")

    def execute_sell(self, trade_request):
        # Construct the endpoint URL for executing a sell order
        endpoint = TRADE_API_CONFIG["endpoint"].format(account_id=trade_request["account_id"])
        # Get the headers with the API key for authentication
        headers = TRADE_API_CONFIG["headers"](self.api_key)
        # Make a POST request to the API to execute the sell order
        response = requests.post(endpoint, headers=headers, json=trade_request)
        if response.status_code == 200:
            # Return the response as JSON if the request is successful
            return response.json()
        else:
            # Raise an exception if the request fails
            raise Exception(f"Failed to execute sell order: {response.text}")
