# win_predictor.py

import os
import re
import yfinance as yf
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

client = OpenAI(api_key=api_key)

class WinPredictor:
    def __init__(self, ticker, win_percent=10):
        self.ticker = ticker.upper()
        self.win_percent = win_percent
        self.data = {}
        self.prediction_score = None
        self.justification = ""

    def fetch_yahoo_finance_data(self):
        stock = yf.Ticker(self.ticker)
        info = stock.info

        self.data = {
            "currentPrice": info.get("currentPrice"),
            "beta": info.get("beta"),
            "debtToEquity": info.get("debtToEquity"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "sector": info.get("sector"),
            "longBusinessSummary": info.get("longBusinessSummary"),
        }

    def analyze_with_chatgpt(self):
        prompt = (
            f"You are a short-term quantitative trader analyzing the stock below to estimate the probability "
            f"that it will experience a short-term gain of at least {self.win_percent}% **by the end of the current trading day**.\n\n"
            f"A 'win' is defined as a price increase of {self.win_percent}% or more from its current level today.\n\n"
            f"Use the stock's current valuation, technical indicators (if implied), financial ratios, sector performance, "
            f"and any plausible catalysts based on the provided description. Be objective and avoid hype or emotional language.\n\n"
            f"Scoring System (Win Probability Score):\n"
            f"1–20: Highly Unlikely – Fundamentally weak or no recent momentum\n"
            f"21–40: Unlikely – Neutral or slightly negative outlook, no catalysts\n"
            f"41–60: Possible – Mixed indicators, uncertain short-term path\n"
            f"61–80: Likely – Positive setup, possible catalyst, reasonable valuation\n"
            f"81–100: Highly Likely – Strong fundamentals AND immediate bullish catalyst or momentum\n\n"
            f"Do not hedge or include financial disclaimers. Be concise. Avoid repeating the prompt. "
            f"Only base your response on the data provided.\n\n"
            f"Ticker: {self.ticker}\n"
            f"Stock Data: {self.data}\n\n"
            f"Respond in this exact format:\n"
            f"Win Probability Score: <1–100>\n"
            f"Justification: <2 clear, data-driven sentences explaining the score>"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()

        match = re.search(r"Win Probability Score:\s*(\d{1,3})", content)
        self.prediction_score = int(match.group(1)) if match else None

        just_match = re.search(r"Justification:\s*(.+)", content, re.DOTALL)
        self.justification = just_match.group(1).strip() if just_match else ""

    def predict_win(self):
        self.fetch_yahoo_finance_data()
        self.analyze_with_chatgpt()
        return {
            "ticker": self.ticker,
            "win_percent": self.win_percent,
            "prediction_score": self.prediction_score,
            "justification": self.justification,
        }

if __name__ == "__main__":
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    win_percent = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"\nRunning win prediction for {ticker} with target of {win_percent}%...")
    predictor = WinPredictor(ticker, win_percent)

    try:
        result = predictor.predict_win()
        print(f"\nWIN PREDICTION for {result['ticker']}:")
        print(f"  Probability Score: {result['prediction_score']}/100")
        print(f"  Target Win: {result['win_percent']}%")
        print(f"  Justification: {result['justification']}")
    except Exception as e:
        print(f"\nError predicting win for {ticker}: {e}")
