from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.analysis.copy_analyzer import CopyAnalyzerService, CopyAnalysisResult

router = APIRouter()

class CopyAuditRequest(BaseModel):
    text: str
    objective: str

@router.post("/audit-copy", response_model=CopyAnalysisResult)
async def audit_copy(request: CopyAuditRequest):
    analyzer = CopyAnalyzerService()
    result = await analyzer.analyze_copy(request.text, request.objective)
    return result
