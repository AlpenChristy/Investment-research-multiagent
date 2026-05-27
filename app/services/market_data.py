# pyrefly: ignore [missing-import]
import yfinance as yf


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

if __name__ == "__main__":
    print(fetch_market_data("BEL.NS"))