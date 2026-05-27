from app.schemas.models import BearOutput
from app.prompts.bear import BEAR_PROMPT
from app.services.llm_service import call_llm


class BearAgent:
    async def run(
        self,
        ticker: str,
        market_data: dict,
        news_data: dict,
    ) -> BearOutput:
        formatted_headlines = "\n".join([
            f"- [{a['source']}] {a['title']}"
            for a in news_data.get("headlines", [])[:10]
        ])

        prompt = BEAR_PROMPT.format(
            ticker=ticker,
            market_data=market_data,
            news_data=formatted_headlines,
        )
        raw = await call_llm(prompt)
        return BearOutput.model_validate_json(raw)