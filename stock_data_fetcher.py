import yfinance as yf
import pandas as pd

class StockDataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.data = {}

    def fetch(self):
        stock = yf.Ticker(self.ticker)
        info = stock.info

        # Historical data for performance
        hist_month = stock.history(period="1mo")
        hist_week = stock.history(period="7d")

        # Calculate performance
        month_perf = None
        week_perf = None
        if not hist_month.empty:
            month_perf = ((hist_month["Close"].iloc[-1] - hist_month["Close"].iloc[0]) / hist_month["Close"].iloc[0]) * 100
        if not hist_week.empty:
            week_perf = ((hist_week["Close"].iloc[-1] - hist_week["Close"].iloc[0]) / hist_week["Close"].iloc[0]) * 100

        # Recent news headlines
        try:
            news = stock.news
            recent_news = [n['title'] for n in news[:5]]
        except Exception:
            recent_news = []

        # Moving averages
        ma7 = hist_month["Close"].rolling(window=7).mean().iloc[-1] if not hist_month.empty else None
        ma30 = hist_month["Close"].rolling(window=30).mean().iloc[-1] if not hist_month.empty else None

        # RSI calculation
        def get_rsi(series, period=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else None

        rsi = get_rsi(hist_month["Close"]) if not hist_month.empty else None

        self.data = {
            "currentPrice": info.get("currentPrice"),
            "beta": info.get("beta"),
            "debtToEquity": info.get("debtToEquity"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "sector": info.get("sector"),
            "longBusinessSummary": info.get("longBusinessSummary"),
            "monthPerformancePct": month_perf,
            "weekPerformancePct": week_perf,
            "averageVolume": info.get("averageVolume"),
            "currentVolume": info.get("volume"),
            "MA7": ma7,
            "MA30": ma30,
            "RSI": rsi,
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "recentNews": recent_news,
        }
        self.hist_month = hist_month  # Save for table output

    def get_data(self):
        if not self.data:
            self.fetch()
        return self.data

    def get_daily_performance_table(self):
        if not hasattr(self, "hist_month"):
            self.fetch()
        hist = self.hist_month
        if hist.empty:
            return "No historical data available."
        # Calculate daily percent change
        hist = hist.copy()
        hist["Pct Change"] = hist["Close"].pct_change() * 100
        hist = hist.dropna()
        # Calculate volatility (std dev of daily returns)
        volatility = hist["Pct Change"].std()
        # Format as table
        table = "Date       | Close    | % Change\n"
        table += "-----------|----------|---------\n"
        for idx, row in hist.iterrows():
            table += f"{idx.date()} | {row['Close']:.2f} | {row['Pct Change']:+.2f}%\n"
        table += f"\nVolatility (std dev of daily % change): {volatility:.2f}%"
        return table

if __name__ == "__main__":
    fetcher = StockDataFetcher("AAPL")
    data = fetcher.get_data()
    print("Apple (AAPL) Stock Data:")
    for key, value in data.items():
        if key == "recentNews":
            print("Recent News Headlines:")
            for headline in value:
                print(f"  - {headline}")
        else:
            print(f"{key}: {value}")
    print("\nDaily Performance Table:")
    print(fetcher.get_daily_performance_table())