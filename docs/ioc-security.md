# Threat Intelligence Security, Safety Boundaries & Defenses

## 1. Offline Defensive Sandbox

NexoraNet is an educational learning platform designed with strict defensive safety controls. In Step 13, all threat intelligence and indicator investigation operations are isolated:

```text
[ Incoming IOC Data ]
        │
        ▼
[ Normalization Engine ] ──► [ Local DB / Cache ] ──► [ Student UI ]
        │
        ▼ (NO NETWORK EGRESS)
   [ 🛑 BLOCKED ]
 (No HTTP Fetch / No Socket Egress / No DNS Resolution)
```

### Absolute Constraints:
1. **Zero External HTTP Requests (SSRF Defense):** The backend never attempts to connect to or fetch URLs, domains, or IP addresses stored as indicators. Lookups are strictly internal against local synthetic tables and cache.
2. **Zero Active Scanning:** No port scans, vulnerability scans, or active probes are launched against any indicator.
3. **Zero Packet Transmission:** No raw sockets, packet injection, or packet replay.
4. **Indicators as Passive Data:** Indicator values are strings stored in text columns; they are never passed to system shells, `eval()`, or execution engines.

---

## 2. Safe Import & Export Defenses

The `ImportExportService` enforces multi-layer input validation and payload sanitization:

### File Caps & Limits
- **Maximum File Payload:** 5 MB (`MAX_FILE_BYTES = 5 * 1024 * 1024`). Files exceeding this size are rejected with HTTP 413.
- **Maximum Batch Count:** 1,000 indicators per upload (`MAX_INDICATOR_ROWS = 1000`). Prevents resource exhaustion and denial of service.

### CSV Formula Injection Mitigation
When exported data is opened in spreadsheet software (Microsoft Excel, LibreOffice Calc, Google Sheets), values starting with formula control characters can execute arbitrary commands or leak data via DDE / formula execution.

NexoraNet neutralizes formula prefixes:
- Any exported field starting with `=`, `+`, `-`, `@`, `\t`, or `\r` is escaped with a prepended single quote (`'`).
- On batch import, formula prefixes attempting injection are sanitized and stripped before normalization.

---

## 3. Authorization & IDOR Protections

- **Analyst Watchlists:** Watchlist items belong to specific authenticated student profiles. Deletions and removals verify ownership (`item.user_id == user.id`), preventing Insecure Direct Object References (IDOR).
- **Challenge Submissions:** Challenge evaluations record student attempt history and feedback scoped strictly to the authenticated user session.
