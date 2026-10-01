# SOC Investigation Management & Forensic Reporting

## 1. Overview

An **Investigation** is an analytical workspace where analysts gather evidence, formulate scientific hypotheses, test conclusions, and synthesize technical incident reports.

---

## 2. Hypothesis-Driven Analysis Model

In NexoraNet, investigations follow the scientific method:

1. **Hypothesis Formulation**:
   - The analyst articulates an explanatory statement (e.g., *"Host 192.168.1.50 is conducting an automated port sweep targeting SSH port 22"*).
2. **Evidence Association**:
   - Telemetry evidence (specific packet numbers, conversation volume, protocol headers) is bound to the hypothesis.
3. **Hypothesis Validation State**:
   - `UNTESTED`: Newly registered hypothesis awaiting telemetry verification.
   - `SUPPORTED`: Validated by concrete corroborating packet evidence.
   - `NOT_SUPPORTED`: Refuted by contradictory observations (e.g. valid application traffic).
   - `INCONCLUSIVE`: Telemetry lacks sufficient depth to reach a definitive verdict.

---

## 3. Forensic Findings & Reporting

When hypotheses are supported by evidence, analysts record formal **Findings**:
- **Title & Description**: Clear synopsis of what occurred.
- **Evidence Summary**: Summary of bound packets and telemetry metrics.
- **Confidence Rating**: `HIGH`, `MEDIUM`, or `LOW`.

### Exportable Forensic Dossier
The workspace compiles the entire investigation into an industry-standard structured JSON incident dossier (`GET /api/v1/soc/investigations/{id}/report`), detailing:
- Sequential Investigation ID (`INV-YYYY-XXXX`)
- Bound detection alerts
- Raw packet evidence items
- Validated hypotheses and status history
- Analyst chronological notes
- Final conclusions and recommended defensive remediation
