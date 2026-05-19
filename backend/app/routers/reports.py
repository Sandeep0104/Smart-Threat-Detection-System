"""
AI Security Analyst - Reports Router
Endpoints for generating and downloading PDF incident reports.
"""
import os
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..models.schemas import ReportRequest, ReportResponse
from ..services.pdf_generator import generate_report_pdf
from ..config import settings

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Store generated reports
_reports: dict[str, str] = {}  # report_id -> filepath


@router.post("/generate", response_model=ReportResponse)
async def generate_report(req: ReportRequest):
    """Generate a PDF incident report for an analysis."""
    # Import here to avoid circular imports
    from ..routers.logs import _analyses

    if req.analysis_id not in _analyses:
        raise HTTPException(404, "Analysis not found. Upload and analyze logs first.")

    analysis = _analyses[req.analysis_id]

    try:
        filepath = generate_report_pdf(
            analysis=analysis,
            company_name=req.company_name,
            output_dir=settings.REPORTS_DIR,
        )
    except Exception as e:
        raise HTTPException(500, f"Failed to generate report: {str(e)}")

    report_id = str(uuid.uuid4())
    _reports[report_id] = filepath

    filename = os.path.basename(filepath)
    return ReportResponse(
        report_id=report_id,
        filename=filename,
        download_url=f"/api/reports/download/{report_id}",
    )


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Download a generated PDF report."""
    if report_id not in _reports:
        raise HTTPException(404, "Report not found")

    filepath = _reports[report_id]
    if not os.path.exists(filepath):
        raise HTTPException(404, "Report file not found on disk")

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath),
    )
