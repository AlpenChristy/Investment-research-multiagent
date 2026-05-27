import asyncio
from app.graph.workflow import AgentOrchestrator
from app.schemas.models import AnalysisReport
from dotenv import load_dotenv

load_dotenv()

async def main():
    orchestrator = AgentOrchestrator()

    print("=" * 50)
    print("Running full NVDA analysis...")
    print("=" * 50)

    report = await orchestrator.run(
        ticker="NVDA",
        analysis_type="long_term",
    )

    # assert it's the right type
    assert isinstance(report, AnalysisReport), "Report is not an AnalysisReport"

    # assert critical fields are populated
    assert report.recommendation in ["BUY", "HOLD", "SELL"]
    assert 0 <= report.confidence <= 100
    assert report.agents_used > 0
    assert report.processing_time_ms > 0

    print("\n" + "=" * 50)
    print("FINAL REPORT")
    print("=" * 50)
    print(report.model_dump_json(indent=2))

    print("\n" + "=" * 50)
    print(f"  Recommendation : {report.recommendation}")
    print(f"  Confidence     : {report.confidence}%")
    print(f"  Agents used    : {report.agents_used}/5")
    print(f"  Processing time: {report.processing_time_ms}ms")
    print("=" * 50)

asyncio.run(main())