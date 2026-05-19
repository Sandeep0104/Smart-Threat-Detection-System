"""
AI Security Analyst - AI Analyzer Service
Uses Ollama (via LangChain) to summarize threats and provide recommendations in plain English.
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from ..models.schemas import ThreatDetection, AnalysisStats, SeverityLevel
from ..config import settings


def _get_llm() -> ChatOllama:
    """Get an Ollama LLM instance."""
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0.3,
    )


SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a cybersecurity analyst explaining security findings to a small business owner 
who has NO technical background. Use simple, everyday language. Avoid jargon.

Your job is to:
1. Explain what happened in plain English (like explaining to a friend)
2. How serious this is for their business
3. What they should do RIGHT NOW

Be concise but thorough. Use bullet points. Be reassuring but honest about risks."""),
    ("human", """Here are the security findings from analyzing server logs:

**Log Statistics:**
- Total log entries analyzed: {total_lines}
- Unique IP addresses: {unique_ips}
- Failed login attempts: {failed_logins}
- Successful logins: {successful_logins}
- Risk Score: {risk_score}/100

**Detected Threats ({threat_count} total):**
{threat_details}

Please provide:
1. A clear, non-technical summary of what's happening (2-3 paragraphs)
2. The top 3 most important things they should do right now
3. An overall assessment of their security posture""")
])


RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful cybersecurity advisor for small businesses. 
Provide actionable, step-by-step recommendations that a non-technical person can follow.
Include exact commands when applicable (for Linux servers).
Prioritize recommendations by urgency."""),
    ("human", """Based on these detected threats, provide specific recommendations:

{threat_details}

Risk Score: {risk_score}/100

Provide 5-7 specific, actionable recommendations ordered by priority.
For each recommendation, include:
- What to do (in simple terms)
- Why it matters
- The exact command or steps to follow""")
])


def _format_threats_for_prompt(threats: list[ThreatDetection]) -> str:
    """Format threats into a readable string for the LLM prompt."""
    if not threats:
        return "No threats detected."

    lines = []
    for i, threat in enumerate(threats, 1):
        lines.append(
            f"{i}. **{threat.threat_type.replace('_', ' ').title()}** "
            f"[{threat.severity.value.upper()}]\n"
            f"   - Source: {threat.source_ip or 'N/A'}\n"
            f"   - Count: {threat.count}\n"
            f"   - {threat.description}\n"
        )
    return "\n".join(lines)


async def generate_ai_summary(
    threats: list[ThreatDetection],
    stats: AnalysisStats,
    risk_score: int,
) -> str:
    """Generate an AI summary of the security analysis using Ollama."""
    try:
        llm = _get_llm()
        threat_details = _format_threats_for_prompt(threats)

        chain = SUMMARY_PROMPT | llm
        response = await chain.ainvoke({
            "total_lines": stats.total_lines,
            "unique_ips": stats.unique_ips,
            "failed_logins": stats.failed_logins,
            "successful_logins": stats.successful_logins,
            "risk_score": risk_score,
            "threat_count": len(threats),
            "threat_details": threat_details,
        })

        return response.content
    except Exception as e:
        # Fallback: generate a basic summary without AI
        return _generate_fallback_summary(threats, stats, risk_score)


async def generate_recommendations(
    threats: list[ThreatDetection],
    risk_score: int,
) -> list[str]:
    """Generate AI-powered recommendations."""
    try:
        llm = _get_llm()
        threat_details = _format_threats_for_prompt(threats)

        chain = RECOMMENDATION_PROMPT | llm
        response = await chain.ainvoke({
            "threat_details": threat_details,
            "risk_score": risk_score,
        })

        # Split response into individual recommendations
        content = response.content
        recs = []
        for line in content.split("\n"):
            line = line.strip()
            if line and len(line) > 10:
                recs.append(line)

        return recs if recs else _generate_fallback_recommendations(threats)
    except Exception as e:
        return _generate_fallback_recommendations(threats)


def _generate_fallback_summary(
    threats: list[ThreatDetection],
    stats: AnalysisStats,
    risk_score: int,
) -> str:
    """Generate a basic summary when Ollama is not available."""
    critical = sum(1 for t in threats if t.severity == SeverityLevel.CRITICAL)
    high = sum(1 for t in threats if t.severity == SeverityLevel.HIGH)

    summary = f"## Security Analysis Summary\n\n"
    summary += f"Analyzed **{stats.total_lines}** log entries from **{stats.unique_ips}** unique IP addresses.\n\n"

    if not threats:
        summary += "**Good news!** No significant security threats were detected in the analyzed logs. "
        summary += "Your system appears to be operating normally.\n"
    else:
        summary += f"**⚠️ {len(threats)} security threats detected** (Risk Score: {risk_score}/100)\n\n"

        if critical > 0:
            summary += f"- 🔴 **{critical} CRITICAL** threats require immediate attention\n"
        if high > 0:
            summary += f"- 🟠 **{high} HIGH** severity threats found\n"
        summary += f"- {stats.failed_logins} failed login attempts detected\n\n"

        summary += "### Key Findings:\n"
        for threat in threats[:5]:
            summary += f"- **{threat.threat_type.replace('_', ' ').title()}** from {threat.source_ip or 'unknown'}: {threat.description[:150]}\n"

    summary += (
        "\n\n> **Note:** AI-powered analysis requires Ollama to be running. "
        "Start Ollama with `ollama serve` and pull a model with `ollama pull llama3.2` "
        "for enhanced AI analysis."
    )
    return summary


def _generate_fallback_recommendations(threats: list[ThreatDetection]) -> list[str]:
    """Generate basic recommendations without AI."""
    recs = []
    threat_types = set(t.threat_type for t in threats)

    if "brute_force" in threat_types:
        recs.append("🔴 URGENT: Install and configure fail2ban to automatically block brute-force attackers")
        recs.append("Enable SSH key-based authentication and disable password login")

    if "sql_injection" in threat_types:
        recs.append("🔴 URGENT: Review and patch your web application for SQL injection vulnerabilities")
        recs.append("Deploy a Web Application Firewall (WAF) like ModSecurity")

    if "directory_traversal" in threat_types:
        recs.append("Update your web server configuration to prevent directory traversal")

    ips = set(t.source_ip for t in threats if t.source_ip and t.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH))
    if ips:
        ip_list = ", ".join(list(ips)[:5])
        recs.append(f"Block malicious IPs immediately: {ip_list}")

    recs.append("Ensure all software and services are updated to the latest versions")
    recs.append("Set up regular log monitoring and automated security alerts")
    recs.append("Create regular backups and test your disaster recovery plan")

    return recs
