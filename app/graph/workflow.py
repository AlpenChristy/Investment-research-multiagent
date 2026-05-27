import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from app.schemas.models import (
    AgentOutputs, AnalysisReport, FinalThesis,
    FinancialOutput, NewsOutput, RiskOutput, BullOutput, BearOutput,
)
from app.agents.financial_agent import FinancialAgent
from app.agents.news_agent import NewsAgent
from app.agents.risk_agent import RiskAgent
from app.agents.bull_agent import BullAgent
from app.agents.bear_agent import BearAgent
from app.services.market_data import fetch_market_data
from app.services.news_service import fetch_news
from app.services.llm_service import call_llm
from app.prompts.synthesizer import SYNTHESIZER_PROMPT


# ── State ─────────────────────────────────────────────────────────────────────

@dataclass
class AnalysisState:
    ticker:       str
    analysis_type: str
    market_data:  dict = field(default_factory=dict)
    news_data:    dict = field(default_factory=dict)
    outputs:      Optional[AgentOutputs] = None
    thesis:       Optional[FinalThesis]  = None
    start_time:   float = field(default_factory=time.time)


# ── Synthesizer ───────────────────────────────────────────────────────────────

class Synthesizer:
    async def run(self, outputs: AgentOutputs, ticker: str) -> FinalThesis:
        prompt = SYNTHESIZER_PROMPT.format(
            ticker          = ticker,
            financial       = outputs.financial.model_dump_json() if outputs.financial else "unavailable",
            news            = outputs.news.model_dump_json()       if outputs.news      else "unavailable",
            risk            = outputs.risk.model_dump_json()       if outputs.risk      else "unavailable",
            bull            = outputs.bull.model_dump_json()       if outputs.bull      else "unavailable",
            bear            = outputs.bear.model_dump_json()       if outputs.bear      else "unavailable",
            bull_conviction = outputs.bull.conviction              if outputs.bull      else "unavailable",
            bear_conviction = outputs.bear.conviction              if outputs.bear      else "unavailable",
        )
        raw = await call_llm(prompt)
        return FinalThesis.model_validate_json(raw)


# ── Orchestrator ──────────────────────────────────────────────────────────────

class AgentOrchestrator:
    def __init__(self):
        self.financial_agent = FinancialAgent()
        self.news_agent      = NewsAgent()
        self.risk_agent      = RiskAgent()
        self.bull_agent      = BullAgent()
        self.bear_agent      = BearAgent()
        self.synthesizer     = Synthesizer()

    async def run(self, ticker: str, analysis_type: str) -> AnalysisReport:
        state = AnalysisState(ticker=ticker, analysis_type=analysis_type)

        # ── Step 1: fetch data once ───────────────────────────────────────────
        print(f"[{ticker}] Fetching market data and news...")
        state.market_data = fetch_market_data(ticker)
        state.news_data   = await fetch_news(ticker)

        # ── Step 2: run all agents in parallel ────────────────────────────────
        print(f"[{ticker}] Running agents in parallel...")
        results = await asyncio.gather(
            self.financial_agent.run(ticker, state.market_data),
            self.news_agent.run(ticker, state.news_data),
            self.risk_agent.run(ticker, state.market_data),
            self.bull_agent.run(ticker, state.market_data, state.news_data),
            self.bear_agent.run(ticker, state.market_data, state.news_data),
            return_exceptions=True,
        )

        # ── Step 3: separate successes from failures ──────────────────────────
        financial, news, risk, bull, bear = results

        def safe(result, expected_type):
            if isinstance(result, Exception):
                print(f"  Agent failed: {type(result).__name__}: {result}")
                return None
            return result

        state.outputs = AgentOutputs(
            financial = safe(financial, FinancialOutput),
            news      = safe(news,      NewsOutput),
            risk      = safe(risk,      RiskOutput),
            bull      = safe(bull,      BullOutput),
            bear      = safe(bear,      BearOutput),
        )

        print(f"[{ticker}] Agents succeeded: {state.outputs.available_count()}/5")

        # ── Step 4: failure handling ──────────────────────────────────────────
        if state.outputs.all_failed():
            raise RuntimeError(f"All agents failed for ticker {ticker}")

        if state.outputs.available_count() <= 1:
            raise RuntimeError(
                f"Only {state.outputs.available_count()}/5 agents succeeded — "
                "insufficient data to synthesize a recommendation"
            )

        # ── Step 5: synthesize ────────────────────────────────────────────────
        print(f"[{ticker}] Synthesizing final thesis...")
        state.thesis = await self.synthesizer.run(state.outputs, ticker)

        # ── Step 6: build final report ────────────────────────────────────────
        processing_time = int((time.time() - state.start_time) * 1000)
        print(f"[{ticker}] Done in {processing_time}ms")

        return AnalysisReport(
            ticker             = ticker,
            analysis_type      = analysis_type,
            recommendation     = state.thesis.recommendation,
            confidence         = state.thesis.confidence,
            reasoning          = state.thesis.reasoning,
            bull_summary       = state.thesis.bull_summary,
            bear_summary       = state.thesis.bear_summary,
            key_risks          = state.thesis.key_risks,
            key_catalysts      = state.thesis.key_catalysts,
            agent_outputs      = state.outputs,
            agents_used        = state.outputs.available_count(),
            processing_time_ms = processing_time,
            timestamp          = datetime.utcnow(),
        )