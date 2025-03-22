import logging
import requests
import pandas as pd
from Config import EOD_API_KEY

class EODDataDAO:
    def __init__(self):
        self.api_key = EOD_API_KEY

    def get_intraday_data(self, ticker, exchange, interval="1h"):
        logging.info(f"Fetching intraday data for {ticker} on exchange {exchange} with interval {interval}")
        endpoint = f"https://eodhd.com/api/intraday/{ticker}.{exchange}?api_token={self.api_key}&interval={interval}"
        response = requests.get(endpoint)
        logging.debug(f"API Response: {response.text}")
        if response.status_code == 200:
            try:
                if response.text.strip() == "":
                    raise ValueError("Empty API response")
                data = response.json()
                if not isinstance(data, list):
                    raise ValueError(f"Unexpected API response format: {response.text}")
                df = pd.DataFrame(data)
                df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce')
                df.set_index("datetime", inplace=True)
                logging.info(f"Successfully processed intraday data for {ticker} on exchange {exchange}")
                return df
            except ValueError as e:
                logging.error(f"Error processing intraday data for {ticker} on exchange {exchange}: {e}")
                logging.error(f"Full API Response: {response.text}")
                return None
            except Exception as e:
                logging.error(f"Unexpected error processing intraday data for {ticker} on exchange {exchange}: {e}")
                return None
        else:
            logging.error(f"Failed to fetch intraday data: {response.text}")
            logging.error(f"HTTP Status Code: {response.status_code}")
            return None

    def get_daily_data(self, ticker):
        logging.info(f"Fetching daily data for {ticker}")
        endpoint = f"https://eodhd.com/api/eod/{ticker}?api_token={self.api_key}&fmt=json"
        response = requests.get(endpoint)
        logging.debug(f"API Response: {response.text}")
        if response.status_code == 200:
            try:
                if response.text.strip() == "":
                    raise ValueError("Empty API response")
                data = response.json()
                if not isinstance(data, list):
                    raise ValueError(f"Unexpected API response format: {response.text}")
                df = pd.DataFrame(data)
                df["date"] = pd.to_datetime(df["date"], errors='coerce')
                df.set_index("date", inplace=True)
                logging.info(f"Successfully processed daily data for {ticker}")
                return df
            except ValueError as e:
                logging.error(f"Error processing daily data for {ticker}: {e}")
                logging.error(f"Full API Response: {response.text}")
                return None
            except Exception as e:
                logging.error(f"Unexpected error processing daily data for {ticker}: {e}")
                return None
        else:
            logging.error(f"Failed to fetch daily data: {response.text}")
            logging.error(f"HTTP Status Code: {response.status_code}")
            return None

    def scan_market(self, criteria):
        logging.info(f"Scanning market with criteria: {criteria}")
        endpoint = f"https://eodhd.com/api/screener?api_token={self.api_key}"
        response = requests.get(endpoint, params=criteria)
        logging.debug(f"API Response: {response.text}")
        if response.status_code == 200:
            try:
                if response.text.strip() == "":
                    raise ValueError("Empty API response")
                data = response.json()["data"]
                return data
            except ValueError as e:
                logging.error(f"Error processing market scan data: {e}")
                logging.error(f"Full API Response: {response.text}")
                return []
            except Exception as e:
                logging.error(f"Unexpected error processing market scan data: {e}")
                return []
        else:
            logging.error(f"Failed to scan market: {response.text}")
            logging.error(f"HTTP Status Code: {response.status_code}")
            return []
