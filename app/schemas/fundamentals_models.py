from pydantic import BaseModel
from typing import Literal, Optional


class QuarterlySnapshot(BaseModel):
    quarter:          str
    revenue:          Optional[float]
    net_income:       Optional[float]
    gross_profit:     Optional[float]
    ebitda:           Optional[float]
    eps_estimate:     Optional[float]
    eps_actual:       Optional[float]
    eps_surprise_pct: Optional[float]
    beat:             Optional[bool]


class GrowthMetrics(BaseModel):
    revenue_growth_yoy:  Optional[float]
    earnings_growth_yoy: Optional[float]
    revenue_trend:       str    # "accelerating" | "decelerating" | "stable"
    earnings_trend:      str


class ProfitabilityMetrics(BaseModel):
    gross_margin:     Optional[float]
    operating_margin: Optional[float]
    net_margin:       Optional[float]
    roe:              Optional[float]
    roa:              Optional[float]
    free_cash_flow:   Optional[float]
    ebitda:           Optional[float]
    quality:          str    # "high" | "medium" | "low"


class ValuationMetrics(BaseModel):
    pe_ratio:   Optional[float]
    forward_pe: Optional[float]
    peg_ratio:  Optional[float]
    ps_ratio:   Optional[float]
    pb_ratio:   Optional[float]
    ev_ebitda:  Optional[float]
    verdict:    str    # "undervalued" | "fair" | "overvalued"


class BalanceSheetHealth(BaseModel):
    debt_to_equity: Optional[float]
    current_ratio:  Optional[float]
    total_cash:     Optional[float]
    total_debt:     Optional[float]
    net_cash:       Optional[float]
    health:         str    # "strong" | "adequate" | "leveraged"


class AnalystConsensus(BaseModel):
    recommendation:   str
    num_analysts:     Optional[int]
    target_mean:      Optional[float]
    target_high:      Optional[float]
    target_low:       Optional[float]
    upside_to_target: Optional[float]


class SECEvent(BaseModel):
    title:      str
    filed_date: str
    url:        str
    event_type: str


class GovContract(BaseModel):
    award_id:    Optional[str]
    recipient:   Optional[str]
    amount:      Optional[float]
    description: Optional[str]
    agency:      Optional[str]
    start_date:  Optional[str]
    end_date:    Optional[str]


class FundamentalsOutput(BaseModel):
    ticker:        str
    company_name:  Optional[str]
    sector:        Optional[str]
    industry:      Optional[str]
    market_cap:    Optional[float]
    next_earnings: Optional[str]

    quarterly_trend:   list[QuarterlySnapshot]
    growth:            GrowthMetrics
    profitability:     ProfitabilityMetrics
    valuation:         ValuationMetrics
    balance_sheet:     BalanceSheetHealth
    analyst_consensus: AnalystConsensus
    sec_events:        list[SECEvent]
    gov_contracts:     list[GovContract]

    overall_signal:     Literal["strong_buy", "buy", "neutral", "sell", "strong_sell"]
    fundamental_score:  float        # –10 to +10
    key_strengths:      list[str]    # exactly 3
    key_risks:          list[str]    # exactly 3
    reasoning:          str          # 4–5 sentence narrative