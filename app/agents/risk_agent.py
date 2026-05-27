from app.schemas.models import RiskOutput
from app.prompts.risk import RISK_PROMPT
from app.services.llm_service import call_llm


class RiskAgent:
    async def run(self, ticker: str, market_data: dict) -> RiskOutput:
        prompt = RISK_PROMPT.format(
            ticker=ticker,
            market_data=market_data,
        )
        raw = await call_llm(prompt)
        return RiskOutput.model_validate_json(raw)