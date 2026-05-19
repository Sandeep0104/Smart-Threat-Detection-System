"""
AI Security Analyst - Log Router
Endpoints for uploading, parsing, and analyzing server logs.
"""
import uuid
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.schemas import AnalysisResult, AnalysisStats
from ..services.log_parser import parse_log_content
from ..services.threat_detector import detect_threats, calculate_stats, calculate_risk_score
from ..services.ai_analyzer import generate_ai_summary, generate_recommendations
from ..services import vector_store as vs
from ..config import settings

router = APIRouter(prefix="/api/logs", tags=["logs"])

# In-memory storage for analysis results
_analyses: dict[str, AnalysisResult] = {}


@router.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """Upload a log file, parse it, detect threats, and run AI analysis."""
    # Validate file
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    # Read content
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        raise HTTPException(400, "Could not read file. Please upload a text-based log file.")

    if not text.strip():
        raise HTTPException(400, "File is empty")

    # Check file size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(400, f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB")

    # Save file
    analysis_id = str(uuid.uuid4())
    upload_path = os.path.join(settings.UPLOAD_DIR, f"{analysis_id}_{file.filename}")
    with open(upload_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Parse logs
    entries, log_format = parse_log_content(text)
    if not entries:
        raise HTTPException(400, "Could not parse any log entries from the file.")

    # Detect threats
    threats = detect_threats(entries)

    # Calculate stats
    stats = calculate_stats(entries, log_format.value)
    stats.threats_detected = len(threats)

    # Calculate risk score
    risk_score = calculate_risk_score(threats, stats)

    # Generate AI summary (async, may fail if Ollama is not running)
    ai_summary = await generate_ai_summary(threats, stats, risk_score)

    # Generate recommendations
    recommendations = await generate_recommendations(threats, risk_score)

    # Ingest into vector store for chat
    await vs.ingest_logs(analysis_id, entries)

    # Build result
    result = AnalysisResult(
        analysis_id=analysis_id,
        filename=file.filename,
        timestamp=datetime.now().isoformat(),
        stats=stats,
        threats=threats,
        ai_summary=ai_summary,
        risk_score=risk_score,
        recommendations=recommendations,
        log_entries=entries[:100],  # Limit entries sent to frontend
    )

    # Store
    _analyses[analysis_id] = result

    return result


@router.post("/upload-sample/{sample_name}")
async def analyze_sample_log(sample_name: str):
    """Analyze a bundled sample log file."""
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sample_logs")
    sample_map = {
        "auth": "auth.log",
        "syslog": "syslog.log",
        "access": "access.log",
        "nginx": "nginx.log",
        "ssh_heavy": "ssh_heavy.log",
        "mixed": "mixed.log",
    }

    if sample_name not in sample_map:
        raise HTTPException(400, f"Unknown sample. Available: {list(sample_map.keys())}")

    filepath = os.path.join(sample_dir, sample_map[sample_name])
    if not os.path.exists(filepath):
        raise HTTPException(404, f"Sample file not found: {sample_map[sample_name]}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Same analysis pipeline
    analysis_id = str(uuid.uuid4())
    entries, log_format = parse_log_content(text)
    threats = detect_threats(entries)
    stats = calculate_stats(entries, log_format.value)
    stats.threats_detected = len(threats)
    risk_score = calculate_risk_score(threats, stats)
    ai_summary = await generate_ai_summary(threats, stats, risk_score)
    recommendations = await generate_recommendations(threats, risk_score)
    await vs.ingest_logs(analysis_id, entries)

    result = AnalysisResult(
        analysis_id=analysis_id,
        filename=sample_map[sample_name],
        timestamp=datetime.now().isoformat(),
        stats=stats,
        threats=threats,
        ai_summary=ai_summary,
        risk_score=risk_score,
        recommendations=recommendations,
        log_entries=entries[:100],
    )

    _analyses[analysis_id] = result
    return result


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get a previously computed analysis result."""
    if analysis_id not in _analyses:
        raise HTTPException(404, "Analysis not found")
    return _analyses[analysis_id]


@router.get("/threats/{analysis_id}")
async def get_threats(analysis_id: str):
    """Get detected threats for an analysis."""
    if analysis_id not in _analyses:
        raise HTTPException(404, "Analysis not found")
    return _analyses[analysis_id].threats


@router.get("/list")
async def list_analyses():
    """List all available analyses."""
    return [
        {
            "analysis_id": a.analysis_id,
            "filename": a.filename,
            "timestamp": a.timestamp,
            "risk_score": a.risk_score,
            "threat_count": len(a.threats),
        }
        for a in _analyses.values()
    ]
