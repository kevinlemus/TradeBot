import logging


class BacktestMarketScannerService:
    def __init__(self, polygon_service, max_retries=3, retry_delay=2):
        self.polygon_service = polygon_service
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def filter_initial_results(self, tickers, from_date, to_date):
        """
        Fetch aggregated data and apply filtering to tickers based on small-cap criteria:
        - Market cap < $1B
        - Volume >= 1M
        - Price range between $0.15 and $20
        """
        filtered = []
        for ticker in tickers:
            try:
                # Fetch detailed ticker attributes for market cap
                details = self.polygon_service.get_ticker_details(ticker["ticker"])
                if not details or details.get("type") == "WARRANT":  # Skip warrants
                    logging.debug(f"Skipping {ticker['ticker']} due to unsupported type or missing details.")
                    continue

                market_cap = float(details.get("market_cap", 0))

                # Fetch aggregates for volume and price data
                aggregates = self.polygon_service.get_ticker_aggregates(
                    ticker["ticker"], from_date, to_date
                )
                if not aggregates:
                    logging.debug(f"No aggregate data found for {ticker['ticker']}. Skipping.")
                    continue

                # Use the last day's data for filtering
                last_day_data = aggregates[-1]  # Assuming it's sorted
                last_price = float(last_day_data.get("c", 0))  # Closing price
                volume = int(last_day_data.get("v", 0))  # Volume

                logging.debug(f"Ticker: {ticker['ticker']} | Market Cap: {market_cap} | Price: {last_price} | Volume: {volume}")

                # Apply stricter filtering criteria
                if (
                    market_cap < 1_000_000_000
                    and volume >= 1_000_000
                    and 0.15 <= last_price <= 20
                ):
                    filtered.append(ticker["ticker"])
                else:
                    logging.debug(f"Ticker {ticker['ticker']} did not meet criteria: Market Cap {market_cap}, Volume {volume}, Price {last_price}")
            except (TypeError, ValueError) as e:
                logging.warning(f"[Backtest] Skipping ticker due to parsing error: {ticker}. Error: {e}")

        logging.info(f"[Backtest] Initial filter yielded {len(filtered)} tickers meeting the small-cap criteria.")
        return filtered

    def fetch_gap_data(self, symbols, from_date, to_date):
        """
        Fetch historical data for calculating gaps (e.g., overnight price change).
        """
        gap_results = []
        for symbol in symbols:
            try:
                # Fetch the daily historical data
                historical_data = self.polygon_service.get_ticker_aggregates(
                    symbol, from_date, to_date
                )

                # Check if data is valid and is a list
                if not historical_data or not isinstance(historical_data, list):
                    logging.warning(f"Invalid or empty historical data for {symbol}. Skipping.")
                    continue

                # Calculate gap percent for each day
                for i in range(1, len(historical_data)):
                    previous_day = historical_data[i - 1]
                    current_day = historical_data[i]

                    # Make sure the necessary keys exist
                    if all(key in previous_day and key in current_day for key in ["c", "o"]):
                        gap_percent = ((current_day["o"] - previous_day["c"]) / previous_day["c"]) * 100

                        gap_results.append({
                            "symbol": symbol,
                            "date": current_day["t"],
                            "gap_percent": gap_percent,
                            "volume": current_day["v"],
                            "price": current_day["c"],
                        })
                    else:
                        logging.warning(f"Missing keys in data for {symbol}. Skipping day.")

            except Exception as e:
                logging.warning(f"[Backtest] Failed to fetch or process data for {symbol}. Error: {e}")

        logging.info(f"[Backtest] Gap data fetched for {len(gap_results)} tickers.")
        return gap_results

    def scan_market(self, from_date, to_date):
        """
        Perform historical market scan targeting gappers.
        """
        logging.info(f"[Backtest] Starting gap scan for {from_date} to {to_date}...")

        # Step 1: Retrieve all active tickers
        tickers = self.polygon_service.scan_market()

        # Step 2: Fetch detailed attributes and apply filtering
        pre_filtered_symbols = self.filter_initial_results(tickers, from_date, to_date)

        # Step 3: Fetch gap data for pre-filtered symbols
        gap_data = self.fetch_gap_data(pre_filtered_symbols, from_date, to_date)

        return gap_data
