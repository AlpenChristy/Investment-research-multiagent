from app.schemas.models import BullOutput
from app.prompts.bull import BULL_PROMPT
from app.services.llm_service import call_llm


class BullAgent:
    async def run(
        self,
        ticker: str,
        market_data: dict,
        news_data: dict,
    ) -> BullOutput:
        formatted_headlines = "\n".join([
            f"- [{a['source']}] {a['title']}"
            for a in news_data.get("headlines", [])[:10]
        ])

        prompt = BULL_PROMPT.format(
            ticker=ticker,
            market_data=market_data,
            news_data=formatted_headlines,
        )
        raw = await call_llm(prompt)
        return BullOutput.model_validate_json(raw)