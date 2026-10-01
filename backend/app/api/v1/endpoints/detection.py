"""API endpoints for Step 11 Network Detection Engine.

Provides rule management, offline detection runs, alert triage, evidence inspection,
and SOC analyst notes and status tracking.
"""

import json

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc

from app.api.deps import CurrentUser, DbSession
from app.models.detection import DetectionRule, DetectionRun
from app.schemas.common import ModuleStatusResponse
from app.schemas.detection import (
    AlertNoteCreate,
    AlertNoteResponse,
    AlertStatusUpdateRequest,
    DetectionAlertDetail,
    DetectionAlertListItem,
    DetectionRuleCreate,
    DetectionRuleResponse,
    DetectionRuleTestRequest,
    DetectionRuleTestResponse,
    DetectionRuleUpdate,
    DetectionRunCreate,
    DetectionRunResponse,
    DetectionStatsResponse,
)
from app.services.detection.alert_service import AlertService
from app.services.detection.detection_run_service import DetectionRunService

router = APIRouter()
alert_service = AlertService()
run_service = DetectionRunService()


# ============================================================================
# Status & Overview
# ============================================================================


@router.get("", response_model=ModuleStatusResponse)
@router.get("/", response_model=ModuleStatusResponse, include_in_schema=False)
@router.get("/status", response_model=ModuleStatusResponse)
async def get_detection_module_status() -> ModuleStatusResponse:
    """Return status and educational capabilities of the Step 11 Detection Engine."""
    return ModuleStatusResponse(
        module="detection",
        status="planned",
        description="Deterministic educational network detection engine analyzing offline captures and simulator sessions.",
        planned_phase="Phase 4",
        capabilities=[
            "Deterministic multi-protocol rule evaluation (TCP, UDP, DNS, ARP, ICMP, HTTP)",
            "Offline PCAP and simulation telemetry feature extraction",
            "Explainable alert generation with neutral educational language",
            "Granular packet evidence linking and protocol layer inspection",
            "Analyst triage workflows (NEW -> ACKNOWLEDGED -> INVESTIGATING -> CLOSED)",
            "MITRE ATT&CK educational technique correlation",
        ],
    )


@router.get("/stats", response_model=DetectionStatsResponse)
def get_detection_stats(db: DbSession) -> DetectionStatsResponse:
    """Retrieve macro operational metrics for detection dashboard."""
    return alert_service.get_detection_statistics(db)


# ============================================================================
# Detection Rules
# ============================================================================


@router.get("/rules", response_model=list[DetectionRuleResponse])
def list_detection_rules(
    db: DbSession,
    category: str | None = Query(None, description="Filter by RuleCategory"),
    severity: str | None = Query(None, description="Filter by AlertSeverity"),
    status_filter: str | None = Query(None, alias="status", description="Filter by RuleStatus"),
    is_builtin: bool | None = Query(None, description="Filter by built-in vs custom"),
    search: str | None = Query(None, description="Search by name, ID, or description"),
) -> list[DetectionRuleResponse]:
    """List detection rules matching query filters."""
    query = db.query(DetectionRule)

    if category:
        query = query.filter(DetectionRule.category == category)
    if severity:
        query = query.filter(DetectionRule.severity == severity)
    if status_filter:
        query = query.filter(DetectionRule.status == status_filter)
    if is_builtin is not None:
        query = query.filter(DetectionRule.is_builtin == is_builtin)
    if search:
        search_pat = f"%{search}%"
        query = query.filter(
            (DetectionRule.name.ilike(search_pat))
            | (DetectionRule.rule_id.ilike(search_pat))
            | (DetectionRule.description.ilike(search_pat))
        )

    rules = query.order_by(DetectionRule.rule_id.asc()).all()
    return [DetectionRuleResponse.model_validate(r) for r in rules]


@router.post("/rules", response_model=DetectionRuleResponse, status_code=status.HTTP_201_CREATED)
def create_detection_rule(
    rule_in: DetectionRuleCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> DetectionRuleResponse:
    """Create a new custom detection rule."""
    existing = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_in.rule_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Detection rule code '{rule_in.rule_id}' already exists.",
        )

    conditions_json = (
        json.dumps(rule_in.conditions)
        if isinstance(rule_in.conditions, dict)
        else str(rule_in.conditions)
    )

    new_rule = DetectionRule(
        rule_id=rule_in.rule_id,
        name=rule_in.name,
        description=rule_in.description,
        category=str(rule_in.category),
        severity=str(rule_in.severity),
        confidence_default=str(rule_in.confidence_default),
        status=str(rule_in.status),
        logic_type=rule_in.logic_type,
        conditions=conditions_json,
        threshold=rule_in.threshold,
        time_window_seconds=rule_in.time_window_seconds,
        mitre_attack_id=rule_in.mitre_attack_id,
        mitre_technique=rule_in.mitre_technique,
        explanation_template=rule_in.explanation_template,
        investigation_guide=rule_in.investigation_guide,
        is_builtin=False,
        author_id=current_user.id,
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return DetectionRuleResponse.model_validate(new_rule)


@router.get("/rules/{rule_identifier}", response_model=DetectionRuleResponse)
def get_detection_rule(rule_identifier: str, db: DbSession) -> DetectionRuleResponse:
    """Get a detection rule by database ID or rule code (e.g. 'NET-TCP-001')."""
    if rule_identifier.isdigit():
        rule = db.query(DetectionRule).filter(DetectionRule.id == int(rule_identifier)).first()
    else:
        rule = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_identifier).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection rule '{rule_identifier}' not found.",
        )
    return DetectionRuleResponse.model_validate(rule)


@router.patch("/rules/{rule_identifier}", response_model=DetectionRuleResponse)
def update_detection_rule(
    rule_identifier: str,
    update_in: DetectionRuleUpdate,
    db: DbSession,
) -> DetectionRuleResponse:
    """Update properties of an existing detection rule."""
    if rule_identifier.isdigit():
        rule = db.query(DetectionRule).filter(DetectionRule.id == int(rule_identifier)).first()
    else:
        rule = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_identifier).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection rule '{rule_identifier}' not found.",
        )

    update_dict = update_in.model_dump(exclude_unset=True)
    for field_name, value in update_dict.items():
        if field_name == "conditions" and isinstance(value, dict):
            rule.conditions = json.dumps(value)
        elif value is not None:
            setattr(rule, field_name, str(value) if hasattr(value, "value") else value)

    db.commit()
    db.refresh(rule)
    return DetectionRuleResponse.model_validate(rule)


@router.post("/rules/test", response_model=DetectionRuleTestResponse)
def test_detection_rule(
    req: DetectionRuleTestRequest,
    db: DbSession,
) -> DetectionRuleTestResponse:
    """Test a detection rule against a capture without persisting alerts."""
    result = run_service.test_rule(
        db=db,
        rule_id=req.rule_id,
        conditions=req.conditions,
        threshold=req.threshold,
        time_window_seconds=req.time_window_seconds,
        capture_id=req.capture_id,
    )
    return DetectionRuleTestResponse(**result)


# ============================================================================
# Detection Runs
# ============================================================================


@router.post("/runs", response_model=DetectionRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_detection_run(
    req: DetectionRunCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> DetectionRunResponse:
    """Trigger a deterministic detection run over a PCAP or simulation session."""
    run = run_service.create_and_execute_run(
        db=db,
        source_type=req.source_type,
        capture_id=req.capture_id,
        simulation_scenario_id=req.simulation_scenario_id,
        user_id=current_user.id,
        rule_ids=req.rule_ids,
    )
    return DetectionRunResponse.model_validate(run)


@router.get("/runs", response_model=list[DetectionRunResponse])
def list_detection_runs(
    db: DbSession,
    capture_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[DetectionRunResponse]:
    """List execution history of detection runs."""
    query = db.query(DetectionRun)
    if capture_id:
        query = query.filter(DetectionRun.capture_id == capture_id)

    runs = query.order_by(desc(DetectionRun.created_at)).offset(skip).limit(limit).all()
    return [DetectionRunResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=DetectionRunResponse)
def get_detection_run(run_id: int, db: DbSession) -> DetectionRunResponse:
    """Retrieve details and execution summary of a specific detection run."""
    run = db.query(DetectionRun).filter(DetectionRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection run {run_id} not found.",
        )
    return DetectionRunResponse.model_validate(run)


# ============================================================================
# Detection Alerts
# ============================================================================


@router.get("/alerts", response_model=list[DetectionAlertListItem])
def list_detection_alerts(
    db: DbSession,
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    category: str | None = Query(None),
    capture_id: int | None = Query(None),
    run_id: int | None = Query(None),
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[DetectionAlertListItem]:
    """List detection alerts with multi-criteria filtering."""
    alerts, _ = alert_service.get_alerts(
        db=db,
        status=status_filter,
        severity=severity,
        category=category,
        capture_id=capture_id,
        run_id=run_id,
        search=search,
        skip=skip,
        limit=limit,
    )
    return [
        DetectionAlertListItem(
            id=a.id,
            run_id=a.run_id,
            rule_id=a.rule_id,
            rule_code=a.rule.rule_id if a.rule else None,
            title=a.title,
            category=a.category,
            severity=a.severity,
            confidence=a.confidence,
            status=a.status,
            source_ip=a.source_ip,
            source_port=a.source_port,
            destination_ip=a.destination_ip,
            destination_port=a.destination_port,
            protocol=a.protocol,
            first_seen_timestamp=a.first_seen_timestamp,
            last_seen_timestamp=a.last_seen_timestamp,
            packet_count=a.packet_count,
            created_at=a.created_at,
        )
        for a in alerts
    ]


@router.get("/alerts/{alert_id}", response_model=DetectionAlertDetail)
def get_detection_alert_detail(alert_id: int, db: DbSession) -> DetectionAlertDetail:
    """Retrieve full alert details including linked evidence, analyst notes, and audit history."""
    alert = alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection alert {alert_id} not found.",
        )

    # Format notes with author names
    notes_formatted = []
    for n in alert.notes:
        notes_formatted.append(
            AlertNoteResponse(
                id=n.id,
                alert_id=n.alert_id,
                user_id=n.user_id,
                author_name=n.user.username if n.user else "Analyst",
                note=n.note,
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
        )

    return DetectionAlertDetail(
        id=alert.id,
        run_id=alert.run_id,
        rule_id=alert.rule_id,
        rule_code=alert.rule.rule_id if alert.rule else None,
        title=alert.title,
        category=alert.category,
        severity=alert.severity,
        confidence=alert.confidence,
        status=alert.status,
        source_ip=alert.source_ip,
        source_port=alert.source_port,
        destination_ip=alert.destination_ip,
        destination_port=alert.destination_port,
        protocol=alert.protocol,
        first_seen_timestamp=alert.first_seen_timestamp,
        last_seen_timestamp=alert.last_seen_timestamp,
        packet_count=alert.packet_count,
        created_at=alert.created_at,
        explanation=alert.explanation,
        mitre_attack_id=alert.mitre_attack_id,
        mitre_technique=alert.mitre_technique,
        investigation_steps=alert.investigation_steps,
        evidence=alert.evidence,
        notes=notes_formatted,
        status_history=alert.status_history,
    )


@router.patch("/alerts/{alert_id}/status", response_model=DetectionAlertDetail)
def update_alert_status(
    alert_id: int,
    req: AlertStatusUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> DetectionAlertDetail:
    """Update alert investigation workflow state (NEW, ACKNOWLEDGED, INVESTIGATING, CLOSED, FALSE_POSITIVE)."""
    alert = alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection alert {alert_id} not found.",
        )

    alert_service.update_alert_status(
        db=db,
        alert=alert,
        new_status=str(req.status),
        reason=req.reason,
        user_id=current_user.id,
    )
    return get_detection_alert_detail(alert_id, db)


@router.post("/alerts/{alert_id}/notes", response_model=AlertNoteResponse, status_code=status.HTTP_201_CREATED)
def add_alert_analyst_note(
    alert_id: int,
    req: AlertNoteCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> AlertNoteResponse:
    """Append analyst findings or observations to an alert."""
    alert = alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection alert {alert_id} not found.",
        )

    note = alert_service.add_alert_note(
        db=db,
        alert=alert,
        note_text=req.note,
        user_id=current_user.id,
    )
    return AlertNoteResponse(
        id=note.id,
        alert_id=note.alert_id,
        user_id=note.user_id,
        author_name=current_user.username,
        note=note.note,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )
