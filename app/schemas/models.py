from __future__ import annotations
from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from datetime import datetime

#AnalysisRequest — what comes in from the user
class AnalysisRequest(BaseModel):
    ticker: str
    analysis_type: Literal["long_term", "short_term"] = "long_term"

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_valid(cls, v):
        v = v.upper().strip()
        if not v.isalpha() or len(v) > 5:
            raise ValueError("ticker must be 1–5 letters, e.g. NVDA")
        return v


#Five agent output schemas
class FinancialOutput(BaseModel):
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    metrics: dict[str, float | str]
    score: float                        # 0–10, overall financial health

class NewsOutput(BaseModel):
    sentiment: Literal["bullish", "neutral", "bearish"]
    confidence: float                   # 0–1
    key_topics: list[str]
    headlines: list[str]

class RiskOutput(BaseModel):
    macro_risks: list[str]
    valuation_concern: str
    competition: str
    regulation: str
    risk_level: Literal["low", "medium", "high"]

class BullOutput(BaseModel):
    bull_thesis: str
    catalysts: list[str]               # specific upcoming events
    upside_target: str                 # e.g. "$950 in 12 months"
    conviction: float                  # 0–1
    timeframe: str

class BearOutput(BaseModel):
    bear_thesis: str
    risks: list[str]
    downside_target: str
    conviction: float                  # 0–1
    timeframe: str

#AgentOutputs — what the synthesizer receives
class AgentOutputs(BaseModel):
    financial: Optional[FinancialOutput] = None
    news:      Optional[NewsOutput]      = None
    risk:      Optional[RiskOutput]      = None
    bull:      Optional[BullOutput]      = None
    bear:      Optional[BearOutput]      = None

    def all_failed(self) -> bool:
        return all(v is None for v in [
            self.financial, self.news, self.risk, self.bull, self.bear
        ])

    def available_count(self) -> int:
        return sum(1 for v in [
            self.financial, self.news, self.risk, self.bull, self.bear
        ] if v is not None)

#FinalThesis — synthesizer output
class FinalThesis(BaseModel):
    recommendation: Literal["BUY", "HOLD", "SELL"]
    confidence:     float        # 0–100
    reasoning:      str
    bull_summary:   str
    bear_summary:   str
    key_risks:      list[str]
    key_catalysts:  list[str]

#AnalysisReport — the final API response
class AnalysisReport(BaseModel):
    ticker:          str
    analysis_type:   str
    recommendation:  Literal["BUY", "HOLD", "SELL"]
    confidence:      float
    reasoning:       str
    bull_summary:    str
    bear_summary:    str
    key_risks:       list[str]
    key_catalysts:   list[str]
    agent_outputs:   AgentOutputs
    agents_used:     int
    processing_time_ms: int
    timestamp:       datetime = datetime.utcnow()

#Technical Analysis
class IndicatorSignal(BaseModel):
    name: str
    value: float | None
    signal: Literal["bullish", "bearish", "neutral"]
    interpretation: str          # one sentence, plain English

class KeyLevels(BaseModel):
    support:    float            # strongest nearby floor
    resistance: float            # strongest nearby ceiling
    high_52w:   float
    low_52w:    float

class TAOutput(BaseModel):
    ticker:          str
    price:           float
    overall_signal:  Literal["strong_buy", "buy", "neutral", "sell", "strong_sell"]
    signal_score:    float                # –10 to +10
    confluence:      int                  # how many indicators agree with overall signal
    trend:           list[IndicatorSignal]
    momentum:        list[IndicatorSignal]
    volatility:      list[IndicatorSignal]
    volume:          list[IndicatorSignal]
    key_levels:      KeyLevels
    reasoning:       str                  # 3–4 sentence narrative


# paste this at the bottom of models.py temporarily, then delete it
if __name__ == "__main__":
    r = AnalysisRequest(ticker="nvda")
    print(r.ticker)   # should print NVDA