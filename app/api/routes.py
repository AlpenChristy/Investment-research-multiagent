from fastapi import APIRouter, HTTPException
from app.schemas.models import AnalysisRequest, AnalysisReport
from app.graph.workflow import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()


@router.post("/analyze", response_model=AnalysisReport)
async def analyze(request: AnalysisRequest) -> AnalysisReport:
    try:
        report = await orchestrator.run(
            ticker=request.ticker,
            analysis_type=request.analysis_type,
        )
        return report
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")