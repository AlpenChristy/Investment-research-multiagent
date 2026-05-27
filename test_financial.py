import asyncio
from app.services.market_data import fetch_market_data
from app.agents.financial_agent import FinancialAgent
from dotenv import load_dotenv

load_dotenv()

async def main():
    market_data = fetch_market_data("NVDA")
    print("Data fetched:", list(market_data.keys()))

    agent = FinancialAgent()
    result = await agent.run("NVDA", market_data)

    print("\n--- Financial Output ---")
    print(result.model_dump_json(indent=2))

asyncio.run(main())