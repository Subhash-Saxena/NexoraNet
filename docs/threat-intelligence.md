# NexoraNet Threat Intelligence & IOC Investigation System

## 1. Overview & Purpose

The **NexoraNet Threat Intelligence & IOC Investigation System** (Step 13) provides students and aspiring SOC analysts with an offline, deterministic, and explainable threat intelligence platform.

In modern cybersecurity operations, threat intelligence enriches security alerts and telemetry with actionable context, threat actor attribution, and behavioral indicators. However, junior analysts frequently misunderstand threat data:
- Believing that an IOC match is an automatic proof of breach.
- Assuming that unknown indicators are safe or benign.
- Treating external feeds as unquestioned absolute truth.

NexoraNet instills core operational principles through hands-on practice:
```text
ALERT → OBSERVED ARTIFACT → EXTRACT IOC → NORMALIZE → CLASSIFY → ENRICH → VALIDATE → CORRELATE → INVESTIGATE → DOCUMENT → DETECTION / CASE
```

### Core Educational Tenets
1. **IOC ≠ Incident:** An indicator match provides evidentiary lead material, not automated proof of system compromise.
2. **Unknown ≠ Benign:** The absence of threat intelligence records does not indicate safety; zero-day or targeted threats lack prior indicators.
3. **Source Reliability ≠ Indicator Confidence:** An assessment from a reliable feed might still have low confidence due to limited observational corroboration.
4. **Defensive Posture:** All indicators are treated strictly as **DATA ONLY**, never executed, resolved, or requested externally.

---

## 2. Architectural Components

```text
┌─────────────────────────────────────────────────────────────┐
│                    Student SOC Workstation                  │
│   (Dashboard, Indicator Repo, Search, Watchlist, Graph,     │
│                     Challenges Workspace)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP REST
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Engine Router                    │
│                 /api/v1/threat-intel/*                      │
├──────────────────────────────┬──────────────────────────────┤
│ Core Services:                                              │
│  - NormalizationService      (Canonicalization, Defanging)  │
│  - ExtractionService         (Passive Packet & Text Parsing)│
│  - SyntheticProvider         (Local Educational Repository) │
│  - IndicatorService          (Lifecycle, Graphs, Correlation│
│  - WatchlistService          (Student Priority Monitoring)  │
│  - ImportExportService       (Size Capped, Formula-Safe)    │
│  - ChallengeService          (5-Criteria Rubric Evaluation) │
├──────────────────────────────┴──────────────────────────────┤
│ Storage Layer (SQLite / Alembic Migrations)                  │
│  - threat_intel_sources      - indicators                   │
│  - indicator_relationships   - indicator_observations       │
│  - indicator_timelines       - indicator_notes              │
│  - indicator_watchlists      - threat_intel_challenges      │
│  - threat_intel_challenge_attempts                          │
│  - threat_intel_enrichment_cache                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Workflow Integration

The Threat Intelligence engine integrates directly with preceding NexoraNet subsystems:
- **Packet Analysis Engine (Step 10):** Direct extraction from parsed Ethernet, IPv4, IPv6, TCP, UDP, DNS queries, and HTTP/TLS hostnames.
- **Network Detection Engine (Step 11):** Correlation with detection alerts matching source and destination IP addresses or domain anomalies.
- **Mini SOC Dashboard (Step 12):** Cross-linking between SOC alerts, investigations, and threat indicators, allowing analysts to formulate hypotheses backed by intelligence reputation.
