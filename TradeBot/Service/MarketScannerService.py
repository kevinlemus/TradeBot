import logging


class MarketScannerService:
    def __init__(self, polygon_service, backtest_service, max_retries=3, retry_delay=2):
        self.polygon_service = polygon_service
        self.backtest_service = backtest_service
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.permanent_blacklist = set()

    def filter_initial_results(self, tickers):
        """
        Apply initial filtering to tickers based on small-cap criteria:
        - Market cap < $1B
        - Volume >= 1M (if available in metadata)
        - Price range between $0.15 and $20 (if available in metadata)
        """
        filtered = []
        for ticker in tickers:
            try:
                market_cap = float(ticker.get("market_cap", 0))
                last_price = float(ticker.get("last_price", 0))
                volume = float(ticker.get("volume", 0))

                if (
                    market_cap < 1_000_000_000
                    and volume >= 1_000_000
                    and 0.15 <= last_price <= 20
                ):
                    filtered.append(ticker["ticker"])  # Only keep the symbol
            except (TypeError, ValueError) as e:
                logging.warning(f"Skipping ticker due to parsing error: {ticker}. Error: {e}")

        logging.info(f"Initial filter yielded {len(filtered)} tickers meeting the small-cap criteria.")
        return filtered

    def fetch_detailed_data(self, symbols):
        """
        Fetch detailed intraday data for the filtered symbols.
        """
        detailed_results = []
        for symbol in symbols:
            try:
                intraday_data = self.polygon_service.get_intraday_data(
                    ticker=symbol,
                    interval="day",  # Daily data
                    multiplier=1,
                    fromdate="2025-01-01",
                    todate="2025-01-02",
                )

                if intraday_data is not None:
                    # Extract required fields for final filtering
                    detailed_results.append({
                        "symbol": symbol,
                        "volume": intraday_data.get("Volume", 0),
                        "price": intraday_data.get("Close", 0),
                        "percent_change": intraday_data.get("percent_change", 0),
                    })
            except Exception as e:
                logging.warning(f"Failed to fetch intraday data for {symbol}. Error: {e}")

        logging.info(f"Detailed data fetched for {len(detailed_results)} tickers.")
        return detailed_results

    def filter_detailed_results(self, data):
        """
        Apply final filtering to detailed data:
        - Percent change >= 20% (up or down)
        """
        final_results = [
            item for item in data if abs(item.get("percent_change", 0)) >= 20
        ]
        logging.info(f"Filtered {len(final_results)} tickers with percent change >= 20%.")
        return final_results

    def scan_market(self):
        """
        Perform a market scan targeting small-cap stocks.
        """
        logging.info("Starting market scan for small-cap stocks using Polygon...")

        # Step 1: Retrieve all active tickers
        tickers = self.polygon_service.scan_market()

        # Step 2: Initial filtering based on metadata
        pre_filtered_symbols = self.filter_initial_results(tickers)

        # Step 3: Fetch detailed data only for pre-filtered symbols
        detailed_data = self.fetch_detailed_data(pre_filtered_symbols)

        # Step 4: Final filtering based on percent change
        final_results = self.filter_detailed_results(detailed_data)

        return final_results
