from app.schemas.models import FinancialOutput
from app.prompts.financial import FINANCIAL_PROMPT
from app.services.llm_service import call_llm


class FinancialAgent:
    async def run(self, ticker: str, market_data: dict) -> FinancialOutput:
        prompt = FINANCIAL_PROMPT.format(
            ticker=ticker,
            market_data=market_data,
        )
        raw = await call_llm(prompt)
        return FinancialOutput.model_validate_json(raw)