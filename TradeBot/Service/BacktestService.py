import logging
from math import sqrt


class BacktestService:
    def __init__(self, market_data_service, journal_service=None):
        self.market_data_service = market_data_service
        self.journal_service = journal_service
        self.summary = {
            "total_tickers_tested": 0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit_loss": 0.0,
            "average_profit_loss_per_trade": 0.0,
            "average_profit_loss_per_ticker": 0.0,
            "max_profit_trade": None,
            "max_loss_trade": None,
            "profitable_tickers": 0,
            "unprofitable_tickers": 0,
            "sharpe_ratio": 0.0,
            "win_loss_ratio": 0.0,
            "drawdown_percentage": 0.0,
        }
        self.all_trades = []  # Collect all trades globally for summary calculations

    def run_backtest(self, ticker, from_date, to_date, transaction_cost=0.0):
        """
        Perform a backtest for a single ticker.
        """
        try:
            logging.info(f"\nStarting backtest for {ticker}...")

            # Fetch historical data using get_historical_data
            historical_data = self.market_data_service.get_historical_data(
                ticker, from_date, to_date
            )

            if not historical_data:
                logging.warning(f"No historical data available for {ticker}")
                return

            # Identify major supports and verify 200MA & RSI conditions
            major_supports = self._identify_major_supports(historical_data)
            trades = self._simulate_trades(
                historical_data, major_supports, transaction_cost
            )

            # Store trades for later global calculations
            self.all_trades.extend(trades)

            ticker_profit_loss = sum(trade["profit_loss"] for trade in trades)

            # Update summary statistics
            self.summary["total_tickers_tested"] += 1
            self.summary["total_trades"] += len(trades)
            self.summary["total_profit_loss"] += ticker_profit_loss
            self.summary["average_profit_loss_per_ticker"] = (
                self.summary["total_profit_loss"] / self.summary["total_tickers_tested"]
            )

            # Count profitable and unprofitable tickers
            if ticker_profit_loss > 0:
                self.summary["profitable_tickers"] += 1
            else:
                self.summary["unprofitable_tickers"] += 1

            # Track winning and losing trades
            for trade in trades:
                if trade["profit_loss"] > 0:
                    self.summary["winning_trades"] += 1
                else:
                    self.summary["losing_trades"] += 1

                # Track max profit and max loss trades
                if (
                    self.summary["max_profit_trade"] is None
                    or trade["profit_loss"] > self.summary["max_profit_trade"]
                ):
                    self.summary["max_profit_trade"] = trade["profit_loss"]
                if (
                    self.summary["max_loss_trade"] is None
                    or trade["profit_loss"] < self.summary["max_loss_trade"]
                ):
                    self.summary["max_loss_trade"] = trade["profit_loss"]

            # Log results for this ticker
            logging.info(f"Backtest for {ticker} completed. P/L: {ticker_profit_loss}")
        except Exception as e:
            logging.error(f"Backtest failed for {ticker}: {e}")

    def _identify_major_supports(self, historical_data):
        """
        Identify major support levels based on the 4hr/1day data.
        """
        # Example: Identify levels with 3+ bounces
        support_levels = []
        # Add logic to detect support levels here (e.g., price bounce points)
        return support_levels

    def _simulate_trades(self, historical_data, major_supports, transaction_cost):
        """
        Simulate trades based on conditions: 200MA, RSI, and major supports.
        """
        trades = []
        for i in range(1, len(historical_data)):
            # Check if price is at major support & RSI oversold with 200MA alignment
            # Example: Implement condition checks here
            buy_price = historical_data[i - 1]["c"]
            sell_price = historical_data[i]["c"]

            # Calculate profit/loss with transaction costs
            profit_loss = (sell_price - buy_price) - transaction_cost
            trades.append(
                {
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "profit_loss": profit_loss,
                }
            )

        return trades

    def get_summary(self):
        """
        Generate a detailed summary of the backtesting results with enhanced metrics.
        """
        if self.summary["total_trades"] > 0:
            self.summary["average_profit_loss_per_trade"] = (
                self.summary["total_profit_loss"] / self.summary["total_trades"]
            )
            self.summary["win_loss_ratio"] = (
                self.summary["winning_trades"] / self.summary["losing_trades"]
                if self.summary["losing_trades"] > 0
                else float("inf")
            )

        # Example Sharpe Ratio Calculation
        mean_return = (
            self.summary["total_profit_loss"] / self.summary["total_trades"]
            if self.summary["total_trades"] > 0
            else 0
        )
        std_dev = (
            sqrt(
                sum(
                    (trade["profit_loss"] - mean_return) ** 2
                    for trade in self.all_trades  # Use all_trades for Sharpe calculation
                )
                / len(self.all_trades)
            )
            if self.all_trades
            else 0
        )
        self.summary["sharpe_ratio"] = mean_return / (std_dev or 1)

        # Log a prettier summary
        logging.info("\n--- Backtesting Summary ---")
        for key, value in self.summary.items():
            logging.info(f"{key.replace('_', ' ').capitalize()}: {value}")
        logging.info("\n---------------------------\n")

        return self.summary
