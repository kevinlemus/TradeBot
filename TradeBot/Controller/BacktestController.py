from flask import Flask, request, jsonify
from Service.BacktestService import BacktestService

# Create a Flask application instance
app = Flask(__name__)

# Initialize the BacktestService
backtest_service = BacktestService()

# Define a route to backtest a trading strategy
@app.route('/backtest_strategy', methods=['POST'])
def backtest_strategy():
    # Get the strategy request data from the JSON payload
    strategy_request = request.json
    # Perform backtesting using the BacktestService
    result = backtest_service.backtest_strategy(strategy_request)
    # Return the backtest result as a JSON response
    return jsonify(result)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
