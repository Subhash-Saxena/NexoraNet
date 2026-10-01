# NexoraNet Detection Engine Security & Isolation

> **Classification:** Defensive Educational Platform Security  
> **Module:** Step 11 — Network Detection Engine

---

## 1. Safety Principles & Defensive Boundaries

The NexoraNet Network Detection Engine is designed specifically as a **safe, defensive, educational analysis environment**.

The engine strictly enforces the following boundaries:

```text
               +-------------------------------------------+
               |  NEXORANET DETECTION SECURITY PERIMETER   |
               +-------------------------------------------+
                                     |
    [ALLOWED / ENFORCED]             |      [STRICTLY PROHIBITED]
    - Offline PCAP metadata analysis |      - Live network sniffing
    - Synthetic trace evaluation     |      - Raw packet transmission
    - Deterministic threshold checks |      - Packet replay or injection
    - SQLite telemetry queries       |      - Dynamic eval() / exec()
    - Static JSON rule definitions   |      - Payload binary execution
    - SOC triage audit history       |      - Outbound API callbacks
```

---

## 2. Key Protections

### A. Telemetry as Data, Never Instructions
Packets ingested from PCAP files or simulator sessions are treated strictly as **immutable data**.
- No binary payload extracted from a packet is ever saved with executable permissions or executed.
- Shellcode, exploit strings, or script payloads contained inside packet captures remain dormant text fields in the database.

### B. Zero Network Interception & Sniffing
The system does not initialize promiscuous socket listeners (e.g. `pcap_open_live` or `AF_PACKET`) on host machine network interfaces.
All analysis is performed post-capture on files already stored on disk.

### C. Zero Active Probing or Packet Injection
The detection engine is read-only with respect to network hardware. It does not send TCP RSTs, firewall blocks, or active counter-probes. Active response automation is intentionally excluded from Step 11 to preserve educational safety.

### D. Safe Rule Evaluation Sandbox
- Custom or built-in rules do not execute arbitrary Python scripts or shell commands.
- All detection logic is mapped to pre-compiled, parameter-checked logic routines (`SYN_BURST_DETECTION`, `DNS_NXDOMAIN_BURST`, etc.).
- Regex evaluations (such as cleartext credential matching) are bounded to prevent catastrophic backtracking (ReDoS).

---

## 3. Data Privacy & Local Storage

All telemetry, rules, alerts, and analyst notes are stored locally in the application's SQLite database (`backend/nexoranet.db`).
No student analysis data, capture telemetry, or system information is shared externally.
