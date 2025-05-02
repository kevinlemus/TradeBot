import logging
import os
import sys
import pandas as pd
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


def backtest_ticker(ticker_file, from_date, to_date):
    try:
        backtest_service = BacktestService(data_folder=os.path.dirname(ticker_file))
        historical_data = pd.read_csv(ticker_file)

        if "t" not in historical_data.columns:
            logging.warning(f"{ticker_file}: Missing 't' column. Skipping.")
            return None

        try:
            historical_data["t"] = pd.to_datetime(
                historical_data["t"], unit="ms", errors="coerce"
            )
            historical_data.set_index("t", inplace=True)
        except Exception as e:
            logging.error(f"{ticker_file}: Failed to parse timestamps. Error: {e}")
            return None

        historical_data = historical_data[
            ~historical_data.index.duplicated(keep="first")
        ]
        date_range = pd.date_range(
            start=historical_data.index.min(), end=historical_data.index.max(), freq="D"
        )
        historical_data = (
            historical_data.reindex(date_range)
            .fillna(method="ffill")
            .fillna(method="bfill")
        )

        if "support" not in historical_data.columns:
            historical_data["support"] = (
                historical_data["low"].rolling(window=20, min_periods=1).min()
            )

        from_date = pd.Timestamp(from_date)
        to_date = pd.Timestamp(to_date)
        adjusted_from_date = max(from_date, historical_data.index.min())
        adjusted_to_date = min(to_date, historical_data.index.max())

        data_in_range = historical_data.loc[adjusted_from_date:adjusted_to_date]
        if data_in_range.empty:
            logging.warning(
                f"{ticker_file}: No valid data in adjusted range. Skipping."
            )
            return None

        if "support" not in data_in_range.columns:
            logging.warning(
                f"{ticker_file}: Missing 'support' column after slicing. Generating dynamically."
            )
            data_in_range["support"] = (
                data_in_range["low"].rolling(window=20, min_periods=1).min()
            )

        buy_signals = (
            (data_in_range["support"] >= 2)
            & (data_in_range["rsi"] < 40)
            & (
                abs(data_in_range["close"] - data_in_range["200ma"])
                < 0.1 * data_in_range["200ma"]
            )
        )
        selected_data = data_in_range[buy_signals]
        if selected_data.empty:
            logging.debug(f"No trades executed for {ticker_file}.")
            return None

        summary = {
            "ticker": ticker_file,
            "total_trades": len(selected_data),
            "profit_loss": 0.0,
        }
        for _, day_data in selected_data.iterrows():
            summary["profit_loss"] += backtest_service._simulate_trade(day_data)

        logging.info(f"Backtest summary for {ticker_file}: {summary}")
        return summary
    except Exception as e:
        logging.error(f"Error processing {ticker_file}: {e}")
        return None


def run_parallel_backtest(files, from_date, to_date):
    """
    Perform parallelized backtest for multiple tickers.
    """
    from concurrent.futures import ProcessPoolExecutor

    try:
        with ProcessPoolExecutor() as executor:
            results = list(
                executor.map(
                    backtest_ticker,
                    files,
                    [from_date] * len(files),
                    [to_date] * len(files),
                )
            )
            for result in results:
                if result is None:
                    logging.warning("Skipped a ticker due to missing data or errors.")
                    continue
                if result["total_trades"] > 0:
                    logging.info(f"Backtest summary for {result['ticker']}: {result}")
                else:
                    logging.debug(f"No trades executed for {result['ticker']}.")
    except Exception as e:
        logging.error(f"[Backtest] Parallel execution failed: {e}")


def run_backtest(from_date, to_date):
    """
    Perform a backtest for the given date range.
    """
    try:
        logging.info(f"Starting backtest for date range: {from_date} to {to_date}")
        data_folder = (
            "C:\\Users\\kevin\\vscode-projects\\trade-bot\\TradeBot\\MarketData"
        )

        backtest_service = BacktestService(
            data_folder=data_folder, journal_service=None
        )

        # Fetch CSV files
        csv_files = backtest_service.get_csv_files()
        if not csv_files:
            logging.warning("No CSV files found in the data folder.")
            return

        # Run parallel processing for speed
        run_parallel_backtest(csv_files, from_date, to_date)

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
