# Controller/TradeJournalController.py

from flask import Flask, request, jsonify
from Service.TradeJournalService import TradeJournalService
from DAO.DatabaseDAO import DatabaseDAO

# Create a Flask application instance
app = Flask(__name__)

# Initialize the DatabaseDAO
db_dao = DatabaseDAO()

# Initialize the TradeJournalService with the DatabaseDAO
trade_journal_service = TradeJournalService(db_dao)


# Define a route to log a trade
@app.route("/log_trade", methods=["POST"])
def log_trade():
    # Get the trade request data from the JSON payload
    trade_request = request.json
    # Log the trade using the TradeJournalService
    trade_journal_service.log_trade(
        trade_request["ticker"],
        trade_request["entry_price"],
        trade_request["current_price"],
        trade_request["exit_price"],
    )
    # Return a success message as a JSON response
    return jsonify({"message": "Trade logged successfully."})


# Define a route to get the trade history
@app.route("/trade_history", methods=["GET"])
def trade_history():
    # Retrieve the trade history using the TradeJournalService
    trades = trade_journal_service.get_trade_history()
    # Return the trade history as a JSON response
    return jsonify(trades)


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
