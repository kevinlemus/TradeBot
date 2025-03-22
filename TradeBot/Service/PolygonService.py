import requests
import logging
import pickle
import os


class PolygonService:
    def __init__(self, api_key, cache_dir="polygon_cache"):
        self.api_key = api_key
        self.cache_dir = cache_dir
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

    def _save_to_cache(self, data, filename):
        """
        Save data to cache using pickle.
        """
        filepath = os.path.join(self.cache_dir, filename)
        try:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
            logging.debug(f"Data cached successfully: {filename}")
        except Exception as e:
            logging.error(f"Failed to cache data to {filename}: {e}")

    def _load_from_cache(self, filename):
        """
        Load data from cache using pickle.
        """
        filepath = os.path.join(self.cache_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    logging.debug(f"Data loaded from cache: {filename}")
                    return pickle.load(f)
        except Exception as e:
            logging.error(f"Failed to load data from {filename}: {e}")
        return None

    def _make_request_with_retries(self, url, params, retries=3):
        """
        Helper method to make API requests with retries.
        """
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    return response
                else:
                    logging.warning(
                        f"Request failed with status {response.status_code}. Retrying... (Attempt {attempt + 1})"
                    )
            except Exception as e:
                logging.error(f"Request failed: {e}")
        return None

    def scan_market(self):
        """
        Fetches all active tickers from Polygon's `/v3/reference/tickers` endpoint.
        """
        cache_filename = "scan_market.pkl"
        cached_data = self._load_from_cache(cache_filename)
        if cached_data:
            logging.info(f"Using cached tickers data from {cache_filename}")
            return cached_data

        endpoint = "https://api.polygon.io/v3/reference/tickers"
        params = {
            "market": "stocks",
            "active": "true",
            "apiKey": self.api_key,
            "limit": 500,
        }
        tickers = []

        while endpoint:
            response = self._make_request_with_retries(endpoint, params)
            if response and response.status_code == 200:
                data = response.json()
                logging.debug(f"Raw API Response: {data}")
                tickers.extend(data.get("results", []))
                endpoint = data.get("next_url")  # Handle pagination
            else:
                logging.error(
                    f"Failed to fetch tickers: HTTP {response.status_code if response else 'N/A'}"
                )
                break

        self._save_to_cache(tickers, cache_filename)
        logging.info(f"Total tickers retrieved and cached: {len(tickers)}")
        return tickers

    def get_ticker_details(self, ticker):
        """
        Fetch detailed information for a specific ticker using `/v3/reference/tickers/{ticker}`.
        """
        cache_filename = f"{ticker}_details.pkl"
        cached_data = self._load_from_cache(cache_filename)
        if cached_data:
            logging.info(f"Using cached details for {ticker} from {cache_filename}")
            return cached_data

        endpoint = f"https://api.polygon.io/v3/reference/tickers/{ticker}"
        params = {"apiKey": self.api_key}
        response = self._make_request_with_retries(endpoint, params)

        if response and response.status_code == 200:
            data = response.json()
            logging.debug(f"Details for {ticker}: {data}")
            self._save_to_cache(data.get("results", {}), cache_filename)
            return data.get("results", {})
        else:
            logging.error(
                f"Failed to fetch details for {ticker}: HTTP {response.status_code if response else 'N/A'}"
            )
            return {}

    def get_ticker_aggregates(
        self, ticker, from_date, to_date, multiplier=1, timespan="day"
    ):
        """
        Fetch aggregated data (e.g., OHLC, volume) for a specific ticker over a date range using `/v2/aggs/ticker/...`.
        """
        cache_filename = f"{ticker}_{from_date}_{to_date}_aggregates.pkl"
        cached_data = self._load_from_cache(cache_filename)
        if cached_data:
            logging.info(f"Using cached aggregates for {ticker} from {cache_filename}")
            return cached_data

        endpoint = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"apiKey": self.api_key}
        response = self._make_request_with_retries(endpoint, params)

        if response and response.status_code == 200:
            data = response.json()
            logging.debug(f"Aggregates for {ticker}: {data}")
            self._save_to_cache(data.get("results", []), cache_filename)
            return data.get("results", [])
        else:
            logging.error(
                f"Failed to fetch aggregates for {ticker}: HTTP {response.status_code if response else 'N/A'}"
            )
            return []

    def get_historical_data(self, ticker, from_date, to_date):
        """
        Wrapper for fetching historical data using get_ticker_aggregates.
        """
        logging.info(
            f"Fetching historical data for {ticker} from {from_date} to {to_date}"
        )
        return self.get_ticker_aggregates(
            ticker, from_date, to_date, multiplier=1, timespan="day"
        )
