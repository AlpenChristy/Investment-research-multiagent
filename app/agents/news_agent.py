from app.schemas.models import NewsOutput
from app.prompts.news import NEWS_PROMPT
from app.services.llm_service import call_llm


class NewsAgent:
    async def run(self, ticker: str, news_data: dict) -> NewsOutput:
        formatted_headlines = "\n".join([
            f"- [{a['source']}] {a['title']} | {a['description']}"
            for a in news_data.get("headlines", [])[:15]   # cap at 15 to stay within token budget
        ])

        prompt = NEWS_PROMPT.format(
            ticker=ticker,
            news_data=formatted_headlines,
        )
        raw = await call_llm(prompt)
        return NewsOutput.model_validate_json(raw)