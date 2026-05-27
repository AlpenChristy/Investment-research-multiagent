import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def fetch_news(ticker: str, company_name: str = "") -> dict:
    api_key = os.getenv("NEWSAPI_KEY")
    query   = company_name if company_name else ticker

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q":        query,
                "apiKey":   api_key,
                "pageSize": 20,
                "sortBy":   "publishedAt",
                "language": "en",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

    articles = data.get("articles", [])

    headlines = [
        {
            "title":       a.get("title", ""),
            "description": a.get("description", ""),
            "source":      a.get("source", {}).get("name", ""),
            "published":   a.get("publishedAt", ""),
        }
        for a in articles
        if a.get("title") and "[Removed]" not in a.get("title", "")
    ]

    return {
        "ticker":     ticker,
        "query":      query,
        "count":      len(headlines),
        "headlines":  headlines,
    }

if __name__ == "__main__":
    import asyncio
    news_data = asyncio.run(fetch_news("NVDA"))
    print(news_data)