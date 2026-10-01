"""Incident Report Generation Service for Step 17.

Produces comprehensive NIST SP 800-61 post-incident reports and executive briefs.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.services.incident_response.incident_service import IncidentService


class ReportService:
    """Generates structured educational post-incident reports and executive briefings."""

    @classmethod
    def generate_incident_report(cls, db: Session, incident_id_or_int: str | int) -> dict[str, Any]:
        incident = IncidentService.get_incident(db, incident_id_or_int)
        if not incident:
            raise ValueError(f"Incident {incident_id_or_int} not found")

        # Compile sections
        tactics_observed = sorted({
            mapping.technique.tactic.name
            for mapping in incident.technique_mappings
            if mapping.technique and mapping.technique.tactic
        })

        techniques_observed = [
            {
                "technique_id": m.technique.technique_id,
                "name": m.technique.name,
                "confidence": m.mapping_confidence,
                "evidence": m.evidence_summary,
            }
            for m in incident.technique_mappings
            if m.technique
        ]

        evidence_items = [
            {
                "evidence_id": ev.evidence_id,
                "title": ev.title,
                "type": ev.evidence_type,
                "source": ev.source_engine,
                "hash_sha256": ev.hash_sha256,
                "relevance": ev.relevance,
            }
            for ev in incident.evidence
        ]

        timeline_entries = [
            {
                "timestamp": t.timestamp.isoformat(),
                "title": t.title,
                "category": t.event_category,
                "is_milestone": t.is_milestone,
            }
            for t in sorted(incident.timeline_events, key=lambda x: x.timestamp)
        ]

        actions_taken = [
            {
                "action_id": a.action_id,
                "type": a.action_type,
                "category": a.category,
                "target": a.target_identifier,
                "status": a.status,
                "executed_at": a.executed_at.isoformat() if a.executed_at else None,
                "outcome": a.simulated_outcome,
            }
            for a in incident.response_actions
        ]

        hypotheses_tested = [
            {
                "id": h.hypothesis_id,
                "statement": h.statement,
                "status": h.status,
                "confidence": h.confidence,
                "rationale": h.rationale,
            }
            for h in incident.hypotheses
        ]

        findings = [
            {
                "id": f.finding_id,
                "title": f.title,
                "severity": f.severity,
                "affected_systems": f.affected_systems,
                "mitre_technique": f.mitre_technique,
            }
            for f in incident.findings
        ]

        # Generate markdown report
        md_lines = [
            f"# INCIDENT REPORT: {incident.title}",
            f"**Incident ID:** {incident.incident_id}  |  **Severity:** {incident.severity}  |  **Status:** {incident.status}",
            f"**Classification:** {incident.classification}  |  **Lead Analyst:** {incident.lead_analyst or 'Unassigned'}",
            f"**Detection Time:** {incident.detected_at.strftime('%Y-%m-%d %H:%M UTC')}  |  **Phase:** {incident.phase}",
            "\n---",
            "\n## 1. Executive Summary",
            incident.summary or incident.description or "No executive summary recorded.",
            "\n## 2. Business & Technical Impact",
            incident.impact_assessment or "Impact assessment pending completion.",
            "\n## 3. MITRE ATT&CK Matrix Alignment",
            f"**Observed Tactics:** {', '.join(tactics_observed) if tactics_observed else 'None'}",
            "\n| Technique ID | Technique Name | Confidence | Evidence Summary |",
            "|--------------|----------------|------------|------------------|",
        ]

        for t in techniques_observed:
            md_lines.append(f"| `{t['technique_id']}` | {t['name']} | {t['confidence']} | {t['evidence'] or 'Observed'} |")

        md_lines.extend([
            "\n## 4. Key Evidence Collected & Chain of Custody",
            "| Evidence ID | Title | Type | Source Engine | SHA-256 Hash | Relevance |",
            "|-------------|-------|------|---------------|--------------|-----------|",
        ])
        for ev in evidence_items:
            h_short = (ev["hash_sha256"][:12] + "...") if ev["hash_sha256"] else "N/A"
            md_lines.append(f"| `{ev['evidence_id']}` | {ev['title']} | {ev['type']} | {ev['source']} | `{h_short}` | {ev['relevance']} |")

        md_lines.extend([
            "\n## 5. Timeline of Key Events",
        ])
        for tl in timeline_entries:
            star = "★ " if tl["is_milestone"] else "- "
            md_lines.append(f"{star}**{tl['timestamp']}** — [{tl['category']}] {tl['title']}")

        md_lines.extend([
            "\n## 6. Simulated Response Actions Executed",
            "| Action ID | Category | Type | Target | Status | Simulated Outcome |",
            "|-----------|----------|------|--------|--------|-------------------|",
        ])
        for a in actions_taken:
            outcome_snippet = (a["outcome"][:50] + "...") if a["outcome"] and len(a["outcome"]) > 50 else (a["outcome"] or "Pending")
            md_lines.append(f"| `{a['action_id']}` | {a['category']} | `{a['type']}` | {a['target']} | {a['status']} | {outcome_snippet} |")

        md_lines.extend([
            "\n## 7. Root Cause Analysis",
            incident.root_cause or "Root cause investigation underway.",
            "\n## 8. Lessons Learned & Recommendations",
            f"**Lessons Learned:**\n{incident.lessons_learned or 'To be discussed during post-incident review.'}",
            f"\n**Strategic Recommendations:**\n{incident.recommendations or 'No remediation items specified yet.'}",
            "\n\n*Document generated by NexoraNet Educational Incident Response Workbench. Strictly synthetic training data.*",
        ])

        markdown_content = "\n".join(md_lines)

        return {
            "incident_id": incident.incident_id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "phase": incident.phase,
            "classification": incident.classification,
            "lead_analyst": incident.lead_analyst,
            "detected_at": incident.detected_at.isoformat(),
            "contained_at": incident.contained_at.isoformat() if incident.contained_at else None,
            "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
            "tactics_observed": tactics_observed,
            "techniques_observed": techniques_observed,
            "evidence_count": len(evidence_items),
            "evidence_items": evidence_items,
            "timeline_entries": timeline_entries,
            "actions_taken": actions_taken,
            "hypotheses_tested": hypotheses_tested,
            "findings": findings,
            "markdown_report": markdown_content,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
