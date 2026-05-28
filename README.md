# 🤖 Investment Research Multi-Agent System

> A production-style multi-agent AI platform that autonomously researches any publicly traded stock and delivers a structured investment thesis — complete with bull/bear debate, technical analysis, fundamental deep-dive, SEC filings, and a synthesized BUY / HOLD / SELL recommendation.

---

## 📌 Overview

This system takes a single ticker symbol (e.g. `NVDA`, `AAPL`, `TSLA`) and orchestrates **6 specialised AI agents** running in parallel to produce a comprehensive, institutional-grade investment report. Each agent is an independent reasoning unit with its own prompt, data context, and Pydantic-validated output schema. A central **Synthesizer** then acts as an investment committee moderator, weighing every agent's conviction score and delivering a final recommendation.

Built with **FastAPI**, **LangGraph**, **OpenAI GPT-4.1-mini**, and **yfinance** — the architecture is intentionally clean, async-first, and designed to scale.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔀 **Parallel Execution** | All agents run concurrently via `asyncio.gather()` — full analysis in seconds, not minutes |
| 🛡️ **Fault-Tolerant** | `return_exceptions=True` ensures one failed agent never crashes the entire run |
| 📐 **Structured Outputs** | Every agent response is validated against a Pydantic schema — no raw LLM text leaks into the report |
| ⚔️ **Bull vs Bear Debate** | Two adversarial agents argue opposite sides; the Synthesizer weighs their conviction scores |
| 📊 **Technical Analysis** | 15+ indicators computed with `pandas-ta` and interpreted by an LLM analyst |
| 📈 **Fundamental Analysis** | Deep-dive into quarterly financials, SEC 8-K filings, government contracts, and analyst consensus |
| 🗞️ **Live News Sentiment** | NewsAPI integration pulls the 20 most recent articles and rates overall sentiment with a confidence score |
| 🏛️ **SEC Filing Tracker** | Monitors recent 8-K filings (earnings releases, M&A events, guidance updates, leadership changes) |
| 🏦 **Gov Contract Intelligence** | Queries USASpending.gov for recent government contract awards — especially relevant for defence/tech stocks |
| 🧠 **LLM Synthesizer** | A senior investment committee moderator persona that weighs all 5 agent outputs into one final thesis |

---

## 🏗️ Architecture

```
POST /analyze  {ticker: "NVDA", analysis_type: "long_term"}
        │
        ▼
 AgentOrchestrator  (app/graph/workflow.py)
        │
        ├── fetch_market_data()   ─── yfinance (shared, fetched once)
        └── fetch_news()          ─── NewsAPI  (shared, fetched once)
        │
        ▼
  asyncio.gather()  ─── all agents run in parallel
  ┌─────────────────────────────────────────────┐
  │  FinancialAgent    NewsAgent    RiskAgent   │
  │  BullAgent         BearAgent               │
  └─────────────────────────────────────────────┘
        │
        ▼
    Synthesizer  ─── weighs conviction scores → FinalThesis
        │
        ▼
    AnalysisReport  ─── structured JSON response
```

The orchestrator owns **data fetching** — agents only own **reasoning**. This prevents redundant API calls, avoids rate limits, and guarantees all agents reason on the same price snapshot.

---

## 🤖 The Agents

### 1. 📊 Financial Agent
**Role:** Quantitative analyst — data-heavy, score-driven.

Receives raw market data (P/E, margins, cash flow, revenue growth, debt ratios) and produces a structured financial health assessment.

**Output:**
```json
{
  "summary": "NVDA shows exceptional financial health...",
  "strengths": ["87% gross margins", "strong FCF generation"],
  "weaknesses": ["elevated forward P/E of 35x", "customer concentration"],
  "metrics": {"pe_ratio": 35.2, "gross_margin": 87.1},
  "score": 8.4
}
```

---

### 2. 🗞️ News / Sentiment Agent
**Role:** Tracks the daily pulse of a stock through recent news headlines.

Calls NewsAPI for the 20 most recent English-language articles about the ticker, then reasons about tone, key narrative themes, and overall market sentiment. The **confidence float** (0–1) is critical — 0.55 means uncertain signal, 0.92 means a clear directional bias.

**Output:**
```json
{
  "sentiment": "bullish",
  "confidence": 0.82,
  "key_topics": ["AI chip demand", "data centre expansion", "export controls"],
  "headlines": ["NVIDIA reports record Q4 revenue..."]
}
```

---

### 3. ⚠️ Risk Agent
**Role:** Structured pessimist — designed to surface what the bulls miss.

Prompted to reason like a risk committee: macro threats, valuation excess, competitive pressure, regulatory exposure. Its `risk_level` field (low / medium / high) is used by the Synthesizer to weight the overall recommendation.

**Output:**
```json
{
  "macro_risks": ["US-China export restrictions", "cyclical slowdown in data centre capex"],
  "valuation_concern": "Trading at 35x forward earnings vs sector average of 22x",
  "competition": "AMD and custom silicon from hyperscalers pose long-term margin risk",
  "regulation": "CHIPS Act compliance and export controls limit addressable market",
  "risk_level": "medium"
}
```

---

### 4. 🐂 Bull Analyst Agent
**Role:** Makes the strongest possible case for buying.

Sees both market data and news, but is explicitly instructed to argue for the position — not evaluate it neutrally. Produces specific upcoming **catalysts** that could drive price appreciation and sets an **upside target**. Its `conviction` score (0–1) is what the Synthesizer weighs against the Bear.

**Output:**
```json
{
  "bull_thesis": "NVDA is the infrastructure layer of the AI revolution...",
  "catalysts": ["Blackwell GPU ramp", "sovereign AI spending wave", "NIM software monetisation"],
  "upside_target": "$1,400 in 12 months",
  "conviction": 0.87,
  "timeframe": "12 months"
}
```

---

### 5. 🐻 Bear Analyst Agent
**Role:** Mirror of the Bull — same inputs, opposite mandate.

Argues the strongest case for caution or selling. The structured debate between Bull and Bear is the "wow factor" of the system — the Synthesizer must explicitly reconcile their conflicting conviction scores in its reasoning.

**Output:**
```json
{
  "bear_thesis": "Valuation leaves no room for execution errors...",
  "risks": ["hyperscaler custom silicon cannibalisation", "export ban escalation", "demand pull-forward"],
  "downside_target": "$700 in 12 months",
  "conviction": 0.61,
  "timeframe": "12 months"
}
```

---

### 6. 🔬 Fundamentals Agent *(deep analysis mode)*
**Role:** Deep-dive CFA-style fundamental analyst.

This is the most data-intensive agent. It receives a much richer data payload and produces a fully structured multi-section report across five analytical dimensions.

**Data inputs:**
- Last 4 quarters of Revenue, Net Income, Gross Profit, EBITDA
- EPS estimate vs actual vs surprise % for each quarter
- YoY revenue and earnings growth rates
- Full profitability suite (Gross / Operating / Net Margin, ROE, ROA, FCF, EBITDA)
- Valuation multiples (P/E, Forward P/E, PEG, P/S, P/B, EV/EBITDA)
- Balance sheet health (D/E, current ratio, total cash, total debt)
- Analyst consensus (rating, # of analysts, price target range, upside %)
- Recent SEC 8-K filings (classified by event type)
- US government contract awards from USASpending.gov

**Structured output sections:**

| Section | Fields |
|---|---|
| `quarterly_trend` | Per-quarter revenue, net income, gross profit, EBITDA, EPS beat/miss |
| `growth` | YoY revenue & earnings growth, trend classification |
| `profitability` | All margin metrics, ROE, ROA, FCF, quality rating |
| `valuation` | 6 valuation multiples + undervalued/fair/overvalued verdict |
| `balance_sheet` | D/E, current ratio, cash, debt, net cash, health rating |
| `analyst_consensus` | Consensus rating, target range, upside to mean target |
| `sec_events` | Recent 8-K filings with classification |
| `gov_contracts` | Government contract awards with amounts and agencies |
| `overall_signal` | `strong_buy` / `buy` / `neutral` / `sell` / `strong_sell` |
| `fundamental_score` | –10 to +10 composite score |
| `key_strengths` | Top 3 fundamental strengths |
| `key_risks` | Top 3 fundamental risks |
| `reasoning` | 4–5 sentence narrative |

---

### 🧠 Synthesizer *(not an agent — the final workflow step)*
**Role:** Senior investment committee moderator.

Receives all 5 agent outputs and explicitly:
- Weighs Bull conviction vs Bear conviction
- Factors in risk level and news sentiment confidence
- Notes significant analyst disagreements
- Handles partial failures gracefully ("Note: risk analysis was unavailable for this run")

Produces the **FinalThesis**:

```json
{
  "recommendation": "BUY",
  "confidence": 74.0,
  "reasoning": "Financial strength and AI tailwinds outweigh near-term valuation risk...",
  "bull_summary": "Blackwell GPU ramp creates a multi-year earnings acceleration cycle",
  "bear_summary": "Hyperscaler custom silicon threatens long-term GPU monopoly",
  "key_risks": ["export controls", "valuation compression", "demand cyclicality"],
  "key_catalysts": ["Blackwell ramp", "sovereign AI", "software monetisation"]
}
```

---

## 📈 Technical Analysis Service

The `indicators_service.py` module computes **15+ indicators** from 6-month OHLCV data using `pandas-ta`, then the **TAAgent** interprets each one with a bullish / bearish / neutral signal and a plain-English interpretation.

### Trend Indicators
| Indicator | Config |
|---|---|
| EMA | 20-period |
| EMA | 50-period |
| SMA | 200-period |
| MACD | 12 / 26 / 9 (line, signal, histogram) |

### Momentum Indicators
| Indicator | Config |
|---|---|
| RSI | 14-period |
| Stochastic | %K and %D (14, 3, 3) |

### Volatility Indicators
| Indicator | Config |
|---|---|
| Bollinger Bands | 20-period, 2σ (upper, mid, lower, %B) |
| ATR | 14-period |

### Volume Indicators
| Indicator | Config |
|---|---|
| OBV | On-Balance Volume |
| VWAP | Volume-Weighted Average Price |

### Price Levels
| Level | Description |
|---|---|
| 20-day High/Low | Short-term support & resistance |
| 52-week High/Low | Long-term range extremes |

**TAOutput** includes a `signal_score` (–10 to +10), a `confluence` count (how many indicators agree with the overall signal), and a `reasoning` narrative.

---

## 🌍 Supported Markets

Any ticker supported by **Yahoo Finance** (`yfinance`) can be analysed. This includes:

| Market | Examples |
|---|---|
| 🇺🇸 US Equities (NYSE / NASDAQ) | `AAPL`, `NVDA`, `TSLA`, `MSFT`, `AMZN` |
| 🇬🇧 London Stock Exchange | `HSBA.L`, `BP.L`, `VOD.L` |
| 🇩🇪 Frankfurt / XETRA | `BMW.DE`, `SAP.DE` |
| 🇮🇳 NSE / BSE India | `RELIANCE.NS`, `TCS.NS`, `INFY.NS` |
| 🇭🇰 Hong Kong | `0700.HK` (Tencent), `9988.HK` (Alibaba) |
| 🇯🇵 Tokyo Stock Exchange | `7203.T` (Toyota), `6758.T` (Sony) |
| 📦 ETFs | `SPY`, `QQQ`, `VTI` |
| ₿ Crypto | `BTC-USD`, `ETH-USD` |

> **Note:** SEC filings and government contract data are only available for US-listed companies. News sentiment works globally via NewsAPI.

---

## 📦 Final Output — `AnalysisReport`

The API returns a single fully structured JSON object:

```json
{
  "ticker": "NVDA",
  "analysis_type": "long_term",
  "recommendation": "BUY",
  "confidence": 74.0,
  "reasoning": "...",
  "bull_summary": "...",
  "bear_summary": "...",
  "key_risks": ["...", "...", "..."],
  "key_catalysts": ["...", "...", "..."],
  "agent_outputs": {
    "financial": { ... },
    "news": { ... },
    "risk": { ... },
    "bull": { ... },
    "bear": { ... }
  },
  "agents_used": 5,
  "processing_time_ms": 4231,
  "timestamp": "2026-05-28T10:00:00Z"
}
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API key
- NewsAPI key

### Installation

```bash
git clone https://github.com/AlpenChristy/Investment-research-multiagent.git
cd Investment-research-multiagent

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
NEWSAPI_KEY=your_newsapi_key_here
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## 🔌 API Usage

### Endpoint

```
POST /analyze
```

### Request Body

```json
{
  "ticker": "NVDA",
  "analysis_type": "long_term"
}
```

`analysis_type` accepts `"long_term"` or `"short_term"`.

### cURL Example

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "analysis_type": "long_term"}'
```

### Python Example

```python
import httpx, asyncio

async def analyze(ticker: str):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "http://localhost:8000/analyze",
            json={"ticker": ticker, "analysis_type": "long_term"}
        )
        return r.json()

report = asyncio.run(analyze("NVDA"))
print(report["recommendation"], report["confidence"])
```

---

## 📁 Project Structure

```
investment-research-agent/
│
├── app/
│   ├── agents/
│   │   ├── financial_agent.py     # Quantitative financial analyst
│   │   ├── news_agent.py          # News sentiment analyst
│   │   ├── risk_agent.py          # Risk assessment analyst
│   │   ├── bull_agent.py          # Bullish case advocate
│   │   ├── bear_agent.py          # Bearish case advocate
│   │   ├── fundamentals_agent.py  # Deep-dive fundamental analyst
│   │   └── ta_agent.py            # Technical analysis interpreter
│   │
│   ├── graph/
│   │   └── workflow.py            # AgentOrchestrator + Synthesizer
│   │
│   ├── services/
│   │   ├── market_data.py         # yfinance: price, financials, SEC, gov contracts
│   │   ├── news_service.py        # NewsAPI integration
│   │   ├── indicators_service.py  # pandas-ta indicator computation
│   │   └── llm_service.py         # Shared OpenAI call_llm() helper
│   │
│   ├── prompts/
│   │   ├── financial.py           # Financial agent system prompt
│   │   ├── news.py                # News agent system prompt
│   │   ├── risk.py                # Risk agent system prompt
│   │   ├── bull.py                # Bull agent system prompt
│   │   ├── bear.py                # Bear agent system prompt
│   │   ├── fundamentals.py        # Fundamentals agent system prompt
│   │   ├── ta.py                  # Technical analysis system prompt
│   │   └── synthesizer.py        # Synthesizer / investment committee prompt
│   │
│   ├── schemas/
│   │   ├── models.py              # Core Pydantic schemas (all agent outputs)
│   │   └── fundamentals_models.py # Deep fundamental analysis schemas
│   │
│   ├── api/
│   │   └── routes.py              # FastAPI route: POST /analyze
│   │
│   └── main.py
│
├── tests/
├── requirements.txt
└── .env
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI + Uvicorn |
| **Agent Orchestration** | LangGraph + asyncio |
| **LLM** | OpenAI GPT-4.1-mini |
| **Data Validation** | Pydantic v2 |
| **Market Data** | yfinance |
| **Technical Analysis** | pandas-ta |
| **News** | NewsAPI |
| **SEC Filings** | EDGAR (SEC.gov public API) |
| **Gov Contracts** | USASpending.gov API |
| **HTTP Client** | httpx (async) |

---

## ⚙️ Design Decisions

**1. Data fetched once at the top — never inside agents.**  
The orchestrator owns data fetching. All 5 agents share the same `market_data` and `news_data` snapshots. This avoids 5x API calls, prevents rate limit issues, and guarantees consistent numbers if the price ticks between calls.

**2. `return_exceptions=True` on `asyncio.gather()`.**  
The most important line in the codebase. Without it, one agent timeout kills the entire request. With it, partial failures are recoverable — a report with 4/5 agents is still highly usable.

**3. Prompts are isolated in their own files.**  
All system prompts live in `app/prompts/` as plain string constants. Prompt engineering happens independently of orchestration logic — you can iterate on wording without touching `workflow.py`.

**4. Every agent output is a Pydantic model.**  
No raw LLM text leaks into the report. Each `model_validate_json()` call enforces the schema contract at runtime, making the API response fully predictable.

**5. The Synthesizer handles partial failures gracefully.**  
If an agent's output is `None`, the synthesizer prompt is explicitly told: "Note this gap in your reasoning. Do not invent data that was marked unavailable."

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙋 Author

**Alpen Christy**  
Built as a portfolio project demonstrating multi-agent AI system design, async Python, and financial data engineering.

> *"Developed a multi-agent financial research platform using LangGraph and FastAPI, enabling autonomous investment analysis, sentiment evaluation, risk assessment, and AI-driven bullish/bearish debate generation."*