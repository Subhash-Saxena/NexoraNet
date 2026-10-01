# SOC Incident Case Management

## 1. Overview

While an **Investigation** analyzes a specific anomaly or threat actor activity, an **Incident Case** (`Case`) acts as a top-level managerial container grouping multiple investigations, alerts, and operational notes into a cohesive incident tracking entity.

---

## 2. Structure & Relationships

```text
CASE (e.g. CASE-2026-0001: Subnet Reconnaissance & Lateral Probing)
 │
 ├── Investigation 1: Port Sweep against Web Servers (INV-2026-0001)
 │    ├── Alert #101: TCP SYN Scan
 │    └── Alert #102: Port 22 Probing Burst
 │
 ├── Investigation 2: DNS Tunneling Anomaly (INV-2026-0002)
 │    └── Alert #105: Excessive NXDOMAIN Query Rate
 │
 └── Case Timeline & Operational Notes
```

---

## 3. Case Lifecycle States

- `OPEN`: Incident declared; team is aggregating related investigations and affected assets.
- `INVESTIGATING`: Active analysis underway across linked investigations.
- `PENDING`: Awaiting additional PCAP telemetry or system owner input.
- `RESOLVED`: Defensive actions recommended and root cause identified.
- `CLOSED`: Post-incident review complete; case archived.
