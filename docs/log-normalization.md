# SIEM Log Normalization & Taxonomy Harmonization

**Step 15 — Log Parsing, Ingestion, and Harmonization Guide**  
*Platform Tagline: "Learn. Simulate. Analyze. Defend."*

---

## 1. The Normalization Problem

In an enterprise security ecosystem, telemetry originates from heterogeneous platforms:
* Windows Domain Controllers record XML logon events (`EventID 4625`)
* Linux bastion hosts emit RFC 3164 Syslog messages (`sshd[1234]: Failed password...`)
* Cisco ASA Firewalls generate ArcSight Common Event Format (CEF) drops (`act=DROP`)
* Cloud authentication proxies stream structured JSON records

Without normalization, an analyst must learn dozens of vendor-specific query syntaxes. The NexoraNet Normalization Engine extracts and unifies critical observables into the standard `SecurityEvent` schema.

---

## 2. Standard Security Event Taxonomy

All ingested logs are mapped to the following normalized attributes:

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `timestamp` | `DateTime (UTC)` | Event occurrence timestamp | `2026-09-30T14:00:00Z` |
| `event_category` | `Enum` | Functional category | `AUTHENTICATION`, `FIREWALL`, `DNS`, `PROCESS`, `WEB` |
| `event_type` | `String` | Specific event identifier | `windows_logon_failure`, `linux_ssh_login` |
| `source_type` | `Enum` | Generating technology | `WINDOWS_SECURITY`, `LINUX_SSH`, `FIREWALL` |
| `host` | `String` | System or machine hostname | `DC01.corp.test`, `server01` |
| `username` | `String` | Subject or target identity | `alice.smith`, `admin` |
| `source_ip` | `String` | Originating IPv4/IPv6 | `198.51.100.45` |
| `source_port` | `Integer` | Ephemeral client port | `51234` |
| `destination_ip` | `String` | Target server IPv4/IPv6 | `192.0.2.10` |
| `destination_port`| `Integer` | Service port | `22`, `445`, `80` |
| `protocol` | `String` | Transport/App protocol | `TCP`, `UDP`, `SSH`, `HTTP`, `DNS` |
| `action` | `Enum` | Harmonized action code | `LOGIN`, `LOGIN_FAILURE`, `CONNECTION_BLOCKED` |
| `severity` | `Enum` | Unified severity | `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `domain` | `String` | Queried domain name | `c2-listener.test` |
| `process_name` | `String` | Executable process | `cmd.exe`, `powershell.exe`, `sshd` |

---

## 3. Supported Parsers

### 3.1 Windows Event XML
Parses structured `<Event>` XML trees:
* **Event 4624**: Successful Logon (`action=LOGIN`, `status=SUCCESS`)
* **Event 4625**: Failed Logon (`action=LOGIN_FAILURE`, `status=FAILURE`, `severity=LOW`)
* **Event 4688**: Process Creation (`action=PROCESS_START`, extracts `CommandLine`)
* **Event 4740**: User Account Locked Out (`action=ACCOUNT_DISABLED`)
* **Event 7045**: New Service Installed (`action=SERVICE_START`, `severity=MEDIUM`)

### 3.2 Linux / Unix Syslog
Regex-based extraction following RFC 3164/5424 formats:
* `sshd`: Parses failed and accepted passwords, usernames, and remote source IPs.
* `sudo`: Parses privilege escalation execution, target commands, and username.
* `iptables` / `ufw`: Extracts `SRC=`, `DST=`, `SPT=`, `DPT=`, `PROTO=`, mapping drops to `CONNECTION_BLOCKED`.

### 3.3 ArcSight Common Event Format (CEF)
Parses pipe-delimited headers and key-value extension pairs:
```text
CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]
```
Maps `src`, `dst`, `spt`, `dpt`, `suser`, `proto`, and converts `act=DROP` / `act=DENY` into `CONNECTION_BLOCKED`.

### 3.4 Structured JSON & CSV
Parses standard exports with sanitization against spreadsheet formula injection prefixes (`=`, `+`, `-`, `@`).
