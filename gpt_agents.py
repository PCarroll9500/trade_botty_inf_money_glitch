from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are a highly aggressive day trader specializing in short-term stock spikes.

Your job is to identify ONE stock that is likely to surge at least 10% TODAY due to a **very recent catalyst** — something that happened in the past 24 hours, ideally the past few hours.

You may use any of the following to justify your pick:
- Politician trading disclosures (House/Senate reports, especially recent buys)
- Breaking news, rumors, press releases, or regulatory events
- Social media hype (Reddit, Twitter/X, Stocktwits, Discord, etc.)
- Unusual trading volume or price movement this morning
- Sector momentum from recent global events (e.g. war, cyberattacks, sanctions, natural disasters, etc.)

Avoid safe or large-cap names like AAPL, TSLA, MSFT, AMZN, etc. Focus instead on bold, under-the-radar stocks — small-caps, penny stocks, low-float runners, etc.

Your response must include ONLY:
- The stock's TICKER SYMBOL (uppercase)
- One short sentence describing the **recent catalyst** behind your pick

No disclaimers. No alternative picks. No extra commentary. Be decisive and bold.

"""

def single_stock_picker():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": PROMPT_TEMPLATE}],
        temperature=1.2,  # High creativity for diversification
    )
    return response.choices[0].message.content.strip()

def run_multiple_agents(agent_count=10):
    with ThreadPoolExecutor(max_workers=agent_count) as executor:
        return list(executor.map(lambda _: single_stock_picker(), range(agent_count)))
    
# Local testing
if __name__ == "__main__":
    print("Running GPT agents...\n")
    picks = run_multiple_agents(1)
    for i, pick in enumerate(picks, 1):
        print(f"Agent {i}: {pick}")