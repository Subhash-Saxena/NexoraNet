# SIEM & Security Log Analysis Defensive Safeguards

**Step 15 — Platform Security, Offline Constraints & Educational Guardrails**  
*Platform Tagline: "Learn. Simulate. Analyze. Defend."*

---

## 1. Safety Principles & Guardrails

The NexoraNet SIEM is an educational learning engine designed under strict defensive and offline constraints:

```text
[NO LIVE AGENTS] ──> [NO SOCKET LISTENERS] ──> [NO SSRF] ──> [NO CODE EXECUTION]
       │                        │                     │                 │
       ▼                        ▼                     ▼                 ▼
Offline Synthetic       Safe REST Ingestion    RFC 5737 Scoped    Deterministic AST
  Telemetry Only          Payload Limits          IP Ranges         Query Parser
```

* **Zero Endpoint Agents**: No software agents (e.g. Winlogbeat, Osquery, Wazuh agents) are installed or run on the host system.
* **Zero Live Packet Capture**: Live network traffic is never captured, intercepted, or replayed.
* **Zero Network Transmission**: The SIEM does not emit network traffic, perform active port scans, or contact external servers.
* **Deterministic AST Evaluation**: Queries and correlation rules are parsed via typed AST representations and SQLAlchemy ORM statements; no `eval()`, `exec()`, or raw string interpolation is permitted.

---

## 2. Ingestion Defense & Spreadsheet Formula Injection Protection

When analysts export log data to spreadsheets, malicious input starting with formula trigger symbols (`=`, `+`, `-`, `@`, `\t`, `\r`) can execute unauthorized local macros or commands in spreadsheet applications.

NexoraNet automatically sanitizes all string fields during ingestion:
```python
@classmethod
def sanitize_field(cls, value: str | None) -> str | None:
    if not value or not isinstance(value, str):
        return value
    trimmed = value.strip()
    if trimmed.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{trimmed}"
    return trimmed
```

---

## 3. Payload and Resource Quotas

To prevent denial of service through oversized uploads or resource exhaustion:
* **Payload Limit**: Ingested content is strictly capped at **5 MB**. Uploads exceeding 5 MB are rejected immediately with a `ValueError`.
* **Record Count Cap**: Maximum **2,000 log events** per ingestion transaction.
* **Message Truncation**: Raw messages are truncated to 5,000 characters; metadata JSON strings are bounded.
* **Whitelisted Field Queries**: Search queries can only operate against indexed, whitelisted schema fields, preventing arbitrary database introspection or SQL injection.

---

## 4. Documentation IP Address Standards

All synthetic datasets and simulated threat scenarios strictly use reserved documentation address space:
* **IPv4 Blocks**:
  * `192.0.2.0/24` (TEST-NET-1, RFC 5737)
  * `198.51.100.0/24` (TEST-NET-2, RFC 5737)
  * `203.0.113.0/24` (TEST-NET-3, RFC 5737)
* **Domain Names**: Reserved top-level domains (`.test`, `.example`, `.invalid`, RFC 2606)
