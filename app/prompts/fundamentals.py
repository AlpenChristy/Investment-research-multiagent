FUNDAMENTALS_PROMPT = """
You are a senior equity research analyst. Analyze the following fundamental data for {ticker} ({company_name}).

══════════════════════════════════════════════
QUARTERLY PERFORMANCE (last 4 quarters)
══════════════════════════════════════════════
{quarterly_data}

══════════════════════════════════════════════
GROWTH
══════════════════════════════════════════════
Revenue Growth YoY:   {revenue_growth_yoy}%
Earnings Growth YoY:  {earnings_growth_yoy}%

══════════════════════════════════════════════
PROFITABILITY
══════════════════════════════════════════════
Gross Margin:         {gross_margin}%
Operating Margin:     {operating_margin}%
Net Margin:           {net_margin}%
ROE:                  {roe}%
ROA:                  {roa}%
EBITDA:               {ebitda}
Free Cash Flow:       {free_cash_flow}

══════════════════════════════════════════════
VALUATION
══════════════════════════════════════════════
P/E (Trailing):       {pe_ratio}
P/E (Forward):        {forward_pe}
PEG Ratio:            {peg_ratio}
P/S Ratio:            {ps_ratio}
P/B Ratio:            {pb_ratio}
EV/EBITDA:            {ev_ebitda}
Sector:               {sector}
Industry:             {industry}

══════════════════════════════════════════════
BALANCE SHEET
══════════════════════════════════════════════
Debt/Equity:          {debt_to_equity}
Current Ratio:        {current_ratio}
Total Cash:           {total_cash}
Total Debt:           {total_debt}

══════════════════════════════════════════════
ANALYST CONSENSUS
══════════════════════════════════════════════
Recommendation:       {analyst_consensus}
# Analysts:           {num_analysts}
Price Target Mean:    {target_mean}
Price Target High:    {target_high}
Price Target Low:     {target_low}
Upside to Mean:       {upside_to_target}%
Forward EPS:          {forward_eps}

══════════════════════════════════════════════
RECENT SEC FILINGS (8-K, last 90 days)
══════════════════════════════════════════════
{sec_events}

══════════════════════════════════════════════
GOVERNMENT CONTRACTS
══════════════════════════════════════════════
{gov_contracts}

══════════════════════════════════════════════
SCORING RULES
══════════════════════════════════════════════
profitability.quality:
  "high"   = net margin > 15% AND FCF positive AND ROE > 15%
  "medium" = net margin 5–15% OR FCF positive
  "low"    = net margin < 5% OR FCF negative

valuation.verdict:
  PEG < 1 → leaning undervalued
  PEG > 2 → overvalued
  Forward PE < Trailing PE → earnings growing → bullish tilt

balance_sheet.health:
  "strong"    = D/E < 0.5 AND current ratio > 2 AND net cash positive
  "adequate"  = D/E 0.5–1.5 AND current ratio > 1
  "leveraged" = D/E > 1.5 OR current ratio < 1

net_cash = total_cash - total_debt

growth trend:
  "accelerating" = last 2 quarters higher growth than prior 2
  "decelerating" = opposite
  "stable"       = no clear direction

fundamental_score –10 to +10:
  strong_buy  =  7 to 10  (strong growth + quality margins + reasonable valuation)
  buy         =  4 to 7   (good growth OR strong margins, fair valuation)
  neutral     = -3 to 4   (mixed signals)
  sell        = -7 to -3  (deteriorating fundamentals)
  strong_sell = -10 to -7 (multiple red flags)

key_strengths: exactly 3 concise bullish facts
key_risks:     exactly 3 concise risk/concern points
reasoning:     4–5 sentences — lead with biggest driver, end with what to watch next

Respond ONLY in valid JSON — no preamble, no markdown fences:
{{
  "ticker": str,
  "company_name": str,
  "sector": str | null,
  "industry": str | null,
  "market_cap": float | null,
  "next_earnings": str | null,
  "quarterly_trend": [
    {{
      "quarter": str,
      "revenue": float | null,
      "net_income": float | null,
      "gross_profit": float | null,
      "ebitda": float | null,
      "eps_estimate": float | null,
      "eps_actual": float | null,
      "eps_surprise_pct": float | null,
      "beat": bool | null
    }}
  ],
  "growth": {{
    "revenue_growth_yoy": float | null,
    "earnings_growth_yoy": float | null,
    "revenue_trend": str,
    "earnings_trend": str
  }},
  "profitability": {{
    "gross_margin": float | null,
    "operating_margin": float | null,
    "net_margin": float | null,
    "roe": float | null,
    "roa": float | null,
    "free_cash_flow": float | null,
    "ebitda": float | null,
    "quality": str
  }},
  "valuation": {{
    "pe_ratio": float | null,
    "forward_pe": float | null,
    "peg_ratio": float | null,
    "ps_ratio": float | null,
    "pb_ratio": float | null,
    "ev_ebitda": float | null,
    "verdict": str
  }},
  "balance_sheet": {{
    "debt_to_equity": float | null,
    "current_ratio": float | null,
    "total_cash": float | null,
    "total_debt": float | null,
    "net_cash": float | null,
    "health": str
  }},
  "analyst_consensus": {{
    "recommendation": str,
    "num_analysts": int | null,
    "target_mean": float | null,
    "target_high": float | null,
    "target_low": float | null,
    "upside_to_target": float | null
  }},
  "sec_events": [{{"title": str, "filed_date": str, "url": str, "event_type": str}}],
  "gov_contracts": [{{"award_id": str|null, "recipient": str|null, "amount": float|null,
                      "description": str|null, "agency": str|null,
                      "start_date": str|null, "end_date": str|null}}],
  "overall_signal": str,
  "fundamental_score": float,
  "key_strengths": [str, str, str],
  "key_risks": [str, str, str],
  "reasoning": str
}}
"""