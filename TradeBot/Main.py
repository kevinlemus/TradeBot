import json
import sys
import os
import logging
from Controller.TradeController import app as trade_app
from Controller.BacktestController import app as backtest_app
from multiprocessing import Process
from Auth.OAuth import OAuth
from DAO.DatabaseDAO import DatabaseDAO

# Configure logging
log_directory = "C:\\Users\\kevin\\vscode-projects\\trade-bot\\TradeBot"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    filename=os.path.join(log_directory, "app.log"),
    level=logging.DEBUG,  # Set the logging level to DEBUG for detailed logging
    format="%(asctime)s %(levelname)s: %(message)s",
)

# Function to run the trade Flask app
def run_trade_app():
    logging.info("Starting trade Flask app")
    trade_app.run(debug=True, port=5000)

# Function to run the backtest Flask app
def run_backtest_app():
    logging.info("Starting backtest Flask app")
    backtest_app.run(debug=True, port=5001)

# Function to handle OAuth authentication and token retrieval
def authenticate_and_get_tokens():
    logging.info("Authenticating and getting tokens")
    oauth = OAuth()
    oauth.get_authorization_code()  # Direct user to authorize the app and obtain authorization code

    # After user authorization, retrieve the authorization code
    authorization_code = input("Enter the authorization code: ")

    # Get the access token using the authorization code
    access_token_response = oauth.get_access_token(authorization_code)
    logging.info(f"Access Token: {access_token_response['access_token']}")
    # Store access tokens as needed for later use

if __name__ == '__main__':
    try:
        logging.info("Initializing DatabaseDAO")
        # Initialize DatabaseDAO to create tables if they don't exist
        db_dao = DatabaseDAO()

        # Authenticate and get tokens
        logging.info("Starting authentication process")
        authenticate_and_get_tokens()

        # Start the Flask apps in separate processes
        logging.info("Starting trade and backtest Flask apps in separate processes")
        trade_process = Process(target=run_trade_app)
        backtest_process = Process(target=run_backtest_app)

        # Start the processes
        trade_process.start()
        backtest_process.start()

        # Wait for the processes to complete
        trade_process.join()
        backtest_process.join()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
