"""
AI Security Analyst - Pydantic Models / Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class LogFormat(str, Enum):
    AUTH_LOG = "auth.log"
    SYSLOG = "syslog"
    APACHE_ACCESS = "apache_access"
    UNKNOWN = "unknown"


class LogEntry(BaseModel):
    """A single parsed log entry."""
    timestamp: Optional[str] = None
    hostname: Optional[str] = None
    service: Optional[str] = None
    pid: Optional[str] = None
    message: str = ""
    source_ip: Optional[str] = None
    username: Optional[str] = None
    action: Optional[str] = None  # success, failure, blocked, etc.
    severity: SeverityLevel = SeverityLevel.INFO
    raw_line: str = ""
    line_number: int = 0


class ThreatDetection(BaseModel):
    """A detected security threat."""
    threat_type: str  # brute_force, port_scan, sql_injection, directory_traversal, etc.
    severity: SeverityLevel
    source_ip: Optional[str] = None
    target: Optional[str] = None  # target user, resource, etc.
    count: int = 1
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    description: str = ""
    recommendation: str = ""
    evidence: list[str] = Field(default_factory=list)


class AnalysisStats(BaseModel):
    """Statistics from log analysis."""
    total_lines: int = 0
    parsed_lines: int = 0
    unique_ips: int = 0
    failed_logins: int = 0
    successful_logins: int = 0
    threats_detected: int = 0
    log_format: str = "unknown"
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    analysis_id: str
    filename: str
    timestamp: str
    stats: AnalysisStats
    threats: list[ThreatDetection] = Field(default_factory=list)
    ai_summary: str = ""
    risk_score: int = 0  # 0-100
    recommendations: list[str] = Field(default_factory=list)
    log_entries: list[LogEntry] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """A chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request from the frontend."""
    message: str
    analysis_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response to the frontend."""
    response: str
    sources: list[str] = Field(default_factory=list)


class ReportRequest(BaseModel):
    """Request to generate an incident report."""
    analysis_id: str
    company_name: str = "Your Company"
    include_recommendations: bool = True


class ReportResponse(BaseModel):
    """Response with report info."""
    report_id: str
    filename: str
    download_url: str
