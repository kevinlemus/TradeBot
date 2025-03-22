# Config.py

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Missytheinvestor96!",
    "database": "TradeBot_Pro",
    "port": 3306,
}

# Schwab API credentials
API_KEYS = {
    "schwab_app_key": "F0YcE1xniZ1jzlbxrK9kG8yU3zqAQKXU",
    "schwab_client_secret": "RRx7K9Cf6Nco7mwf",
}

OAUTH_CONFIG = {
    "redirect_uri": "https://127.0.0.1/callback",
    "authorization_url": "https://api.schwabapi.com/v1/oauth/authorize",
    "token_url": "https://api.schwabapi.com/v1/oauth/token",
    "scope": "market_data.read",  # Adjust scope as required
}

# Market Data API configuration
MARKET_DATA_API_CONFIG = {
    "base_url": "https://api.schwabapi.com/marketdata/v1",
    "headers": lambda access_token: {"Authorization": f"Bearer {access_token}"},
}

# Configuration for trading API
TRADE_API_CONFIG = {
    "endpoint": "https://api.schwabapi.com/trader/v1/accounts/{account_id}/orders",
    "headers": lambda access_token: {"Authorization": f"Bearer {access_token}"},
}

# Configuration for backtesting
BACKTEST_CONFIG = {
    "default_period": {
        "fromdate": "2015-01-01",
        "todate": "2025-01-01",
    },
    "analyzers": [
        "TradeAnalyzer",
        "SharpeRatio",
        "DrawDown",
    ],
}

# Polygon.io Historical Data API credentials
POLYGON_API_KEY = "8h4nb6aWnyIpgCmpSg49703qLekGgEx_"
