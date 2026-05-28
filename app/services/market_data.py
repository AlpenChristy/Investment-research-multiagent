# pyrefly: ignore [missing-import]
import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests


def fetch_market_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info  = stock.info

    return {
        "ticker":          ticker,
        "current_price":   info.get("currentPrice"),
        "pe_ratio":        info.get("trailingPE"),
        "forward_pe":      info.get("forwardPE"),
        "revenue_growth":  info.get("revenueGrowth"),
        "gross_margins":   info.get("grossMargins"),
        "net_margins":     info.get("profitMargins"),
        "debt_to_equity":  info.get("debtToEquity"),
        "free_cashflow":   info.get("freeCashflow"),
        "market_cap":      info.get("marketCap"),
        "sector":          info.get("sector"),
        "summary":         info.get("longBusinessSummary", "")[:500],
    }

# ─────────────────────────────────────────────
# fetch_financials now accepts the already-fetched
# market_data dict and only pulls what's missing
# from it (quarterly history, EPS beat/miss).
# ─────────────────────────────────────────────

async def fetch_financials(ticker: str, market_data: dict) -> dict:
    t = yf.Ticker(ticker)

    # quarterly history — not in market_data, need direct call
    q_fin = t.quarterly_financials

    def safe(df, row):
        try:
            series = df.loc[row].dropna()
            return {str(col.date()): round(float(val), 2) for col, val in series.items()}
        except Exception:
            return {}

    quarterly_revenue  = safe(q_fin, "Total Revenue")
    quarterly_earnings = safe(q_fin, "Net Income")
    quarterly_ebitda   = safe(q_fin, "EBITDA")
    quarterly_gross    = safe(q_fin, "Gross Profit")

    # EPS beat/miss history — not in market_data
    try:
        earn_dates = t.earnings_dates.dropna(subset=["EPS Estimate", "Reported EPS"])
        beat_miss  = []
        for date, row in earn_dates.head(6).iterrows():
            est    = float(row["EPS Estimate"])
            actual = float(row["Reported EPS"])
            surprise_pct = round(((actual - est) / abs(est)) * 100, 2) if est != 0 else 0
            beat_miss.append({
                "date":         str(date.date()),
                "eps_estimate": est,
                "eps_actual":   actual,
                "surprise_pct": surprise_pct,
                "beat":         actual >= est,
            })
    except Exception:
        beat_miss = []

    info = t.info

    return {
        # ── reuse what market_data already fetched ──────────
        "current_price":    market_data.get("current_price"),
        "pe_ratio":         market_data.get("pe_ratio"),
        "forward_pe":       market_data.get("forward_pe"),
        "revenue_growth_yoy": round(market_data["revenue_growth"] * 100, 2)
                               if market_data.get("revenue_growth") else None,
        "gross_margin":     round(market_data["gross_margins"] * 100, 2)
                               if market_data.get("gross_margins") else None,
        "net_margin":       round(market_data["net_margins"] * 100, 2)
                               if market_data.get("net_margins") else None,
        "debt_to_equity":   market_data.get("debt_to_equity"),
        "free_cash_flow":   market_data.get("free_cashflow"),
        "market_cap":       market_data.get("market_cap"),
        "sector":           market_data.get("sector"),

        # ── extras not in market_data — single info call ────
        "company_name":      info.get("longName"),
        "industry":          info.get("industry"),
        "ebitda":            info.get("ebitda"),
        "operating_margin":  round(info["operatingMargins"] * 100, 2)
                              if info.get("operatingMargins") else None,
        "peg_ratio":         info.get("pegRatio"),
        "ps_ratio":          info.get("priceToSalesTrailing12Months"),
        "pb_ratio":          info.get("priceToBook"),
        "ev_ebitda":         info.get("enterpriseToEbitda"),
        "roe":               round(info["returnOnEquity"] * 100, 2)
                              if info.get("returnOnEquity") else None,
        "roa":               round(info["returnOnAssets"] * 100, 2)
                              if info.get("returnOnAssets") else None,
        "total_cash":        info.get("totalCash"),
        "total_debt":        info.get("totalDebt"),
        "earnings_growth_yoy": round(info["earningsGrowth"] * 100, 2)
                                if info.get("earningsGrowth") else None,
        "next_earnings_date": info.get("earningsDate", [None])[0],

        # ── quarterly history (new fetches) ─────────────────
        "quarterly_revenue":  quarterly_revenue,
        "quarterly_earnings": quarterly_earnings,
        "quarterly_ebitda":   quarterly_ebitda,
        "quarterly_gross":    quarterly_gross,
        "eps_history":        beat_miss,
    }


async def fetch_estimates(ticker: str) -> dict:
    t    = yf.Ticker(ticker)
    info = t.info

    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    target_mean   = info.get("targetMeanPrice")
    upside = None
    if target_mean and current_price:
        upside = round(((target_mean - current_price) / current_price) * 100, 2)

    return {
        "current_price":     current_price,
        "target_high":       info.get("targetHighPrice"),
        "target_low":        info.get("targetLowPrice"),
        "target_mean":       target_mean,
        "target_median":     info.get("targetMedianPrice"),
        "upside_to_target":  upside,
        "analyst_consensus": info.get("recommendationKey"),
        "num_analysts":      info.get("numberOfAnalystOpinions"),
        "forward_eps":       info.get("forwardEps"),
        "forward_pe":        info.get("forwardPE"),
    }


async def fetch_sec_events(ticker: str, lookback_days: int = 90) -> list[dict]:
    try:
        headers    = {"User-Agent": "research-agent contact@example.com"}
        search_url = (
            f"https://www.sec.gov/cgi-bin/browse-edgar"
            f"?company=&CIK={ticker}&type=8-K&dateb=&owner=include"
            f"&count=10&search_text=&action=getcompany&output=atom"
        )
        r = requests.get(search_url, headers=headers, timeout=10)

        import xml.etree.ElementTree as ET
        ns     = {"atom": "http://www.w3.org/2005/Atom"}
        root   = ET.fromstring(r.text)
        cutoff = datetime.now() - timedelta(days=lookback_days)
        events = []

        for entry in root.findall("atom:entry", ns)[:10]:
            title      = entry.findtext("atom:title",   default="", namespaces=ns)
            updated    = entry.findtext("atom:updated", default="", namespaces=ns)
            link       = entry.find("atom:link", ns)
            url        = link.attrib.get("href", "") if link is not None else ""

            try:
                filed_date = datetime.fromisoformat(updated[:10])
            except Exception:
                continue

            if filed_date < cutoff:
                continue

            events.append({
                "title":      title,
                "filed_date": str(filed_date.date()),
                "url":        url,
                "event_type": _classify_8k(title),
            })

        return events

    except Exception as e:
        return [{"error": str(e)}]


def _classify_8k(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["earnings", "results", "quarter", "revenue"]):
        return "earnings_release"
    if any(k in t for k in ["acqui", "merger", "purchase", "agreement"]):
        return "ma_event"
    if any(k in t for k in ["contract", "award", "order"]):
        return "contract_order"
    if any(k in t for k in ["guidance", "outlook", "forecast"]):
        return "guidance"
    if any(k in t for k in ["dividend", "buyback", "repurchase"]):
        return "capital_return"
    if any(k in t for k in ["officer", "director", "appoint", "resign"]):
        return "leadership_change"
    return "other"


async def fetch_gov_contracts(company_name: str, limit: int = 5) -> list[dict]:
    try:
        url     = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
        payload = {
            "filters": {
                "keywords":         [company_name],
                "award_type_codes": ["A", "B", "C", "D"],
                "time_period": [{
                    "start_date": "2023-01-01",
                    "end_date":   datetime.now().strftime("%Y-%m-%d"),
                }],
            },
            "fields": [
                "Award ID", "Recipient Name", "Award Amount", "Description",
                "Period of Performance Start Date",
                "Period of Performance Current End Date",
                "Awarding Agency Name",
            ],
            "sort":  "Award Amount",
            "order": "desc",
            "limit": limit,
        }
        r    = requests.post(url, json=payload, timeout=15)
        data = r.json()

        return [
            {
                "award_id":    a.get("Award ID"),
                "recipient":   a.get("Recipient Name"),
                "amount":      a.get("Award Amount"),
                "description": a.get("Description"),
                "agency":      a.get("Awarding Agency Name"),
                "start_date":  a.get("Period of Performance Start Date"),
                "end_date":    a.get("Period of Performance Current End Date"),
            }
            for a in data.get("results", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]

async def fetch_ohlcv(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")
    df.columns = [c.lower() for c in df.columns]
    df.dropna(inplace=True)
    return df


if __name__ == "__main__":
    print(fetch_market_data("AAPL"))
