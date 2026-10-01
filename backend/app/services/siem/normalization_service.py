"""Log Normalization Service for NexoraNet Step 15.

Normalizes heterogeneous educational security logs (Syslog, Windows Event XML,
CEF, CSV, JSON) into a unified SecurityEvent taxonomy without executing or resolving
any external artifacts.
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

from app.models.enums import (
    LogSourceType,
    RawLogFormat,
    SecurityEventAction,
    SecurityEventCategory,
    SecurityEventSeverity,
)


class LogNormalizationService:
    """Safely normalizes raw log content into canonical SecurityEvent attributes."""

    # Regex patterns for Syslog (RFC 3164 style)
    # e.g.: <134>Sep 30 14:20:00 web-server-01 sshd[1234]: Failed password for invalid user admin from 192.0.2.105 port 54321 ssh2
    SYSLOG_PATTERN = re.compile(
        r"^(?:<(?P<pri>\d+)>)?(?:(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}|[0-9T:.\-+Z]+)\s+)?(?P<host>[^\s:]+)\s+(?P<process>[^:\[\s]+)(?:\[(?P<pid>\d+)\])?:\s*(?P<message>.*)$"
    )

    # Regex for CEF format
    # CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
    CEF_PATTERN = re.compile(
        r"^CEF:\s*0\s*\|(?P<vendor>[^|]*)\|(?P<product>[^|]*)\|(?P<version>[^|]*)\|(?P<sig_id>[^|]*)\|(?P<name>[^|]*)\|(?P<severity>[^|]*)\|(?:(?P<ext>.*))?$"
    )

    @classmethod
    def normalize(
        cls,
        raw_message: str,
        log_format: str = RawLogFormat.JSON.value,
        default_source_type: str = LogSourceType.WINDOWS_SECURITY.value,
        default_timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Normalize raw log string into structured SecurityEvent field dictionary."""
        now = default_timestamp or datetime.now(timezone.utc)
        normalized: dict[str, Any] = {
            "timestamp": now,
            "event_type": "security_log",
            "event_category": SecurityEventCategory.SECURITY.value,
            "source_type": default_source_type,
            "host": None,
            "username": None,
            "source_ip": None,
            "source_port": None,
            "destination_ip": None,
            "destination_port": None,
            "protocol": None,
            "action": None,
            "status": "INFO",
            "severity": SecurityEventSeverity.INFO.value,
            "process_name": None,
            "parent_process": None,
            "command_summary": None,
            "file_name": None,
            "file_hash": None,
            "domain": None,
            "url": None,
            "authentication_method": None,
            "result": None,
            "message": raw_message[:1000].strip(),
            "metadata": {},
        }

        format_upper = (log_format or "JSON").upper()
        if format_upper == RawLogFormat.JSON.value or raw_message.strip().startswith("{"):
            cls._parse_json(raw_message, normalized)
        elif format_upper == RawLogFormat.WINDOWS_EVENT_XML.value or "<Event" in raw_message:
            cls._parse_windows_xml(raw_message, normalized)
        elif format_upper == RawLogFormat.CEF_LIKE.value or raw_message.startswith("CEF:"):
            cls._parse_cef(raw_message, normalized)
        elif format_upper == RawLogFormat.SYSLOG.value or cls.SYSLOG_PATTERN.match(raw_message):
            cls._parse_syslog(raw_message, normalized)
        elif format_upper == RawLogFormat.CSV.value:
            cls._parse_csv_line(raw_message, normalized)
        else:
            cls._parse_generic_text(raw_message, normalized)

        # Ensure timestamp is datetime with timezone
        if not isinstance(normalized["timestamp"], datetime):
            normalized["timestamp"] = now
        elif normalized["timestamp"].tzinfo is None:
            normalized["timestamp"] = normalized["timestamp"].replace(tzinfo=timezone.utc)

        # Convert metadata dictionary to JSON string
        if isinstance(normalized.get("metadata"), dict):
            normalized["metadata_json"] = json.dumps(normalized.pop("metadata"))
        else:
            normalized["metadata_json"] = json.dumps({})

        return normalized

    @classmethod
    def _parse_json(cls, raw: str, norm: dict[str, Any]) -> None:
        """Parse structured JSON log dictionary."""
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                return
        except (json.JSONDecodeError, TypeError):
            cls._parse_generic_text(raw, norm)
            return

        # Direct attribute mapping
        for key, target in [
            ("host", "host"),
            ("hostname", "host"),
            ("computer_name", "host"),
            ("user", "username"),
            ("username", "username"),
            ("user_name", "username"),
            ("src_ip", "source_ip"),
            ("source_ip", "source_ip"),
            ("client_ip", "source_ip"),
            ("dst_ip", "destination_ip"),
            ("destination_ip", "destination_ip"),
            ("server_ip", "destination_ip"),
            ("protocol", "protocol"),
            ("proto", "protocol"),
            ("action", "action"),
            ("status", "status"),
            ("severity", "severity"),
            ("process", "process_name"),
            ("process_name", "process_name"),
            ("parent_process", "parent_process"),
            ("command", "command_summary"),
            ("command_summary", "command_summary"),
            ("file_name", "file_name"),
            ("file_hash", "file_hash"),
            ("domain", "domain"),
            ("url", "url"),
            ("event_type", "event_type"),
            ("event_category", "event_category"),
            ("source_type", "source_type"),
            ("result", "result"),
            ("message", "message"),
        ]:
            if key in data and data[key] is not None:
                val = str(data[key]).strip()
                if val:
                    norm[target] = val

        # Ports
        for p_key, target in [
            ("src_port", "source_port"),
            ("source_port", "source_port"),
            ("dst_port", "destination_port"),
            ("destination_port", "destination_port"),
        ]:
            if p_key in data:
                try:
                    norm[target] = int(data[p_key])
                except (ValueError, TypeError):
                    pass

        # Timestamps
        for ts_key in ("timestamp", "time", "@timestamp", "event_time"):
            if data.get(ts_key):
                ts_val = data[ts_key]
                if isinstance(ts_val, (int, float)):
                    try:
                        norm["timestamp"] = datetime.fromtimestamp(ts_val, tz=timezone.utc)
                    except (ValueError, OSError):
                        pass
                elif isinstance(ts_val, str):
                    try:
                        norm["timestamp"] = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                    except ValueError:
                        pass

        # Deduce category and action if not set
        cls._harmonize_taxonomy(norm, data)
        norm["metadata"] = {k: v for k, v in data.items() if k not in norm}

    @classmethod
    def _parse_windows_xml(cls, raw: str, norm: dict[str, Any]) -> None:
        """Parse Windows Event Log XML representation (e.g. Security Log 4624, 4625, 4688)."""
        norm["source_type"] = LogSourceType.WINDOWS_SECURITY.value
        norm["event_category"] = SecurityEventCategory.AUTHENTICATION.value

        event_id = None
        data_dict: dict[str, str] = {}

        try:
            # Wrap in root if snippet lacks single parent
            wrapped = raw if raw.strip().startswith("<Event") else f"<Event>{raw}</Event>"
            root = ET.fromstring(wrapped)

            # Find EventID
            id_el = root.find(".//EventID")
            if id_el is None:
                id_el = root.find(".//{*}EventID")
            if id_el is not None and id_el.text:
                event_id = id_el.text.strip()

            # Find Computer
            comp_el = root.find(".//Computer")
            if comp_el is None:
                comp_el = root.find(".//{*}Computer")
            if comp_el is not None and comp_el.text:
                norm["host"] = comp_el.text.strip()

            # Find TimeCreated
            time_el = root.find(".//TimeCreated")
            if time_el is None:
                time_el = root.find(".//{*}TimeCreated")
            if time_el is not None:
                system_time = time_el.attrib.get("SystemTime")
                if system_time:
                    try:
                        norm["timestamp"] = datetime.fromisoformat(system_time.replace("Z", "+00:00"))
                    except ValueError:
                        pass

            # Extract Data elements
            for data_node in root.findall(".//Data") + root.findall(".//{*}Data"):
                name = data_node.attrib.get("Name")
                val = data_node.text
                if name and val:
                    data_dict[name] = val.strip()

        except ET.ParseError:
            # Fallback regex search for EventID
            m = re.search(r"EventID[>:]?\s*(\d+)", raw)
            if m:
                event_id = m.group(1)

        norm["metadata"] = data_dict

        # Windows Event ID Mappings
        if event_id == "4624":
            norm["event_type"] = "windows_logon_success"
            norm["event_category"] = SecurityEventCategory.AUTHENTICATION.value
            norm["action"] = SecurityEventAction.LOGIN.value
            norm["status"] = "SUCCESS"
            norm["result"] = "SUCCESS"
            norm["severity"] = SecurityEventSeverity.INFO.value
            norm["username"] = data_dict.get("TargetUserName") or norm.get("username")
            norm["source_ip"] = data_dict.get("IpAddress") or norm.get("source_ip")
            norm["message"] = f"An account was successfully logged on: {norm.get('username', 'Unknown')}"
        elif event_id == "4625":
            norm["event_type"] = "windows_logon_failure"
            norm["event_category"] = SecurityEventCategory.AUTHENTICATION.value
            norm["action"] = SecurityEventAction.LOGIN_FAILURE.value
            norm["status"] = "FAILURE"
            norm["result"] = "FAILURE"
            norm["severity"] = SecurityEventSeverity.LOW.value
            norm["username"] = data_dict.get("TargetUserName") or norm.get("username")
            norm["source_ip"] = data_dict.get("IpAddress") or norm.get("source_ip")
            norm["message"] = f"An account failed to log on: {norm.get('username', 'Unknown')}"
        elif event_id == "4740":
            norm["event_type"] = "windows_account_locked"
            norm["event_category"] = SecurityEventCategory.ACCOUNT.value
            norm["action"] = SecurityEventAction.ACCOUNT_DISABLED.value
            norm["status"] = "LOCKED"
            norm["severity"] = SecurityEventSeverity.MEDIUM.value
            norm["username"] = data_dict.get("TargetUserName") or norm.get("username")
            norm["message"] = f"A user account was locked out: {norm.get('username', 'Unknown')}"
        elif event_id == "4688":
            norm["event_type"] = "windows_process_creation"
            norm["event_category"] = SecurityEventCategory.PROCESS.value
            norm["action"] = SecurityEventAction.PROCESS_START.value
            norm["status"] = "SUCCESS"
            norm["severity"] = SecurityEventSeverity.INFO.value
            norm["process_name"] = data_dict.get("NewProcessName")
            norm["parent_process"] = data_dict.get("ParentProcessName")
            norm["command_summary"] = data_dict.get("CommandLine")
            norm["username"] = data_dict.get("SubjectUserName")
            norm["message"] = f"A new process was created: {norm.get('process_name', 'Unknown')}"
        elif event_id == "7045":
            norm["event_type"] = "windows_service_creation"
            norm["event_category"] = SecurityEventCategory.SYSTEM.value
            norm["action"] = SecurityEventAction.SERVICE_START.value
            norm["status"] = "SUCCESS"
            norm["severity"] = SecurityEventSeverity.MEDIUM.value
            norm["message"] = f"A new service was installed: {data_dict.get('ServiceName', 'Unknown')}"
        else:
            norm["event_type"] = f"windows_event_{event_id or 'unknown'}"
            norm["message"] = raw[:500]

    @classmethod
    def _parse_cef(cls, raw: str, norm: dict[str, Any]) -> None:
        """Parse ArcSight Common Event Format (CEF)."""
        m = cls.CEF_PATTERN.match(raw)
        if not m:
            cls._parse_generic_text(raw, norm)
            return

        norm["source_type"] = LogSourceType.IDS.value
        norm["event_type"] = m.group("sig_id") or "cef_event"
        norm["message"] = m.group("name") or "CEF Alert"

        # Severity mapping
        sev_str = (m.group("severity") or "1").strip().upper()
        if sev_str in ("10", "HIGH", "CRITICAL", "VERY HIGH"):
            norm["severity"] = SecurityEventSeverity.CRITICAL.value
        elif sev_str in ("7", "8", "9", "HIGH"):
            norm["severity"] = SecurityEventSeverity.HIGH.value
        elif sev_str in ("4", "5", "6", "MEDIUM"):
            norm["severity"] = SecurityEventSeverity.MEDIUM.value
        elif sev_str in ("1", "2", "3", "LOW"):
            norm["severity"] = SecurityEventSeverity.LOW.value
        else:
            norm["severity"] = SecurityEventSeverity.INFO.value

        # Parse key=value extension pairs
        ext = m.group("ext") or ""
        pairs = re.findall(r"(\w+)=([^=]+?)(?=\s+\w+=|$)", ext)
        ext_dict = {}
        for k, v in pairs:
            v_clean = v.strip()
            ext_dict[k] = v_clean
            if k in ("src", "source_ip", "suser_ip"):
                norm["source_ip"] = v_clean
            elif k in ("dst", "destination_ip", "duser_ip"):
                norm["destination_ip"] = v_clean
            elif k in ("spt", "src_port"):
                try:
                    norm["source_port"] = int(v_clean)
                except ValueError:
                    pass
            elif k in ("dpt", "dst_port"):
                try:
                    norm["destination_port"] = int(v_clean)
                except ValueError:
                    pass
            elif k in ("suser", "suid", "duser"):
                norm["username"] = v_clean
            elif k in ("shost", "dhost", "host"):
                norm["host"] = v_clean
            elif k in ("proto", "protocol"):
                norm["protocol"] = v_clean.upper()
            elif k in ("act", "action"):
                norm["action"] = v_clean.upper()

        norm["metadata"] = ext_dict
        cls._harmonize_taxonomy(norm, ext_dict)

    @classmethod
    def _parse_syslog(cls, raw: str, norm: dict[str, Any]) -> None:
        """Parse Linux / Unix Syslog lines."""
        m = cls.SYSLOG_PATTERN.match(raw)
        if not m:
            cls._parse_generic_text(raw, norm)
            return

        norm["host"] = m.group("host")
        process = m.group("process") or "syslog"
        norm["process_name"] = process
        msg = m.group("message")
        norm["message"] = msg

        # Specific Linux daemons
        if "sshd" in process.lower():
            norm["source_type"] = LogSourceType.LINUX_SSH.value
            norm["event_category"] = SecurityEventCategory.AUTHENTICATION.value
            norm["protocol"] = "SSH"
            norm["destination_port"] = 22

            if "Failed password" in msg or "authentication failure" in msg:
                norm["event_type"] = "linux_ssh_login_failure"
                norm["action"] = SecurityEventAction.LOGIN_FAILURE.value
                norm["status"] = "FAILURE"
                norm["result"] = "FAILURE"
                norm["severity"] = SecurityEventSeverity.LOW.value

                # Extract user & IP: "Failed password for invalid user admin from 192.0.2.105 port 54321"
                u_m = re.search(r"for (?:invalid user )?([^\s]+)", msg)
                if u_m:
                    norm["username"] = u_m.group(1)
                ip_m = re.search(r"from ([0-9a-fA-F:.]+) port (\d+)", msg)
                if ip_m:
                    norm["source_ip"] = ip_m.group(1)
                    norm["source_port"] = int(ip_m.group(2))

            elif "Accepted password" in msg or "Accepted publickey" in msg:
                norm["event_type"] = "linux_ssh_login_success"
                norm["action"] = SecurityEventAction.LOGIN.value
                norm["status"] = "SUCCESS"
                norm["result"] = "SUCCESS"
                norm["severity"] = SecurityEventSeverity.INFO.value
                u_m = re.search(r"for ([^\s]+)", msg)
                if u_m:
                    norm["username"] = u_m.group(1)
                ip_m = re.search(r"from ([0-9a-fA-F:.]+) port (\d+)", msg)
                if ip_m:
                    norm["source_ip"] = ip_m.group(1)
                    norm["source_port"] = int(ip_m.group(2))

        elif "sudo" in process.lower():
            norm["source_type"] = LogSourceType.LINUX_AUTH.value
            norm["event_category"] = SecurityEventCategory.PRIVILEGE.value
            norm["action"] = SecurityEventAction.PRIVILEGE_CHANGE.value
            norm["event_type"] = "linux_sudo_execution"
            norm["severity"] = SecurityEventSeverity.LOW.value
            u_m = re.search(r"([^\s]+)\s*:\s*COMMAND=(.*)", msg)
            if u_m:
                norm["username"] = u_m.group(1)
                norm["command_summary"] = u_m.group(2)
        elif "iptables" in msg.lower() or "firewall" in process.lower() or "ufw" in msg.lower():
            norm["source_type"] = LogSourceType.FIREWALL.value
            norm["event_category"] = SecurityEventCategory.FIREWALL.value
            if "drop" in msg.lower() or "block" in msg.lower() or "deny" in msg.lower():
                norm["action"] = SecurityEventAction.CONNECTION_BLOCKED.value
                norm["status"] = "BLOCKED"
                norm["severity"] = SecurityEventSeverity.LOW.value
            else:
                norm["action"] = SecurityEventAction.CONNECTION.value
                norm["status"] = "ALLOWED"

            # Parse SRC= and DST=
            src_m = re.search(r"SRC=([0-9a-fA-F:.]+)", msg)
            if src_m:
                norm["source_ip"] = src_m.group(1)
            dst_m = re.search(r"DST=([0-9a-fA-F:.]+)", msg)
            if dst_m:
                norm["destination_ip"] = dst_m.group(1)
            spt_m = re.search(r"SPT=(\d+)", msg)
            if spt_m:
                norm["source_port"] = int(spt_m.group(1))
            dpt_m = re.search(r"DPT=(\d+)", msg)
            if dpt_m:
                norm["destination_port"] = int(dpt_m.group(1))
            proto_m = re.search(r"PROTO=([A-Za-z0-9]+)", msg)
            if proto_m:
                norm["protocol"] = proto_m.group(1).upper()
        else:
            norm["source_type"] = LogSourceType.LINUX_SYSLOG.value
            norm["event_category"] = SecurityEventCategory.SYSTEM.value
            norm["event_type"] = f"linux_{process}"

    @classmethod
    def _parse_csv_line(cls, raw: str, norm: dict[str, Any]) -> None:
        """Parse comma-separated values line safely."""
        parts = [p.strip().strip('"\'') for p in raw.split(",")]
        # Heuristic mapping for standard 8-10 column CSV export
        # [timestamp, host, user, src_ip, dst_ip, dst_port, protocol, action, message]
        if len(parts) >= 8:
            norm["host"] = parts[1] or None
            norm["username"] = parts[2] or None
            norm["source_ip"] = parts[3] or None
            norm["destination_ip"] = parts[4] or None
            try:
                norm["destination_port"] = int(parts[5])
            except ValueError:
                pass
            norm["protocol"] = parts[6].upper() if parts[6] else None
            norm["action"] = parts[7].upper() if parts[7] else None
            if len(parts) >= 9:
                norm["message"] = parts[8]
        else:
            cls._parse_generic_text(raw, norm)

    @classmethod
    def _parse_generic_text(cls, raw: str, norm: dict[str, Any]) -> None:
        """Fallback regex extractor for IPs, domains, and actions from plain text."""
        # IP Extraction
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw)
        if len(ips) >= 1:
            norm["source_ip"] = ips[0]
        if len(ips) >= 2:
            norm["destination_ip"] = ips[1]

        # Domain Extraction
        dom = re.search(r"\b([a-zA-Z0-9][-a-zA-Z0-9]*\.(?:test|example|org|com|local))\b", raw)
        if dom:
            norm["domain"] = dom.group(1).lower()

        # Action heuristic
        raw_upper = raw.upper()
        if "FAIL" in raw_upper or "DENIED" in raw_upper or "REJECTED" in raw_upper:
            norm["status"] = "FAILURE"
            norm["action"] = SecurityEventAction.LOGIN_FAILURE.value
            norm["severity"] = SecurityEventSeverity.LOW.value
        elif "SUCCESS" in raw_upper or "ACCEPTED" in raw_upper:
            norm["status"] = "SUCCESS"
            norm["action"] = SecurityEventAction.LOGIN.value
        elif "BLOCKED" in raw_upper or "DROP" in raw_upper:
            norm["status"] = "BLOCKED"
            norm["action"] = SecurityEventAction.CONNECTION_BLOCKED.value

    @classmethod
    def _harmonize_taxonomy(cls, norm: dict[str, Any], context: dict[str, Any]) -> None:
        """Harmonize action, category, and severity into consistent taxonomy."""
        action = str(norm.get("action") or "").upper()
        category = str(norm.get("event_category") or "").upper()
        event_type = str(norm.get("event_type") or "").upper()

        # Check for DNS
        if "DNS" in event_type or "DNS" in category or norm.get("destination_port") == 53:
            norm["event_category"] = SecurityEventCategory.DNS.value
            norm["action"] = SecurityEventAction.DNS_QUERY.value
            norm["protocol"] = norm.get("protocol") or "DNS"
            if not norm.get("domain") and context.get("query"):
                norm["domain"] = str(context["query"]).lower()

        # Check for Firewall or blocked network action
        elif (
            action in ("DENY", "DROP", "REJECT", "BLOCK", "BLOCKED")
            or "FIREWALL" in category
            or "FIREWALL" in str(norm.get("source_type", "")).upper()
            or "DENY" in str(norm.get("message", "")).upper()
            or "DROP" in str(norm.get("message", "")).upper()
        ):
            if not norm.get("event_category") or norm.get("event_category") == SecurityEventCategory.SYSTEM.value:
                norm["event_category"] = SecurityEventCategory.FIREWALL.value
            if (
                action in ("DENY", "DROP", "REJECT", "BLOCK", "BLOCKED")
                or "DENY" in str(norm.get("message", "")).upper()
                or "DROP" in str(norm.get("message", "")).upper()
            ):
                norm["action"] = SecurityEventAction.CONNECTION_BLOCKED.value
                norm["status"] = "BLOCKED"
            else:
                norm["action"] = SecurityEventAction.CONNECTION.value

        # Check for Authentication
        elif (
            "LOGIN" in action
            or "AUTH" in category
            or "AUTH" in event_type
            or "LOGON" in event_type
        ):
            norm["event_category"] = SecurityEventCategory.AUTHENTICATION.value
            if "FAIL" in action or norm.get("status") == "FAILURE":
                norm["action"] = SecurityEventAction.LOGIN_FAILURE.value
            elif "OUT" in action:
                norm["action"] = SecurityEventAction.LOGOUT.value
            else:
                norm["action"] = SecurityEventAction.LOGIN.value

        # Check for Process
        elif "PROCESS" in category or "PROCESS" in event_type or norm.get("process_name"):
            norm["event_category"] = SecurityEventCategory.PROCESS.value
            if not norm.get("action"):
                norm["action"] = SecurityEventAction.PROCESS_START.value

        # Check for Web
        elif "WEB" in category or "HTTP" in event_type or norm.get("destination_port") in (80, 443, 8080):
            norm["event_category"] = SecurityEventCategory.WEB.value
            norm["protocol"] = norm.get("protocol") or "HTTP"
            if not norm.get("action"):
                norm["action"] = SecurityEventAction.CONNECTION.value
