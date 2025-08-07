from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from datetime import datetime
from get_finance import is_valid_ticker
import os
import re

from dotenv import load_dotenv
load_dotenv()

def log(message):
    print(f"[{datetime.now().isoformat()}] {message}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a highly aggressive day trader focused on short-term explosive stock moves.

Your job is to identify ONE stock that is likely to spike at least 10% TODAY based on a **very recent catalyst** something that happened in the last 24 hours, ideally within the last few hours possibly minutes.

You may justify your pick using:
- Politician trading disclosures (recent House/Senate buys)
- Breaking news, earnings, PRs, FDA decisions, or regulatory events
- Reddit, Twitter, Discord, or Stocktwits hype
- Unusual intraday volume or price action
- Sector momentum from global events (wars, hacks, disasters, sanctions, etc.)

✅ You may pick large-cap stocks **only if the catalyst is strong enough to realistically drive a 10%+ move today**  
🚫 Do NOT suggest “safe” or generic picks — only stocks with serious upside potential due to a current catalyst

🧠 Be bold. Be decisive. Pick the one stock with the highest probability of surging hard today.

🎯 Output format:
TICKER  
One short sentence describing the catalyst behind your pick.

Nothing else. No disclaimers. No alternatives. Just the ticker and a one-liner reason.
"""

def single_stock_picker(existing_tickers, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": PROMPT_TEMPLATE}],
                temperature=1.2,
            )
            content = response.choices[0].message.content.strip()

            # Parse ticker and reason
            match = re.match(r"^([A-Z]{1,5})[:\-–\s]+(.+)$", content)
            if match:
                ticker = match.group(1).strip()
                reason = match.group(2).strip()
            else:
                ticker = "UNKNOWN"
                reason = content

            # Validate ticker and check for duplicates
            if ticker != "UNKNOWN" and is_valid_ticker(ticker):
                if ticker in existing_tickers:
                    log(f"[Retry {attempt+1}] Duplicate ticker: '{ticker}'")
                else:
                    return {"ticker": ticker, "reason": reason}
            else:
                log(f"[Retry {attempt+1}] Invalid ticker: '{ticker}'")

        except Exception as e:
            log(f"[Retry {attempt+1}] Error: {str(e)}")

    return {"ticker": "ERROR", "reason": "Exceeded retry limit or invalid/duplicate ticker"}


def run_multiple_agents(agent_count=10):
    results = []
    seen_tickers = set()

    with ThreadPoolExecutor(max_workers=agent_count) as executor:
        futures = []

        for _ in range(agent_count):
            futures.append(
                executor.submit(single_stock_picker, seen_tickers.copy())  # pass copy to avoid race conditions
            )

        for future in futures:
            result = future.result()
            ticker = result["ticker"]
            if ticker != "ERROR" and ticker not in seen_tickers:
                seen_tickers.add(ticker)
                results.append(result)
            else:
                log(f"Duplicate or error: {ticker}")

    return results
    
# Local testing
if __name__ == "__main__":
    print("Running GPT agents...\n")
    picks = run_multiple_agents(10)

    for i, pick in enumerate(picks, 1):
        print(f"Agent {i}:")
        print(f"  Ticker: {pick['ticker']}")
        print(f"  Reason: {pick['reason']}\n")