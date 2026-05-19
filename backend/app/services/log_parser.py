"""
AI Security Analyst - Log Parser Service
Parses auth.log, syslog, and Apache access.log formats into unified LogEntry objects.
"""
import re
from typing import Generator
from ..models.schemas import LogEntry, LogFormat, SeverityLevel


# ── Regex patterns for different log formats ──────────────────────────────────

# auth.log: "May 10 09:15:23 server sshd[12345]: Failed password for root from 192.168.1.100 port 22 ssh2"
AUTH_LOG_PATTERN = re.compile(
    r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"  # timestamp
    r"(\S+)\s+"                                       # hostname
    r"(\S+?)(?:\[(\d+)\])?:\s+"                       # service[pid]:
    r"(.+)$"                                          # message
)

# Apache access.log: '192.168.1.100 - - [10/May/2025:09:15:23 +0000] "GET /index.html HTTP/1.1" 200 1234'
APACHE_ACCESS_PATTERN = re.compile(
    r'^(\S+)\s+'                                       # source IP
    r'(\S+)\s+(\S+)\s+'                                # ident, authuser
    r'\[([^\]]+)\]\s+'                                 # timestamp
    r'"(\S+)\s+(\S+)\s+(\S+)"\s+'                      # method, path, protocol
    r'(\d{3})\s+'                                      # status code
    r'(\d+|-)'                                         # size
    r'(?:\s+"([^"]*)")?\s*'                            # referer (optional)
    r'(?:"([^"]*)")?'                                  # user-agent (optional)
)

# syslog: "May 10 09:15:23 server kernel: [12345.678] UFW BLOCK IN=eth0 ..."
SYSLOG_PATTERN = re.compile(
    r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"  # timestamp
    r"(\S+)\s+"                                       # hostname
    r"(\S+?)(?:\[(\d+)\])?:\s+"                       # service[pid]:
    r"(.+)$"                                          # message
)

# Sub-patterns for extracting security-relevant info from messages
FAILED_PASSWORD_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?(\S+) from ([\d.]+) port (\d+)"
)
ACCEPTED_PASSWORD_PATTERN = re.compile(
    r"Accepted (?:password|publickey) for (\S+) from ([\d.]+) port (\d+)"
)
INVALID_USER_PATTERN = re.compile(
    r"Invalid user (\S+) from ([\d.]+)"
)
CONNECTION_CLOSED_PATTERN = re.compile(
    r"Connection closed by (?:authenticating user )?(\S+)?\s*([\d.]+)?\s*port"
)
SUDO_PATTERN = re.compile(
    r"sudo:\s+(\S+)\s+:.*COMMAND=(.*)"
)
UFW_BLOCK_PATTERN = re.compile(
    r"UFW BLOCK.*SRC=([\d.]+).*DST=([\d.]+).*(?:PROTO=(\S+))?.*(?:DPT=(\d+))?"
)
SQL_INJECTION_PATTERN = re.compile(
    r"(?:union\s+select|or\s+1=1|drop\s+table|;\s*--|'\s*or\s*'|<script)",
    re.IGNORECASE
)
DIRECTORY_TRAVERSAL_PATTERN = re.compile(
    r"(?:\.\./|\.\.\\|%2e%2e|%252e%252e)",
    re.IGNORECASE
)


def detect_log_format(content: str) -> LogFormat:
    """Auto-detect the log file format from the first few lines."""
    lines = content.strip().split("\n")[:20]

    apache_matches = 0
    auth_matches = 0

    for line in lines:
        if APACHE_ACCESS_PATTERN.match(line.strip()):
            apache_matches += 1
        if AUTH_LOG_PATTERN.match(line.strip()):
            auth_matches += 1
            # Check for auth-specific keywords
            if any(kw in line.lower() for kw in ["sshd", "sudo", "pam", "auth", "login", "passwd"]):
                auth_matches += 2

    if apache_matches > len(lines) * 0.3:
        return LogFormat.APACHE_ACCESS
    if auth_matches > 0:
        # Further distinguish auth.log vs generic syslog
        auth_keywords = sum(
            1 for line in lines
            if any(kw in line.lower() for kw in ["sshd", "sudo", "pam", "login", "passwd", "auth", "failed password", "accepted"])
        )
        if auth_keywords > len(lines) * 0.2:
            return LogFormat.AUTH_LOG
        return LogFormat.SYSLOG

    return LogFormat.UNKNOWN


def parse_auth_line(line: str, line_number: int) -> LogEntry:
    """Parse a single auth.log line."""
    entry = LogEntry(raw_line=line, line_number=line_number)

    match = AUTH_LOG_PATTERN.match(line.strip())
    if not match:
        entry.message = line.strip()
        return entry

    entry.timestamp = match.group(1)
    entry.hostname = match.group(2)
    entry.service = match.group(3)
    entry.pid = match.group(4)
    entry.message = match.group(5)

    # Extract security details from message
    msg = entry.message

    # Failed password
    fp_match = FAILED_PASSWORD_PATTERN.search(msg)
    if fp_match:
        entry.username = fp_match.group(1)
        entry.source_ip = fp_match.group(2)
        entry.action = "failed_login"
        entry.severity = SeverityLevel.MEDIUM
        return entry

    # Accepted password
    ap_match = ACCEPTED_PASSWORD_PATTERN.search(msg)
    if ap_match:
        entry.username = ap_match.group(1)
        entry.source_ip = ap_match.group(2)
        entry.action = "successful_login"
        entry.severity = SeverityLevel.INFO
        return entry

    # Invalid user
    iu_match = INVALID_USER_PATTERN.search(msg)
    if iu_match:
        entry.username = iu_match.group(1)
        entry.source_ip = iu_match.group(2)
        entry.action = "invalid_user"
        entry.severity = SeverityLevel.MEDIUM
        return entry

    # Sudo commands
    sudo_match = SUDO_PATTERN.search(msg)
    if sudo_match:
        entry.username = sudo_match.group(1)
        entry.action = "sudo_command"
        entry.severity = SeverityLevel.LOW
        return entry

    # Connection closed
    cc_match = CONNECTION_CLOSED_PATTERN.search(msg)
    if cc_match:
        entry.username = cc_match.group(1)
        entry.source_ip = cc_match.group(2)
        entry.action = "connection_closed"
        entry.severity = SeverityLevel.LOW
        return entry

    entry.action = "other"
    return entry


def parse_apache_line(line: str, line_number: int) -> LogEntry:
    """Parse a single Apache access.log line."""
    entry = LogEntry(raw_line=line, line_number=line_number)

    match = APACHE_ACCESS_PATTERN.match(line.strip())
    if not match:
        entry.message = line.strip()
        return entry

    entry.source_ip = match.group(1)
    entry.timestamp = match.group(4)
    method = match.group(5)
    path = match.group(6)
    status = match.group(8)
    user_agent = match.group(11) if match.group(11) else ""

    entry.message = f"{method} {path} -> {status}"
    entry.hostname = entry.source_ip

    # Detect web attacks
    full_request = f"{path} {user_agent}"

    if SQL_INJECTION_PATTERN.search(full_request):
        entry.action = "sql_injection_attempt"
        entry.severity = SeverityLevel.CRITICAL
        return entry

    if DIRECTORY_TRAVERSAL_PATTERN.search(path):
        entry.action = "directory_traversal"
        entry.severity = SeverityLevel.HIGH
        return entry

    status_int = int(status)
    if status_int == 404:
        entry.action = "not_found"
        entry.severity = SeverityLevel.LOW
    elif status_int == 403:
        entry.action = "forbidden"
        entry.severity = SeverityLevel.MEDIUM
    elif status_int >= 500:
        entry.action = "server_error"
        entry.severity = SeverityLevel.HIGH
    elif status_int == 200:
        entry.action = "success"
        entry.severity = SeverityLevel.INFO
    else:
        entry.action = f"http_{status}"
        entry.severity = SeverityLevel.INFO

    return entry


def parse_syslog_line(line: str, line_number: int) -> LogEntry:
    """Parse a single syslog line."""
    entry = LogEntry(raw_line=line, line_number=line_number)

    match = SYSLOG_PATTERN.match(line.strip())
    if not match:
        entry.message = line.strip()
        return entry

    entry.timestamp = match.group(1)
    entry.hostname = match.group(2)
    entry.service = match.group(3)
    entry.pid = match.group(4)
    entry.message = match.group(5)

    msg = entry.message

    # UFW Block
    ufw_match = UFW_BLOCK_PATTERN.search(msg)
    if ufw_match:
        entry.source_ip = ufw_match.group(1)
        entry.action = "firewall_block"
        entry.severity = SeverityLevel.MEDIUM
        return entry

    # Kernel errors
    if "error" in msg.lower() or "fail" in msg.lower():
        entry.action = "error"
        entry.severity = SeverityLevel.MEDIUM
    elif "warning" in msg.lower() or "warn" in msg.lower():
        entry.action = "warning"
        entry.severity = SeverityLevel.LOW
    else:
        entry.action = "info"
        entry.severity = SeverityLevel.INFO

    return entry


def parse_log_content(content: str) -> tuple[list[LogEntry], LogFormat]:
    """
    Parse log file content into a list of LogEntry objects.
    Auto-detects the log format.
    """
    log_format = detect_log_format(content)
    lines = content.strip().split("\n")
    entries = []

    parser_fn = {
        LogFormat.AUTH_LOG: parse_auth_line,
        LogFormat.APACHE_ACCESS: parse_apache_line,
        LogFormat.SYSLOG: parse_syslog_line,
        LogFormat.UNKNOWN: parse_syslog_line,  # fallback
    }[log_format]

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        entry = parser_fn(line, i)
        entries.append(entry)

    return entries, log_format
