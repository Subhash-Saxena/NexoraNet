"""Incident Response, Case Management & MITRE ATT&CK API Endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.models.incident import IncidentFinding, IncidentHypothesis
from app.schemas.incident_response import (
    AttackTacticResponse,
    AttackTechniqueResponse,
    EscalateAlertRequest,
    IncidentCreate,
    IncidentDetailResponse,
    IncidentEvidenceCreate,
    IncidentEvidenceResponse,
    IncidentEvidenceUpdate,
    IncidentFindingCreate,
    IncidentFindingResponse,
    IncidentHypothesisCreate,
    IncidentHypothesisResponse,
    IncidentHypothesisUpdate,
    IncidentListResponse,
    IncidentNoteCreate,
    IncidentNoteResponse,
    IncidentPlaybookResponse,
    IncidentTechniqueMappingResponse,
    IncidentTimelineEventCreate,
    IncidentTimelineEventResponse,
    IncidentUpdate,
    ResponseActionPropose,
    ResponseActionResponse,
    TechniqueMappingRequest,
)
from app.services.incident_response.evidence_service import EvidenceService
from app.services.incident_response.incident_service import IncidentService
from app.services.incident_response.mitre_service import MitreService
from app.services.incident_response.playbook_service import PlaybookService
from app.services.incident_response.report_service import ReportService
from app.services.incident_response.response_simulation_service import (
    ResponseSimulationService,
)
from app.services.incident_response.timeline_service import TimelineService

router = APIRouter()
mitre_router = APIRouter()
playbook_router = APIRouter()


# ==============================================================================
# INCIDENT CORE ENDPOINTS
# ==============================================================================


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    db: DbSession,
    status: str | None = Query(None, description="Filter by IncidentStatus"),
    severity: str | None = Query(None, description="Filter by IncidentSeverity"),
    classification: str | None = Query(None, description="Filter by IncidentClassification"),
    incident_type: str | None = Query(None, description="Filter by IncidentType"),
    search: str | None = Query(None, description="Search in title, description, analyst"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> IncidentListResponse:
    """List educational incidents with filtering and pagination."""
    items, total = IncidentService.list_incidents(
        db=db,
        status=status,
        severity=severity,
        classification=classification,
        incident_type=incident_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return IncidentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/metrics", response_model=dict[str, Any])
def get_incident_metrics(db: DbSession) -> dict[str, Any]:
    """Retrieve platform-wide educational incident metrics and triage breakdowns."""
    return IncidentService.get_metrics(db)


@router.post("", response_model=IncidentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Create a new educational incident ticket."""
    incident = IncidentService.create_incident(
        db=db,
        title=data.title,
        description=data.description,
        incident_type=data.incident_type,
        severity=data.severity,
        priority=data.priority,
        playbook_id=data.playbook_id,
        case_id=data.case_id,
        created_by_id=current_user.id if current_user else None,
        lead_analyst=data.lead_analyst,
        detected_at=data.detected_at,
    )
    return IncidentService.get_incident(db, incident.id)


@router.post("/escalate-alert", response_model=IncidentDetailResponse, status_code=status.HTTP_201_CREATED)
def escalate_alert_to_incident(
    data: EscalateAlertRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Escalate a Detection Alert directly into an educational Incident."""
    try:
        incident = IncidentService.escalate_alert_to_incident(
            db=db,
            alert_id=data.alert_id,
            title=data.title,
            severity=data.severity,
            playbook_id=data.playbook_id,
            user_id=current_user.id if current_user else None,
        )
        return IncidentService.get_incident(db, incident.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(
    incident_id: str,
    db: DbSession,
) -> Any:
    """Get complete details for an incident including evidence, timeline, hypotheses, and actions."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )
    return incident


@router.patch("/{incident_id}", response_model=IncidentDetailResponse)
def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Update incident status, phase, classification, analysis notes, or lessons learned."""
    updates = data.model_dump(exclude_unset=True)
    incident = IncidentService.update_incident(
        db=db,
        incident_id_or_int=incident_id,
        updates=updates,
        user_id=current_user.id if current_user else None,
    )
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )
    return IncidentService.get_incident(db, incident.id)


@router.post("/{incident_id}/notes", response_model=IncidentNoteResponse, status_code=status.HTTP_201_CREATED)
def add_incident_note(
    incident_id: str,
    data: IncidentNoteCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Add an analyst work log entry to an incident."""
    try:
        return IncidentService.add_note(
            db=db,
            incident_id_or_int=incident_id,
            note_text=data.note,
            user_id=current_user.id if current_user else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/report", response_model=dict[str, Any])
def get_incident_report(
    incident_id: str,
    db: DbSession,
) -> dict[str, Any]:
    """Generate a NIST SP 800-61 post-incident executive report with Markdown and structured JSON."""
    try:
        return ReportService.generate_incident_report(db, incident_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==============================================================================
# EVIDENCE & CHAIN OF CUSTODY ENDPOINTS
# ==============================================================================


@router.get("/{incident_id}/evidence", response_model=list[IncidentEvidenceResponse])
def list_incident_evidence(
    incident_id: str,
    db: DbSession,
    evidence_type: str | None = Query(None),
    source_engine: str | None = Query(None),
) -> Any:
    """List cross-engine evidence items collected for an incident."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return EvidenceService.list_evidence(db, incident.id, evidence_type, source_engine)


@router.post("/{incident_id}/evidence", response_model=IncidentEvidenceResponse, status_code=status.HTTP_201_CREATED)
def add_incident_evidence(
    incident_id: str,
    data: IncidentEvidenceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Attach a new evidence artifact from SIEM, Endpoint, Threat Intel, or PCAP."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    return EvidenceService.add_evidence(
        db=db,
        incident_id=incident.id,
        title=data.title,
        description=data.description,
        evidence_type=data.evidence_type,
        source_engine=data.source_engine,
        source_id=data.source_id,
        source_ref=data.source_ref,
        data_payload=data.data_payload,
        relevance=data.relevance,
        user_id=current_user.id if current_user else None,
    )


@router.get("/{incident_id}/evidence/{evidence_id}", response_model=IncidentEvidenceResponse)
def get_evidence_detail(
    incident_id: str,
    evidence_id: str,
    db: DbSession,
) -> Any:
    """Get full evidence details including full chain of custody audit logs."""
    evidence = EvidenceService.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evidence '{evidence_id}' not found")
    return evidence


@router.post("/{incident_id}/evidence/{evidence_id}/verify-hash", response_model=dict[str, Any])
def verify_evidence_integrity(
    incident_id: str,
    evidence_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Verify cryptographic SHA-256 integrity hash of evidence and log chain of custody touch."""
    evidence = EvidenceService.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evidence '{evidence_id}' not found")
    return EvidenceService.verify_evidence_hash(db, evidence.id, user_id=current_user.id if current_user else None)


@router.patch("/{incident_id}/evidence/{evidence_id}", response_model=IncidentEvidenceResponse)
def update_evidence(
    incident_id: str,
    evidence_id: str,
    data: IncidentEvidenceUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Update evidence relevance rating (Supporting / Contradicting / Context) or containment status."""
    evidence = EvidenceService.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evidence '{evidence_id}' not found")

    updates = data.model_dump(exclude_unset=True)
    updated = EvidenceService.update_evidence(db, evidence.id, updates, user_id=current_user.id if current_user else None)
    return updated


# ==============================================================================
# TIMELINE ENDPOINTS
# ==============================================================================


@router.get("/{incident_id}/timeline", response_model=list[IncidentTimelineEventResponse])
def list_timeline_events(
    incident_id: str,
    db: DbSession,
    category: str | None = Query(None),
    is_milestone: bool | None = Query(None),
) -> Any:
    """Retrieve chronological event timeline for the incident."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return TimelineService.list_events(db, incident.id, category, is_milestone)


@router.post("/{incident_id}/timeline", response_model=IncidentTimelineEventResponse, status_code=status.HTTP_201_CREATED)
def add_timeline_event(
    incident_id: str,
    data: IncidentTimelineEventCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Add a manual event or milestone to the incident timeline."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    return TimelineService.add_event(
        db=db,
        incident_id=incident.id,
        timestamp=data.timestamp,
        title=data.title,
        description=data.description,
        event_category=data.event_category,
        source=data.source,
        source_id=data.source_id,
        mitre_technique_id=data.mitre_technique_id,
        is_milestone=data.is_milestone,
        user_id=current_user.id if current_user else None,
    )


@router.post("/{incident_id}/timeline/sync", response_model=dict[str, Any])
def sync_timeline_sources(
    incident_id: str,
    db: DbSession,
) -> dict[str, Any]:
    """Auto-sync timeline events from executed response actions and linked evidence."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    added = TimelineService.sync_timeline_from_sources(db, incident.id)
    return {"incident_id": incident.incident_id, "events_synced": added}


# ==============================================================================
# HYPOTHESES & FINDINGS ENDPOINTS
# ==============================================================================


@router.post("/{incident_id}/hypotheses", response_model=IncidentHypothesisResponse, status_code=status.HTTP_201_CREATED)
def create_hypothesis(
    incident_id: str,
    data: IncidentHypothesisCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Formulate an investigative hypothesis to test against collected evidence."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    hyp_count = len(incident.hypotheses) + 1
    hyp = IncidentHypothesis(
        hypothesis_id=f"HYP-{incident.incident_id[-4:]}-{hyp_count:02d}",
        incident_id=incident.id,
        statement=data.statement,
        status="PROPOSED",
        confidence=data.confidence,
        rationale=data.rationale,
        created_by_id=current_user.id if current_user else None,
    )
    db.add(hyp)
    db.commit()
    db.refresh(hyp)
    return hyp


@router.patch("/{incident_id}/hypotheses/{hypothesis_id}", response_model=IncidentHypothesisResponse)
def update_hypothesis(
    incident_id: str,
    hypothesis_id: str,
    data: IncidentHypothesisUpdate,
    db: DbSession,
) -> Any:
    """Update testing status (SUPPORTED / NOT_SUPPORTED / INCONCLUSIVE) of an investigative hypothesis."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    hyp = next((h for h in incident.hypotheses if h.hypothesis_id == hypothesis_id or str(h.id) == hypothesis_id), None)
    if not hyp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hypothesis '{hypothesis_id}' not found")

    hyp.status = data.status
    if data.confidence:
        hyp.confidence = data.confidence
    if data.rationale:
        hyp.rationale = data.rationale

    db.commit()
    db.refresh(hyp)
    return hyp


@router.post("/{incident_id}/findings", response_model=IncidentFindingResponse, status_code=status.HTTP_201_CREATED)
def record_finding(
    incident_id: str,
    data: IncidentFindingCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Record a validated factual finding from confirmed evidence."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    find_count = len(incident.findings) + 1
    finding = IncidentFinding(
        finding_id=f"FND-{incident.incident_id[-4:]}-{find_count:02d}",
        incident_id=incident.id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        confidence=data.confidence,
        affected_systems=data.affected_systems,
        affected_accounts=data.affected_accounts,
        indicators_observed=data.indicators_observed,
        mitre_technique=data.mitre_technique,
        mitre_tactic=data.mitre_tactic,
        created_by_id=current_user.id if current_user else None,
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


# ==============================================================================
# RESPONSE ACTIONS (SIMULATION-ONLY) ENDPOINTS
# ==============================================================================


@router.get("/{incident_id}/actions", response_model=list[ResponseActionResponse])
def list_response_actions(
    incident_id: str,
    db: DbSession,
    category: str | None = Query(None),
    status: str | None = Query(None),
) -> Any:
    """List proposed and executed simulated response actions."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")
    return ResponseSimulationService.list_actions(db, incident.id, category, status)


@router.post("/{incident_id}/actions", response_model=ResponseActionResponse, status_code=status.HTTP_201_CREATED)
def propose_response_action(
    incident_id: str,
    data: ResponseActionPropose,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Propose a defensive response action (containment, eradication, recovery). Strictly simulation-only."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    return ResponseSimulationService.propose_action(
        db=db,
        incident_id=incident.id,
        category=data.category,
        action_type=data.action_type,
        target_type=data.target_type,
        target_identifier=data.target_identifier,
        reason=data.reason,
        risk_assessment=data.risk_assessment,
        expected_impact=data.expected_impact,
        user_id=current_user.id if current_user else None,
    )


@router.post("/{incident_id}/actions/{action_id}/execute", response_model=ResponseActionResponse)
def execute_simulated_action(
    incident_id: str,
    action_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Execute a defensive action in synthetic simulation. Strictly safe; never touches real hosts."""
    try:
        return ResponseSimulationService.execute_action(
            db=db,
            action_id_or_int=action_id,
            user_id=current_user.id if current_user else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{incident_id}/actions/{action_id}/revert", response_model=ResponseActionResponse)
def revert_simulated_action(
    incident_id: str,
    action_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Revert a previously executed response action in simulation."""
    try:
        return ResponseSimulationService.revert_action(
            db=db,
            action_id_or_int=action_id,
            user_id=current_user.id if current_user else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==============================================================================
# MITRE ATT&CK MAPPING ENDPOINTS (on incident router)
# ==============================================================================


@router.post("/{incident_id}/mitre/map", response_model=IncidentTechniqueMappingResponse, status_code=status.HTTP_201_CREATED)
def map_technique_to_incident(
    incident_id: str,
    data: TechniqueMappingRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Map a MITRE ATT&CK technique to an incident with analytical confidence and evidence summary."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    try:
        mapping = MitreService.map_technique_to_incident(
            db=db,
            incident_id=incident.id,
            technique_id_or_code=data.technique_id_or_code,
            mapping_confidence=data.mapping_confidence,
            evidence_summary=data.evidence_summary,
            phase=data.phase,
            user_id=current_user.id if current_user else None,
        )
        return mapping
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{incident_id}/mitre/map/{technique_id}", status_code=status.HTTP_204_NO_CONTENT)
def unmap_technique_from_incident(
    incident_id: str,
    technique_id: str,
    db: DbSession,
) -> None:
    """Remove a MITRE ATT&CK technique mapping from an incident."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    removed = MitreService.unmap_technique(db, incident.id, technique_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Technique mapping '{technique_id}' not found")


# ==============================================================================
# PLAYBOOK ATTACHMENT ENDPOINT (on incident router)
# ==============================================================================


@router.post("/{incident_id}/playbooks/attach", response_model=IncidentDetailResponse)
def attach_playbook_to_incident(
    incident_id: str,
    playbook_id: str = Query(..., description="Playbook ID or numeric ID"),
    db: DbSession = None,
) -> Any:
    """Attach a standardized IR Playbook to guide response workflow for an incident."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    try:
        PlaybookService.attach_playbook(db, incident.id, playbook_id)
        return IncidentService.get_incident(db, incident.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==============================================================================
# MITRE ATT&CK CATALOG ROUTER (/api/v1/mitre)
# ==============================================================================


@mitre_router.get("/tactics", response_model=list[AttackTacticResponse])
def list_mitre_tactics(db: DbSession) -> Any:
    """List all 14 MITRE ATT&CK Enterprise Tactics with their techniques."""
    return MitreService.list_tactics(db)


@mitre_router.get("/techniques", response_model=list[AttackTechniqueResponse])
def list_mitre_techniques(
    db: DbSession,
    tactic_id: str | None = Query(None, description="Filter by tactic (e.g. TA0001)"),
    search: str | None = Query(None, description="Search technique ID, name, description"),
) -> Any:
    """Search and browse MITRE ATT&CK Enterprise techniques."""
    return MitreService.list_techniques(db, tactic_id=tactic_id, search=search)


@mitre_router.get("/techniques/{technique_id}", response_model=AttackTechniqueResponse)
def get_mitre_technique(
    technique_id: str,
    db: DbSession,
) -> Any:
    """Get full details for a MITRE ATT&CK technique including detection and mitigation guidance."""
    tech = MitreService.get_technique(db, technique_id)
    if not tech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Technique '{technique_id}' not found")
    return tech


@mitre_router.get("/coverage", response_model=dict[str, Any])
def get_mitre_matrix_coverage(
    db: DbSession,
    incident_id: int | None = Query(None, description="Optional incident ID for specific heat map"),
) -> dict[str, Any]:
    """Calculate interactive MITRE ATT&CK matrix coverage and heat map counts."""
    return MitreService.get_matrix_coverage(db, incident_id=incident_id)


# ==============================================================================
# PLAYBOOKS ROUTER (/api/v1/playbooks)
# ==============================================================================


@playbook_router.get("", response_model=list[IncidentPlaybookResponse])
def list_playbooks(
    db: DbSession,
    category: str | None = Query(None, description="Filter by playbook category (e.g. MALWARE, CREDENTIALS)"),
    search: str | None = Query(None, description="Search in playbook title or description"),
) -> Any:
    """List all standardized Incident Response Playbooks."""
    return PlaybookService.list_playbooks(db, category=category, search=search)


@playbook_router.get("/{playbook_id}", response_model=IncidentPlaybookResponse)
def get_playbook(
    playbook_id: str,
    db: DbSession,
) -> Any:
    """Get full details for a playbook including NIST SP 800-61 phase steps and checklists."""
    pb = PlaybookService.get_playbook(db, playbook_id)
    if not pb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playbook '{playbook_id}' not found")
    return pb
