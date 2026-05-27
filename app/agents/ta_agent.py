from app.schemas.models import TAOutput
from app.prompts.ta import TA_PROMPT
from app.services.llm_service import call_llm

class TAAgent:
    async def run(self, ticker: str, indicators: dict) -> TAOutput:
        prompt = TA_PROMPT.format(ticker=ticker, **indicators)
        raw = await call_llm(prompt)
        return TAOutput.model_validate_json(raw)