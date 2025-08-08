# risk_assessor.py

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

class RiskAssessor:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.data = {}
        self.risk_score = None
        self.reasoning = ""

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
            f"Based on the stock data below, assign a risk score from 1 to 100, where 1 means extremely low risk "
            f"(e.g. stable blue-chip stock), and 100 means extremely high risk (e.g. penny stock, highly volatile, or news-driven).\n\n"
            f"Risk categories:\n"
            f"1-20: Very Low Risk\n21-40: Low Risk\n41-60: Moderate Risk\n61-80: High Risk\n81-100: Very High Risk\n\n"
            f"Ticker: {self.ticker}\n"
            f"Data: {self.data}\n\n"
            f"Respond in this format:\n"
            f"Risk Score: <1–100>\n"
            f"Explanation: <3 concise sentences>"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        content = response.choices[0].message.content.strip()

        match = re.search(r"Risk Score:\s*(\d{1,3})", content)
        self.risk_score = int(match.group(1)) if match else None

        explanation_match = re.search(r"Explanation:\s*(.+)", content, re.DOTALL)
        self.reasoning = explanation_match.group(1).strip() if explanation_match else ""

    def assess_risk(self):
        self.fetch_yahoo_finance_data()
        self.analyze_with_chatgpt()
        return {
            "ticker": self.ticker,
            "risk_score": self.risk_score,
            "reasoning": self.reasoning,
        }

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(f"\nRunning risk assessment for: {ticker}")

    assessor = RiskAssessor(ticker)
    try:
        result = assessor.assess_risk()
        print(f"\nRISK ASSESSMENT for {result['ticker']}:")
        print(f"  Risk Score: {result['risk_score']}/100")
        print(f"  Explanation:\n{result['reasoning']}")
    except Exception as e:
        print(f"\nError assessing risk for {ticker}: {e}")
