# Service/TradeService.py

from DAO.MarketDataDAO import MarketDataDAO
from DAO.TradeExecutionDAO import TradeExecutionDAO
from Service.StrategyService import StrategyService
from Model.TradeRequest import TradeRequest
from Auth.OAuth import OAuth

class TradeService:
    def __init__(self, market_data_dao: MarketDataDAO, trade_execution_dao: TradeExecutionDAO, strategy_service: StrategyService):
        self.market_data_dao = market_data_dao
        self.trade_execution_dao = trade_execution_dao
        self.strategy_service = strategy_service
        self.daily_trade_executed = False

    def execute_trade(self, trade_request: TradeRequest):
        if self.daily_trade_executed:
            print("Daily trade limit reached. No more trades can be executed today.")
            return

        available_funds = self.get_available_funds()
        if available_funds <= 0:
            print("No funds available for trading.")
            return

        signal = self.strategy_service.get_trade_signal(trade_request.ticker)
        if signal == 1:
            trade_request.quantity = available_funds // trade_request.price
            self.trade_execution_dao.execute_buy(trade_request.to_dict())
            self.daily_trade_executed = True
        elif signal == -1:
            self.trade_execution_dao.execute_sell(trade_request.to_dict())
            self.daily_trade_executed = True

    def get_available_funds(self):
        return 100000

# Example usage:
# oauth = OAuth(client_id_type='accounts')
# trade_service = TradeService(market_data_dao, trade_execution_dao, strategy_service)
# trade_request = TradeRequest('AAPL', 'buy', 10, 150, 'ACCOUNT_ID')
# trade_service.execute_trade(trade_request)
