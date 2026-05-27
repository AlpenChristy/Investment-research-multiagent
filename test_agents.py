import asyncio
from app.services.market_data import fetch_market_data
from app.services.news_service import fetch_news
from app.agents.financial_agent import FinancialAgent
from app.agents.news_agent import NewsAgent
from app.agents.risk_agent import RiskAgent
from app.agents.bull_agent import BullAgent
from app.agents.bear_agent import BearAgent
from dotenv import load_dotenv

load_dotenv()

async def main():
    ticker = "NVDA"

    print("Fetching data...")
    market_data = fetch_market_data(ticker)
    news_data   = await fetch_news(ticker, company_name="NVIDIA")

    print("Running all five agents in parallel...")
    results = await asyncio.gather(
        FinancialAgent().run(ticker, market_data),
        NewsAgent().run(ticker, news_data),
        RiskAgent().run(ticker, market_data),
        BullAgent().run(ticker, market_data, news_data),
        BearAgent().run(ticker, market_data, news_data),
        return_exceptions=True
    )

    names = ["Financial", "News", "Risk", "Bull", "Bear"]
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            print(f"\n--- {name}: FAILED ---")
            print(result)
        else:
            print(f"\n--- {name}: OK ---")
            print(result.model_dump_json(indent=2))

asyncio.run(main())