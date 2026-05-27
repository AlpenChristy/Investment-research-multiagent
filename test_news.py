import asyncio
from app.services.news_service import fetch_news
from app.agents.news_agent import NewsAgent
from dotenv import load_dotenv

load_dotenv()

async def main():
    news_data = await fetch_news("NVDA", company_name="NVIDIA")
    print(f"Fetched {news_data['count']} articles")

    agent = NewsAgent()
    result = await agent.run("NVDA", news_data)

    print("\n--- News Output ---")
    print(result.model_dump_json(indent=2))

asyncio.run(main())