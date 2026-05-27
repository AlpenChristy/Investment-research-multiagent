




class AgentOrchestrator:
    def __init__(self):
        self.financial_agent = FinancialAgent()
        self.news_agent      = NewsAgent()
        self.risk_agent      = RiskAgent()
        self.bull_agent      = BullAgent()
        self.bear_agent      = BearAgent()
        self.synthesizer     = Synthesizer()

    async def run(self, request: AnalysisRequest) -> AnalysisReport:
        start = time.time()

        # 1. Fetch data once, share across all agents
        market_data = await fetch_market_data(request.ticker)
        news_data   = await fetch_news(request.ticker)

        # 2. Run all agents in parallel
        results = await asyncio.gather(
            self.financial_agent.run(request.ticker, market_data),
            self.news_agent.run(request.ticker, news_data),
            self.risk_agent.run(request.ticker, market_data),
            self.bull_agent.run(request.ticker, market_data, news_data),
            self.bear_agent.run(request.ticker, market_data, news_data),
            return_exceptions=True   # critical — don't let one agent kill the whole run
        )

        # 3. Separate successes from failures
        financial, news, risk, bull, bear = results
        agent_outputs = AgentOutputs(
            financial = financial if not isinstance(financial, Exception) else None,
            news      = news      if not isinstance(news,      Exception) else None,
            risk      = risk      if not isinstance(risk,      Exception) else None,
            bull      = bull      if not isinstance(bull,      Exception) else None,
            bear      = bear      if not isinstance(bear,      Exception) else None,
        )

        if agent_outputs.all_failed():
            raise HTTPException(500, "All agents failed")

        # 4. Synthesize
        thesis = await self.synthesizer.run(agent_outputs)

        return AnalysisReport(
            ticker          = request.ticker,
            recommendation  = thesis.recommendation,
            confidence      = thesis.confidence,
            reasoning       = thesis.reasoning,
            agent_outputs   = agent_outputs,
            processing_time = int((time.time() - start) * 1000),
        )