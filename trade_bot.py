import os
import json
import random
from datetime import datetime

from openai import OpenAI
import yfinance as yf  # For Yahoo Finance data


# --- CONFIG ---
STOCK_PICK_COUNT = 10
INITIAL_CASH = 10000.0
TRADES_PATH = "data/trades.json"
PORTFOLIO_PATH = "data/portfolio.json"

# --- UTILITIES ---
def ensure_data_folder():
    os.makedirs("data", exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def current_time():
    return datetime.utcnow().isoformat() + "Z"

# --- MAIN BOT LOOP ---

def main():

    ensure_data_folder()

    # Load or init trade log and portfolio
    trades = load_json(TRADES_PATH, [])
    portfolio = load_json(PORTFOLIO_PATH, {
        "cash": INITIAL_CASH,
        "positions": {}
    })

    # Get daily stock picks
    picks = get_daily_stock_picks()
    print(f"Today's picks: {picks}")

    # Simulate trades
    simulate_trades(picks, trades, portfolio)

    # Save updated data
    save_json(TRADES_PATH, trades)
    save_json(PORTFOLIO_PATH, portfolio)

if __name__ == "__main__":
    main()
