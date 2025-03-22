# Model/TradeRequest.py

class TradeRequest:
    def __init__(self, ticker, trade_type, quantity, price, account_id):
        # Initialize a TradeRequest instance with the given parameters
        self.ticker = ticker           # The ticker symbol of the stock (e.g., AAPL)
        self.trade_type = trade_type   # The type of trade (e.g., buy, sell)
        self.quantity = quantity       # The quantity of shares to trade
        self.price = price             # The price at which to execute the trade
        self.account_id = account_id   # The account ID to execute the trade

    def to_dict(self):
        # Convert the TradeRequest instance to a dictionary
        return {
            'ticker': self.ticker,
            'trade_type': self.trade_type,
            'quantity': self.quantity,
            'price': self.price,
            'account_id': self.account_id
        }
