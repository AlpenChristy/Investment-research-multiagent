from app.schemas.fundamentals_models import FundamentalsOutput
from app.prompts.fundamentals import FUNDAMENTALS_PROMPT
from app.services.llm_service import call_llm


def _fmt(val):
    return val if val is not None else "N/A"


def _fmt_quarterly(financials: dict) -> str:
    q_rev    = financials.get("quarterly_revenue", {})
    q_earn   = financials.get("quarterly_earnings", {})
    q_gp     = financials.get("quarterly_gross", {})
    q_ebit   = financials.get("quarterly_ebitda", {})
    eps_hist = financials.get("eps_history", [])

    all_dates  = sorted(set(list(q_rev.keys()) + list(q_earn.keys())), reverse=True)[:4]
    eps_by_date = {e["date"][:7]: e for e in eps_hist}

    lines = []
    for d in all_dates:
        eps = eps_by_date.get(d[:7], {})
        lines.append(
            f"  {d} | Rev: {q_rev.get(d,'N/A'):>15} | "
            f"NetInc: {q_earn.get(d,'N/A'):>15} | "
            f"GrossP: {q_gp.get(d,'N/A'):>15} | "
            f"EBITDA: {q_ebit.get(d,'N/A'):>15} | "
            f"EPS est: {eps.get('eps_estimate','N/A')} "
            f"actual: {eps.get('eps_actual','N/A')} "
            f"surprise: {eps.get('surprise_pct','N/A')}%"
        )
    return "\n".join(lines) if lines else "No quarterly data available"


def _fmt_sec(events: list[dict]) -> str:
    if not events:
        return "No recent 8-K filings found"
    lines = []
    for e in events[:8]:
        if "error" in e:
            return f"SEC fetch error: {e['error']}"
        lines.append(f"  [{e['filed_date']}] ({e['event_type']}) {e['title']}\n  {e['url']}")
    return "\n".join(lines)


def _fmt_contracts(contracts: list[dict]) -> str:
    if not contracts:
        return "No government contracts found"
    lines = []
    for c in contracts[:5]:
        if "error" in c:
            return f"Contracts fetch error: {c['error']}"
        amt = f"${c['amount']:,.0f}" if c.get("amount") else "N/A"
        lines.append(
            f"  {amt} | {c.get('agency','N/A')} | "
            f"{c.get('start_date','?')} – {c.get('end_date','?')}\n"
            f"  {c.get('description','')[:120]}"
        )
    return "\n".join(lines)


class FundamentalsAgent:
    async def run(
        self,
        ticker:        str,
        financials:    dict,
        estimates:     dict,
        sec_events:    list[dict],
        gov_contracts: list[dict],
    ) -> FundamentalsOutput:

        prompt = FUNDAMENTALS_PROMPT.format(
            ticker=ticker,
            company_name=financials.get("company_name", ticker),

            quarterly_data=_fmt_quarterly(financials),

            revenue_growth_yoy=_fmt(financials.get("revenue_growth_yoy")),
            earnings_growth_yoy=_fmt(financials.get("earnings_growth_yoy")),

            gross_margin=_fmt(financials.get("gross_margin")),
            operating_margin=_fmt(financials.get("operating_margin")),
            net_margin=_fmt(financials.get("net_margin")),
            roe=_fmt(financials.get("roe")),
            roa=_fmt(financials.get("roa")),
            ebitda=_fmt(financials.get("ebitda")),
            free_cash_flow=_fmt(financials.get("free_cash_flow")),

            pe_ratio=_fmt(financials.get("pe_ratio")),
            forward_pe=_fmt(financials.get("forward_pe")),
            peg_ratio=_fmt(financials.get("peg_ratio")),
            ps_ratio=_fmt(financials.get("ps_ratio")),
            pb_ratio=_fmt(financials.get("pb_ratio")),
            ev_ebitda=_fmt(financials.get("ev_ebitda")),
            sector=_fmt(financials.get("sector")),
            industry=_fmt(financials.get("industry")),

            debt_to_equity=_fmt(financials.get("debt_to_equity")),
            current_ratio=_fmt(financials.get("current_ratio")),
            total_cash=_fmt(financials.get("total_cash")),
            total_debt=_fmt(financials.get("total_debt")),

            analyst_consensus=_fmt(estimates.get("analyst_consensus")),
            num_analysts=_fmt(estimates.get("num_analysts")),
            target_mean=_fmt(estimates.get("target_mean")),
            target_high=_fmt(estimates.get("target_high")),
            target_low=_fmt(estimates.get("target_low")),
            upside_to_target=_fmt(estimates.get("upside_to_target")),
            forward_eps=_fmt(estimates.get("forward_eps")),

            sec_events=_fmt_sec(sec_events),
            gov_contracts=_fmt_contracts(gov_contracts),
        )

        raw = await call_llm(prompt)
        return FundamentalsOutput.model_validate_json(raw)