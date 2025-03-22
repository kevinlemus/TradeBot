import mysql.connector
from TradeBot.Config import DB_CONFIG  # Updated with absolute import


class DatabaseDAO:
    def __init__(self):
        # Initialize the database connection using the configuration
        self.conn = mysql.connector.connect(**DB_CONFIG)
        # Create tables if they do not exist
        self.create_tables()

    def create_tables(self):
        # Create tables for storing trading journal entries
        with self.conn.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS trades (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                date DATE NOT NULL,
                                time_of_day TIME NOT NULL,
                                ticker VARCHAR(10) NOT NULL,
                                entry_price DECIMAL(10, 2) NOT NULL,
                                current_price DECIMAL(10, 2),
                                exit_price DECIMAL(10, 2),
                                realized_percentage DECIMAL(5, 2),
                                screenshot LONGBLOB,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )"""
            )
        self.conn.commit()

    def insert_trade(
        self,
        date,
        time_of_day,
        ticker,
        entry_price,
        current_price,
        exit_price,
        realized_percentage,
        screenshot,
    ):
        # Insert a new trade entry into the trades table
        with self.conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO trades (date, time_of_day, ticker, entry_price, current_price, exit_price, realized_percentage, screenshot)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    date,
                    time_of_day,
                    ticker,
                    entry_price,
                    current_price,
                    exit_price,
                    realized_percentage,
                    screenshot,
                ),
            )
        self.conn.commit()

    def get_trades(self):
        # Retrieve all trade entries from the trades table
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM trades""")
            return cursor.fetchall()
