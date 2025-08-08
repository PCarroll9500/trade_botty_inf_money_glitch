from utils import log

def main():
    log("🚀 Starting daily trading session...")
    # Ensure OPENAI_API_KEY is set in your environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the OPENAI_API_KEY environment variable.")

    openai_client = OpenAI(api_key=api_key)
    finance_client = FinanceClient()

    picker = StockPicker(
        openai_client,
        finance_client,
        prompt="Pick a stock ticker (1-5 letters) likely to rise at least 10% in the next trading day"
    )
    analyzer = StockAnalyzer(openai_client, finance_client)
    advisor = StockAdvisor(max_risk_level="medium")

    bot = TradeBot(pickers=[picker], analyzers=[analyzer], advisor=advisor)
    bot.run()
    log("✅ Trading session complete.")

if __name__ == '__main__':
    main()