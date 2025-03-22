# Service/StrategyService.py

import pandas as pd
from datetime import datetime
from DAO.MarketDataDAO import MarketDataDAO


class StrategyService:
    def __init__(self, market_data_dao: MarketDataDAO):
        self.market_data_dao = market_data_dao

    def calculate_indicators_5min(self, data):
        data["8MA"] = data["close"].rolling(window=8).mean()
        data["12MA"] = data["close"].rolling(window=12).mean()
        data["50MA"] = data["close"].rolling(window=50).mean()
        data["100MA"] = data["close"].rolling(window=100).mean()
        data["200MA"] = data["close"].rolling(window=200).mean()

        # RSI Calculation
        delta = data["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data["RSI"] = 100 - (100 / (1 + rs))

        # VWAP Calculation
        data["VWAP"] = (data["close"] * data["volume"]).cumsum() / data[
            "volume"
        ].cumsum()

        return data

    def find_support_levels(self, data_daily, data_4hr):
        # Combine daily and 4-hour data to identify major support levels
        supports = set()

        # Example logic to identify support levels based on bounce counts
        for data in [data_daily, data_4hr]:
            potential_supports = data["close"].value_counts()
            major_supports = potential_supports[potential_supports >= 3].index.tolist()
            supports.update(major_supports)

        return list(supports)

    def generate_signals(self, data_5min, data_daily, data_4hr):
        data_5min = self.calculate_indicators_5min(data_5min)
        supports = self.find_support_levels(data_daily, data_4hr)

        data_5min["signal"] = 0
        for i in range(len(data_5min)):
            if (
                data_5min["RSI"].iloc[i] < 30
                and data_5min["close"].iloc[i] in supports
                and data_5min["close"].iloc[i] <= data_5min["200MA"].iloc[i]
            ):
                data_5min["signal"].iloc[i] = 1  # Buy Signal

        return data_5min

    def get_trade_signal(self, ticker):
        # Fetch historical data for different timeframes
        data_5min = self.market_data_dao.get_historical_data(ticker, "5min")
        data_daily = self.market_data_dao.get_historical_data(ticker, "1d")
        data_4hr = self.market_data_dao.get_historical_data(ticker, "4hr")

        # Convert to DataFrames
        data_5min = pd.DataFrame(data_5min)
        data_daily = pd.DataFrame(data_daily)
        data_4hr = pd.DataFrame(data_4hr)

        # Generate signals
        data_5min = self.generate_signals(data_5min, data_daily, data_4hr)
        latest_signal = data_5min["signal"].iloc[-1]
        return latest_signal


# Example usage
# market_data_dao = MarketDataDAO('YOUR_API_KEY')
# strategy_service = StrategyService(market_data_dao)
# signal = strategy_service.get_trade_signal('AAPL')
# print(signal)
