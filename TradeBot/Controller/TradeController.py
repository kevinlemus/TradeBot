from Controller.TradeController import app as trade_app
from Controller.BacktestController import app as backtest_app
from multiprocessing import Process
from Auth.OAuth import OAuth
from DAO.DatabaseDAO import DatabaseDAO

# Function to run the trade Flask app
def run_trade_app():
    trade_app.run(debug=True, port=5000)

# Function to run the backtest Flask app
def run_backtest_app():
    backtest_app.run(debug=True, port=5001)

# Function to handle OAuth authentication and token retrieval
def authenticate_and_get_tokens():
    oauth = OAuth()
    oauth.get_authorization_code()  # Direct user to authorize the app and obtain authorization code

    # After user authorization, retrieve the authorization code
    authorization_code = input("Enter the authorization code: ")

    # Get the access token using the authorization code
    access_token_response = oauth.get_access_token(authorization_code)
    print("Access Token:", access_token_response['access_token'])
    # Store access tokens as needed for later use

if __name__ == '__main__':
    # Initialize DatabaseDAO to create tables if they don't exist
    db_dao = DatabaseDAO()

    # Authenticate and get tokens
    authenticate_and_get_tokens()

    # Start the Flask apps in separate processes
    trade_process = Process(target=run_trade_app)
    backtest_process = Process(target=run_backtest_app)

    # Start the processes
    trade_process.start()
    backtest_process.start()

    # Wait for the processes to complete
    trade_process.join()
    backtest_process.join()
