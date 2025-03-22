# TradeJournalService.py
from TradeBot.DAO.DatabaseDAO import DatabaseDAO  # Updated with absolute import
import pyautogui
from datetime import datetime


class TradeJournalService:
    def __init__(self, db_dao: DatabaseDAO):
        self.db_dao = db_dao

    def capture_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)
        with open(screenshot_path, "rb") as file:
            binary_data = file.read()
        return binary_data

    def log_trade(self, ticker, entry_price, current_price, exit_price):
        date = datetime.now().date()
        time_of_day = datetime.now().time()
        realized_percentage = (
            ((exit_price - entry_price) / entry_price) * 100 if exit_price else None
        )
        screenshot = self.capture_screenshot()
        self.db_dao.insert_trade(
            date,
            time_of_day,
            ticker,
            entry_price,
            current_price,
            exit_price,
            realized_percentage,
            screenshot,
        )

    def get_trade_history(self):
        return self.db_dao.get_trades()
