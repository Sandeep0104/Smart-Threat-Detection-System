"""
AI Security Analyst - PDF Report Generator
Generates professional incident report PDFs using ReportLab.
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from ..models.schemas import AnalysisResult, SeverityLevel


# Custom colors
DARK_BG = colors.HexColor("#0a0e1a")
CYBER_CYAN = colors.HexColor("#00d4ff")
DARK_CARD = colors.HexColor("#1a1f36")
BORDER_COLOR = colors.HexColor("#2a3050")
CRITICAL_RED = colors.HexColor("#ef4444")
HIGH_ORANGE = colors.HexColor("#f59e0b")
MEDIUM_YELLOW = colors.HexColor("#eab308")
LOW_GREEN = colors.HexColor("#10b981")
TEXT_WHITE = colors.HexColor("#333333")
HEADER_BG = colors.HexColor("#1e3a5f")


def _get_styles():
    """Get custom paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=colors.HexColor("#1a1f36"),
        spaceAfter=6,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#6b7280"),
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1e3a5f"),
        spaceBefore=16,
        spaceAfter=8,
        borderWidth=0,
        borderPadding=0,
    ))

    styles.add(ParagraphStyle(
        name="SubSectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#374151"),
        spaceBefore=10,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="BodyText2",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        spaceAfter=6,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="SmallGray",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#9ca3af"),
        alignment=TA_CENTER,
    ))

    return styles


def _severity_color(severity: SeverityLevel) -> colors.HexColor:
    """Get color for severity level."""
    return {
        SeverityLevel.CRITICAL: CRITICAL_RED,
        SeverityLevel.HIGH: HIGH_ORANGE,
        SeverityLevel.MEDIUM: MEDIUM_YELLOW,
        SeverityLevel.LOW: LOW_GREEN,
        SeverityLevel.INFO: colors.HexColor("#6b7280"),
    }.get(severity, colors.HexColor("#6b7280"))


def generate_report_pdf(
    analysis: AnalysisResult,
    company_name: str = "Your Company",
    output_dir: str = "./reports",
) -> str:
    """Generate a professional PDF incident report and return the file path."""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"incident_report_{analysis.analysis_id[:8]}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = _get_styles()
    story = []

    # ── Header ──────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(Paragraph("🛡️ SECURITY INCIDENT REPORT", styles["ReportTitle"]))
    story.append(Paragraph(
        f"{company_name} | Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles["ReportSubtitle"]
    ))
    story.append(Paragraph(
        f"Report ID: {analysis.analysis_id[:12]} | File: {analysis.filename}",
        styles["ReportSubtitle"]
    ))

    # Divider
    story.append(HRFlowable(
        width="100%", thickness=2, color=CYBER_CYAN,
        spaceBefore=10, spaceAfter=20,
    ))

    # ── Executive Summary ──────────────────────────────────
    story.append(Paragraph("Executive Summary", styles["SectionTitle"]))

    risk_label = "LOW"
    risk_color = LOW_GREEN
    if analysis.risk_score >= 75:
        risk_label = "CRITICAL"
        risk_color = CRITICAL_RED
    elif analysis.risk_score >= 50:
        risk_label = "HIGH"
        risk_color = HIGH_ORANGE
    elif analysis.risk_score >= 25:
        risk_label = "MEDIUM"
        risk_color = MEDIUM_YELLOW

    # Stats summary table
    stats_data = [
        ["Total Log Entries", str(analysis.stats.total_lines),
         "Risk Score", f"{analysis.risk_score}/100 ({risk_label})"],
        ["Unique IP Addresses", str(analysis.stats.unique_ips),
         "Threats Detected", str(analysis.stats.threats_detected or len(analysis.threats))],
        ["Failed Logins", str(analysis.stats.failed_logins),
         "Successful Logins", str(analysis.stats.successful_logins)],
        ["Log Format", analysis.stats.log_format,
         "Time Range", f"{analysis.stats.time_range_start or 'N/A'} - {analysis.stats.time_range_end or 'N/A'}"],
    ]

    stats_table = Table(stats_data, colWidths=[1.6 * inch, 1.2 * inch, 1.6 * inch, 2.4 * inch])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_WHITE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 12))

    # AI Summary
    if analysis.ai_summary:
        story.append(Paragraph("AI Analysis", styles["SubSectionTitle"]))
        # Clean up markdown from AI summary
        clean_summary = analysis.ai_summary.replace("##", "").replace("**", "").replace("*", "")
        for para in clean_summary.split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, styles["BodyText2"]))
                story.append(Spacer(1, 4))

    # ── Threat Details ──────────────────────────────────────
    if analysis.threats:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Detected Threats", styles["SectionTitle"]))

        # Threats table
        threat_header = ["#", "Type", "Severity", "Source IP", "Count", "Description"]
        threat_data = [threat_header]

        for i, threat in enumerate(analysis.threats, 1):
            desc = threat.description[:80] + "..." if len(threat.description) > 80 else threat.description
            threat_data.append([
                str(i),
                threat.threat_type.replace("_", " ").title(),
                threat.severity.value.upper(),
                threat.source_ip or "N/A",
                str(threat.count),
                desc,
            ])

        col_widths = [0.3 * inch, 1.2 * inch, 0.8 * inch, 1.1 * inch, 0.5 * inch, 3 * inch]
        threat_table = Table(threat_data, colWidths=col_widths, repeatRows=1)

        # Style the table
        table_style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]

        # Color-code severity cells
        for i, threat in enumerate(analysis.threats, 1):
            sev_color = _severity_color(threat.severity)
            table_style_cmds.append(("TEXTCOLOR", (2, i), (2, i), sev_color))
            table_style_cmds.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))

        threat_table.setStyle(TableStyle(table_style_cmds))
        story.append(threat_table)

        # Detailed findings
        story.append(Spacer(1, 16))
        story.append(Paragraph("Detailed Findings", styles["SectionTitle"]))

        for i, threat in enumerate(analysis.threats, 1):
            sev = threat.severity.value.upper()
            story.append(Paragraph(
                f"Finding #{i}: {threat.threat_type.replace('_', ' ').title()} [{sev}]",
                styles["SubSectionTitle"]
            ))
            story.append(Paragraph(threat.description, styles["BodyText2"]))

            if threat.recommendation:
                story.append(Paragraph("<b>Recommended Actions:</b>", styles["BodyText2"]))
                for rec_line in threat.recommendation.split("\n"):
                    rec_line = rec_line.strip()
                    if rec_line:
                        story.append(Paragraph(f"  {rec_line}", styles["BodyText2"]))

            if threat.evidence:
                story.append(Paragraph("<b>Evidence (sample log entries):</b>", styles["BodyText2"]))
                for ev in threat.evidence[:3]:
                    # Truncate long evidence lines
                    ev_short = ev[:120] + "..." if len(ev) > 120 else ev
                    story.append(Paragraph(
                        f"<font face='Courier' size='7' color='#6b7280'>{ev_short}</font>",
                        styles["BodyText2"]
                    ))

            story.append(Spacer(1, 8))
            story.append(HRFlowable(
                width="80%", thickness=0.5, color=colors.HexColor("#e2e8f0"),
                spaceBefore=4, spaceAfter=8
            ))

    # ── Recommendations ────────────────────────────────────
    if analysis.recommendations:
        story.append(Paragraph("Recommendations", styles["SectionTitle"]))
        for rec in analysis.recommendations:
            clean_rec = rec.replace("**", "").strip()
            if clean_rec:
                story.append(Paragraph(f"• {clean_rec}", styles["BodyText2"]))

    # ── Footer ─────────────────────────────────────────────
    story.append(Spacer(1, 30))
    story.append(HRFlowable(
        width="100%", thickness=1, color=colors.HexColor("#e2e8f0"),
        spaceBefore=10, spaceAfter=10,
    ))
    story.append(Paragraph(
        "Generated by AI Security Analyst | Powered by Ollama + LangChain",
        styles["SmallGray"]
    ))
    story.append(Paragraph(
        "This report is for informational purposes. Consult a cybersecurity professional for critical issues.",
        styles["SmallGray"]
    ))

    # Build PDF
    doc.build(story)
    return filepath
