import yfinance as yf

def is_valid_ticker(ticker):
    """
    Check if a given ticker is a valid stock symbol via yfinance.
    """
    try:
        info = yf.Ticker(ticker).info
        return bool(info and "shortName" in info)
    except Exception:
        return False