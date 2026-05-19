"""
AI Security Analyst - Threat Detector Service
Detects brute-force attacks, port scans, SQL injection, and other threats from parsed log entries.
"""
from collections import defaultdict
from ..models.schemas import LogEntry, ThreatDetection, SeverityLevel, AnalysisStats
from ..config import settings


def detect_threats(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Run all threat detection algorithms on parsed log entries."""
    threats: list[ThreatDetection] = []

    threats.extend(_detect_brute_force(entries))
    threats.extend(_detect_invalid_users(entries))
    threats.extend(_detect_port_scanning(entries))
    threats.extend(_detect_web_attacks(entries))
    threats.extend(_detect_unusual_access(entries))
    threats.extend(_detect_privilege_escalation(entries))
    threats.extend(_detect_firewall_blocks(entries))

    # Sort by severity
    severity_order = {
        SeverityLevel.CRITICAL: 0,
        SeverityLevel.HIGH: 1,
        SeverityLevel.MEDIUM: 2,
        SeverityLevel.LOW: 3,
        SeverityLevel.INFO: 4,
    }
    threats.sort(key=lambda t: severity_order.get(t.severity, 5))

    return threats


def _detect_brute_force(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Detect brute-force login attempts based on failed login count per IP."""
    threats = []
    failed_by_ip: dict[str, list[LogEntry]] = defaultdict(list)

    for entry in entries:
        if entry.action == "failed_login" and entry.source_ip:
            failed_by_ip[entry.source_ip].append(entry)

    for ip, fails in failed_by_ip.items():
        if len(fails) >= settings.BRUTE_FORCE_THRESHOLD:
            usernames = list(set(e.username for e in fails if e.username))
            evidence = [e.raw_line for e in fails[:5]]

            threats.append(ThreatDetection(
                threat_type="brute_force",
                severity=SeverityLevel.CRITICAL if len(fails) >= 20 else SeverityLevel.HIGH,
                source_ip=ip,
                target=", ".join(usernames[:5]),
                count=len(fails),
                first_seen=fails[0].timestamp,
                last_seen=fails[-1].timestamp,
                description=(
                    f"Brute-force attack detected from {ip}. "
                    f"{len(fails)} failed login attempts targeting user(s): {', '.join(usernames[:5])}. "
                    f"This is a clear attempt to guess passwords through automated trial."
                ),
                recommendation=(
                    f"1. Block this IP immediately: sudo ufw deny from {ip}\n"
                    f"2. Check if any login was successful from this IP\n"
                    f"3. Change passwords for targeted accounts: {', '.join(usernames[:3])}\n"
                    f"4. Consider implementing fail2ban for automatic blocking\n"
                    f"5. Enable two-factor authentication (2FA) on SSH"
                ),
                evidence=evidence,
            ))

    return threats


def _detect_invalid_users(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Detect attempts to login with non-existent usernames."""
    threats = []
    invalid_by_ip: dict[str, list[LogEntry]] = defaultdict(list)

    for entry in entries:
        if entry.action == "invalid_user" and entry.source_ip:
            invalid_by_ip[entry.source_ip].append(entry)

    for ip, attempts in invalid_by_ip.items():
        if len(attempts) >= 3:
            usernames = list(set(e.username for e in attempts if e.username))
            evidence = [e.raw_line for e in attempts[:5]]

            threats.append(ThreatDetection(
                threat_type="user_enumeration",
                severity=SeverityLevel.HIGH,
                source_ip=ip,
                target=", ".join(usernames[:5]),
                count=len(attempts),
                first_seen=attempts[0].timestamp,
                last_seen=attempts[-1].timestamp,
                description=(
                    f"User enumeration attack from {ip}. "
                    f"Attempted to login with {len(attempts)} non-existent usernames: {', '.join(usernames[:5])}. "
                    f"The attacker is probing for valid accounts on your system."
                ),
                recommendation=(
                    f"1. Block this IP: sudo ufw deny from {ip}\n"
                    f"2. Disable password authentication, use SSH keys only\n"
                    f"3. Hide username existence in SSH responses\n"
                    f"4. Monitor for follow-up brute-force attacks"
                ),
                evidence=evidence,
            ))

    return threats


def _detect_port_scanning(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Detect port scanning from firewall block logs."""
    threats = []
    blocks_by_ip: dict[str, list[LogEntry]] = defaultdict(list)

    for entry in entries:
        if entry.action == "firewall_block" and entry.source_ip:
            blocks_by_ip[entry.source_ip].append(entry)

    for ip, blocks in blocks_by_ip.items():
        if len(blocks) >= settings.PORT_SCAN_THRESHOLD:
            evidence = [e.raw_line for e in blocks[:5]]

            threats.append(ThreatDetection(
                threat_type="port_scan",
                severity=SeverityLevel.MEDIUM,
                source_ip=ip,
                count=len(blocks),
                first_seen=blocks[0].timestamp,
                last_seen=blocks[-1].timestamp,
                description=(
                    f"Possible port scan from {ip}. "
                    f"{len(blocks)} connection attempts were blocked by the firewall. "
                    f"The attacker is probing for open services on your system."
                ),
                recommendation=(
                    f"1. Ensure firewall is properly configured\n"
                    f"2. Block this IP: sudo ufw deny from {ip}\n"
                    f"3. Consider using a network IDS like Snort or Suricata\n"
                    f"4. Review which ports are actually needed and close all others"
                ),
                evidence=evidence,
            ))

    return threats


def _detect_web_attacks(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Detect SQL injection and directory traversal attempts in web logs."""
    threats = []

    sqli_by_ip: dict[str, list[LogEntry]] = defaultdict(list)
    traversal_by_ip: dict[str, list[LogEntry]] = defaultdict(list)

    for entry in entries:
        if entry.action == "sql_injection_attempt" and entry.source_ip:
            sqli_by_ip[entry.source_ip].append(entry)
        elif entry.action == "directory_traversal" and entry.source_ip:
            traversal_by_ip[entry.source_ip].append(entry)

    for ip, attempts in sqli_by_ip.items():
        evidence = [e.raw_line for e in attempts[:5]]
        threats.append(ThreatDetection(
            threat_type="sql_injection",
            severity=SeverityLevel.CRITICAL,
            source_ip=ip,
            count=len(attempts),
            first_seen=attempts[0].timestamp,
            last_seen=attempts[-1].timestamp,
            description=(
                f"SQL injection attack detected from {ip}. "
                f"{len(attempts)} malicious requests attempted to inject SQL commands. "
                f"This could lead to data theft, modification, or complete database compromise."
            ),
            recommendation=(
                f"1. Block this IP immediately: sudo ufw deny from {ip}\n"
                f"2. Review your web application for SQL injection vulnerabilities\n"
                f"3. Use parameterized queries in all database interactions\n"
                f"4. Deploy a Web Application Firewall (WAF)\n"
                f"5. Check database logs for any successful injection"
            ),
            evidence=evidence,
        ))

    for ip, attempts in traversal_by_ip.items():
        evidence = [e.raw_line for e in attempts[:5]]
        threats.append(ThreatDetection(
            threat_type="directory_traversal",
            severity=SeverityLevel.HIGH,
            source_ip=ip,
            count=len(attempts),
            first_seen=attempts[0].timestamp,
            last_seen=attempts[-1].timestamp,
            description=(
                f"Directory traversal attack from {ip}. "
                f"{len(attempts)} requests attempted to access files outside the web root. "
                f"The attacker is trying to read sensitive system files."
            ),
            recommendation=(
                f"1. Block this IP: sudo ufw deny from {ip}\n"
                f"2. Validate and sanitize all file path inputs\n"
                f"3. Use chroot or containers to limit file access\n"
                f"4. Review web server configuration for path restrictions"
            ),
            evidence=evidence,
        ))

    return threats


def _detect_unusual_access(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Detect login attempts at unusual hours."""
    threats = []
    unusual_by_ip: dict[str, list[LogEntry]] = defaultdict(list)

    for entry in entries:
        if entry.action in ("successful_login", "failed_login") and entry.timestamp:
            try:
                # Parse hour from timestamp like "May 10 03:15:23"
                parts = entry.timestamp.split(":")
                if len(parts) >= 1:
                    hour = int(parts[0].split()[-1])
                    if settings.UNUSUAL_HOUR_START <= hour <= settings.UNUSUAL_HOUR_END:
                        if entry.source_ip:
                            unusual_by_ip[entry.source_ip].append(entry)
            except (ValueError, IndexError):
                continue

    for ip, attempts in unusual_by_ip.items():
        if len(attempts) >= 2:
            evidence = [e.raw_line for e in attempts[:5]]
            threats.append(ThreatDetection(
                threat_type="unusual_hour_access",
                severity=SeverityLevel.MEDIUM,
                source_ip=ip,
                count=len(attempts),
                first_seen=attempts[0].timestamp,
                last_seen=attempts[-1].timestamp,
                description=(
                    f"Suspicious login activity from {ip} during unusual hours "
                    f"({settings.UNUSUAL_HOUR_START}:00 - {settings.UNUSUAL_HOUR_END}:00). "
                    f"{len(attempts)} login attempts detected. This may indicate automated attacks "
                    f"or unauthorized access from a different timezone."
                ),
                recommendation=(
                    f"1. Verify if this access is legitimate with your team\n"
                    f"2. Consider restricting SSH access to business hours\n"
                    f"3. Enable geographic access restrictions if applicable\n"
                    f"4. Set up alerts for after-hours access attempts"
                ),
                evidence=evidence,
            ))

    return threats


def _detect_privilege_escalation(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Detect suspicious sudo/privilege escalation activities."""
    threats = []
    sudo_entries = [e for e in entries if e.action == "sudo_command"]

    # Check for suspicious sudo patterns
    suspicious_cmds = []
    for entry in sudo_entries:
        msg_lower = entry.message.lower()
        if any(kw in msg_lower for kw in [
            "passwd", "useradd", "usermod", "visudo",
            "chmod 777", "chmod +s", "/etc/shadow",
            "rm -rf", "dd if=", "mkfs"
        ]):
            suspicious_cmds.append(entry)

    if suspicious_cmds:
        evidence = [e.raw_line for e in suspicious_cmds[:5]]
        usernames = list(set(e.username for e in suspicious_cmds if e.username))
        threats.append(ThreatDetection(
            threat_type="privilege_escalation",
            severity=SeverityLevel.HIGH,
            target=", ".join(usernames),
            count=len(suspicious_cmds),
            first_seen=suspicious_cmds[0].timestamp,
            last_seen=suspicious_cmds[-1].timestamp,
            description=(
                f"Suspicious privilege escalation detected. "
                f"{len(suspicious_cmds)} sensitive commands were executed via sudo by: "
                f"{', '.join(usernames)}. These commands modify system security settings."
            ),
            recommendation=(
                "1. Review all sudo commands for legitimacy\n"
                "2. Audit the sudoers file for excessive permissions\n"
                "3. Implement sudo logging and alerts\n"
                "4. Use the principle of least privilege for all users\n"
                "5. Consider using a privileged access management (PAM) solution"
            ),
            evidence=evidence,
        ))

    return threats


def _detect_firewall_blocks(entries: list[LogEntry]) -> list[ThreatDetection]:
    """Summarize significant firewall block activity."""
    threats = []
    blocks = [e for e in entries if e.action == "firewall_block"]

    if len(blocks) >= 5:
        unique_ips = set(e.source_ip for e in blocks if e.source_ip)
        evidence = [e.raw_line for e in blocks[:5]]

        threats.append(ThreatDetection(
            threat_type="high_firewall_activity",
            severity=SeverityLevel.MEDIUM if len(blocks) < 50 else SeverityLevel.HIGH,
            count=len(blocks),
            first_seen=blocks[0].timestamp,
            last_seen=blocks[-1].timestamp,
            description=(
                f"High firewall block activity detected. "
                f"{len(blocks)} connections blocked from {len(unique_ips)} unique IP addresses. "
                f"This indicates active probing or attack attempts against your system."
            ),
            recommendation=(
                "1. Review firewall rules to ensure they are up to date\n"
                "2. Consider implementing geographic IP blocking\n"
                "3. Set up automatic IP blacklisting for repeat offenders\n"
                "4. Monitor trends - increasing blocks may indicate a targeted attack"
            ),
            evidence=evidence,
        ))

    return threats


def calculate_stats(entries: list[LogEntry], log_format: str) -> AnalysisStats:
    """Calculate analysis statistics from parsed entries."""
    unique_ips = set()
    failed_logins = 0
    successful_logins = 0
    timestamps = []

    for entry in entries:
        if entry.source_ip:
            unique_ips.add(entry.source_ip)
        if entry.action == "failed_login":
            failed_logins += 1
        elif entry.action == "successful_login":
            successful_logins += 1
        if entry.timestamp:
            timestamps.append(entry.timestamp)

    return AnalysisStats(
        total_lines=len(entries),
        parsed_lines=sum(1 for e in entries if e.action and e.action != "other"),
        unique_ips=len(unique_ips),
        failed_logins=failed_logins,
        successful_logins=successful_logins,
        log_format=log_format,
        time_range_start=timestamps[0] if timestamps else None,
        time_range_end=timestamps[-1] if timestamps else None,
    )


def calculate_risk_score(threats: list[ThreatDetection], stats: AnalysisStats) -> int:
    """Calculate an overall risk score (0-100) based on detected threats."""
    if not threats:
        return 0

    score = 0
    severity_weights = {
        SeverityLevel.CRITICAL: 30,
        SeverityLevel.HIGH: 20,
        SeverityLevel.MEDIUM: 10,
        SeverityLevel.LOW: 5,
        SeverityLevel.INFO: 1,
    }

    for threat in threats:
        weight = severity_weights.get(threat.severity, 5)
        multiplier = min(threat.count / 5, 3)  # Cap multiplier at 3x
        score += weight * max(multiplier, 1)

    # Factor in failed login ratio
    if stats.total_lines > 0:
        fail_ratio = stats.failed_logins / stats.total_lines
        if fail_ratio > 0.3:
            score += 15
        elif fail_ratio > 0.1:
            score += 8

    return min(int(score), 100)
