import logging
import os
import sys
from datetime import datetime, timedelta

# Ensure the project root is included in the Python module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

# Correct imports for the project structure
from TradeBot.Service.BacktestMarketScannerService import BacktestMarketScannerService
from TradeBot.Service.PolygonService import PolygonService
from TradeBot.Service.BacktestService import BacktestService
from TradeBot.Config import POLYGON_API_KEY


def run_backtest(from_date, to_date):
    """
    Perform a backtest for the given date range.
    """
    try:
        logging.info(f"Starting backtest for date range: {from_date} to {to_date}")
        polygon_service = PolygonService(POLYGON_API_KEY)
        backtest_scanner = BacktestMarketScannerService(polygon_service)
        backtest_service = BacktestService(
            polygon_service, None
        )  # No journal service passed for now

        # Perform the historical market scan
        filtered_results = backtest_scanner.scan_market(from_date, to_date)

        if filtered_results:
            logging.info(f"[Backtest] Filtered results: {filtered_results}")
            # Run backtest on each filtered result
            for result in filtered_results:
                ticker = result["symbol"]
                backtest_service.run_backtest(ticker, from_date, to_date)

            # Generate and log the backtesting summary
            summary = backtest_service.get_summary()
            logging.info("Backtesting Summary:")
            for key, value in summary.items():
                logging.info(f"{key}: {value}")
        else:
            logging.warning("[Backtest] No results meeting the criteria.")
    except Exception as e:
        logging.error(f"[Backtest] Failed to perform backtest: {e}")


if __name__ == "__main__":
    # Configure logging
    log_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logs", "app.log"
    )
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

    logging.info("Starting historical backtest...")

    # Define backtest date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Example: Backtest last 30 days

    # Run the backtest
    run_backtest(
        from_date=start_date.strftime("%Y-%m-%d"), to_date=end_date.strftime("%Y-%m-%d")
    )
