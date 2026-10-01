"""SIEM & Security Log Analysis Engine API Endpoints for NexoraNet Step 15."""

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.models.enums import LogCorrelationRuleStatus
from app.models.siem import (
    CorrelationAlert,
    LogCorrelationRule,
    LogSource,
    RawLogEvent,
    SecurityEvent,
    SecurityLogDataset,
    SIEMLabScenario,
)
from app.schemas.siem import (
    CorrelationAlertResponse,
    DatasetImportRequest,
    InvestigateInSocRequest,
    LogCorrelationRuleCreate,
    LogCorrelationRuleResponse,
    LogCorrelationRuleUpdate,
    LogSourceResponse,
    SavedSearchCreate,
    SavedSearchResponse,
    SavedSearchUpdate,
    SearchHistoryResponse,
    SecurityEventDetailResponse,
    SecurityEventResponse,
    SecurityLogDatasetResponse,
    SiemAggregateRequest,
    SiemAggregateResponse,
    SIEMLabScenarioResponse,
    SIEMLabValidateRequest,
    SIEMLabValidateResponse,
    SiemSearchRequest,
    SiemSearchResponse,
    StartHuntFromSiemRequest,
)
from app.services.siem.aggregation_service import SiemAggregationService
from app.services.siem.correlation_engine import SiemCorrelationEngine
from app.services.siem.dataset_service import SiemDatasetService
from app.services.siem.ingestion_service import LogIngestionService
from app.services.siem.integration_service import SiemIntegrationService
from app.services.siem.search_service import SiemSearchService

router = APIRouter()


# ---------------------------------------------------------------------------
# Overview & Aggregations
# ---------------------------------------------------------------------------
@router.get("/overview", response_model=SiemAggregateResponse)
def get_siem_overview(
    db: DbSession,
    dataset_id: int | None = Query(None, description="Optional dataset ID filter"),
    time_preset: str | None = Query(None, description="Time window preset (e.g. 15m, 1h, 24h, dataset)"),
) -> Any:
    """Fetch top-level SIEM dashboard KPIs, severity distribution, top entities, and time-series histogram."""
    return SiemAggregationService.get_dashboard_metrics(db, dataset_id=dataset_id, time_preset=time_preset)


@router.post("/aggregate", response_model=SiemAggregateResponse)
def post_siem_aggregate(
    payload: SiemAggregateRequest,
    db: DbSession,
) -> Any:
    """Compute bounded statistical summaries and time series histograms."""
    return SiemAggregationService.get_dashboard_metrics(
        db, dataset_id=payload.dataset_id, time_preset=payload.time_preset
    )


# ---------------------------------------------------------------------------
# Log Sources
# ---------------------------------------------------------------------------
@router.get("/sources", response_model=list[LogSourceResponse])
def list_log_sources(
    db: DbSession,
) -> Any:
    """List all registered educational log sources."""
    sources = db.execute(select(LogSource).order_by(LogSource.id.asc())).scalars().all()
    if not sources:
        SiemDatasetService.seed_all_siem_data(db)
        sources = db.execute(select(LogSource).order_by(LogSource.id.asc())).scalars().all()
    return sources


@router.get("/sources/{source_id}", response_model=LogSourceResponse)
def get_log_source(
    source_id: int,
    db: DbSession,
) -> Any:
    """Fetch details of a specific log source."""
    src = db.execute(select(LogSource).where(LogSource.id == source_id)).scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="Log source not found.")
    return src


# ---------------------------------------------------------------------------
# Datasets & Ingestion
# ---------------------------------------------------------------------------
@router.get("/datasets", response_model=list[SecurityLogDatasetResponse])
def list_datasets(
    db: DbSession,
) -> Any:
    """List available synthetic security log datasets."""
    datasets = db.execute(select(SecurityLogDataset).order_by(SecurityLogDataset.id.asc())).scalars().all()
    if not datasets:
        SiemDatasetService.seed_all_siem_data(db)
        datasets = db.execute(select(SecurityLogDataset).order_by(SecurityLogDataset.id.asc())).scalars().all()
    return datasets


@router.get("/datasets/{dataset_id}", response_model=SecurityLogDatasetResponse)
def get_dataset(
    dataset_id: int,
    db: DbSession,
) -> Any:
    """Fetch a specific security log dataset by ID."""
    ds = db.execute(select(SecurityLogDataset).where(SecurityLogDataset.id == dataset_id)).scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return ds


@router.get("/datasets/{dataset_id}/events", response_model=SiemSearchResponse)
def get_dataset_events(
    dataset_id: int,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("timestamp"),
    sort_asc: bool = Query(False),
) -> Any:
    """List normalized events belonging to a dataset."""
    return SiemSearchService.execute_search(
        db=db,
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_asc=sort_asc,
    )


@router.post("/datasets/import", status_code=status.HTTP_201_CREATED)
def import_logs_to_dataset(
    payload: DatasetImportRequest,
    db: DbSession,
) -> Any:
    """Safely ingest raw JSON, CSV, or Syslog records into a dataset."""
    try:
        result = LogIngestionService.ingest_payload(
            db=db,
            dataset_id=payload.dataset_id,
            content=payload.content,
            format_hint=payload.format,
            source_id=payload.source_id,
        )
        return {"status": "SUCCESS", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Search & Query Engine
# ---------------------------------------------------------------------------
@router.post("/search", response_model=SiemSearchResponse)
def execute_siem_search(
    payload: SiemSearchRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Execute search query with visual conditions, full-text search, and time-range filtering."""
    cond_dicts = [c.model_dump() for c in payload.conditions] if payload.conditions else None
    not_cond_dicts = [c.model_dump() for c in payload.not_conditions] if payload.not_conditions else None

    return SiemSearchService.execute_search(
        db=db,
        dataset_id=payload.dataset_id,
        conditions=cond_dicts,
        logical_op=payload.logical_op,
        not_conditions=not_cond_dicts,
        search_text=payload.search_text,
        time_preset=payload.time_preset,
        start_time=payload.start_time,
        end_time=payload.end_time,
        quick_filter=payload.quick_filter,
        limit=payload.limit,
        offset=payload.offset,
        sort_by=payload.sort_by,
        sort_asc=payload.sort_asc,
        user_id=current_user.id,
    )


@router.get("/search/history", response_model=list[SearchHistoryResponse])
def get_search_history(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=50),
) -> Any:
    """Fetch search execution history for current user."""
    return SiemSearchService.get_search_history(db=db, user_id=current_user.id, limit=limit)


@router.post("/search/saved", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
def create_saved_search(
    payload: SavedSearchCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Save a search query definition for quick access."""
    return SiemSearchService.create_saved_search(
        db=db,
        name=payload.name,
        query_def=payload.query_definition,
        description=payload.description,
        owner_id=current_user.id,
        is_public=payload.is_public,
    )


@router.get("/search/saved", response_model=list[SavedSearchResponse])
def list_saved_searches(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """List accessible saved searches."""
    return SiemSearchService.list_saved_searches(db=db, user_id=current_user.id, limit=limit)


@router.patch("/search/saved/{saved_id}", response_model=SavedSearchResponse)
def update_saved_search(
    saved_id: int,
    payload: SavedSearchUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Update a saved search owned by the user."""
    try:
        return SiemSearchService.update_saved_search(
            db=db,
            search_id=saved_id,
            user_id=current_user.id,
            name=payload.name,
            description=payload.description,
            query_def=payload.query_definition,
            is_public=payload.is_public,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.delete("/search/saved/{saved_id}")
def delete_saved_search(
    saved_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Delete a saved search."""
    try:
        success = SiemSearchService.delete_saved_search(db=db, search_id=saved_id, user_id=current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Saved search not found.")
        return {"status": "SUCCESS", "deleted_id": saved_id}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Event Details & Related Telemetry
# ---------------------------------------------------------------------------
@router.get("/events/{event_id}", response_model=SecurityEventDetailResponse)
def get_event_detail(
    event_id: str,
    db: DbSession,
) -> Any:
    """Get complete normalized event details and raw log message."""
    ev = db.execute(select(SecurityEvent).where(SecurityEvent.event_id == event_id)).scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Security event not found.")

    raw_msg = None
    if ev.raw_event_id:
        raw_obj = db.execute(select(RawLogEvent).where(RawLogEvent.id == ev.raw_event_id)).scalar_one_or_none()
        if raw_obj:
            raw_msg = raw_obj.raw_message

    res = SecurityEventDetailResponse.model_validate(ev)
    res.raw_message = raw_msg
    return res


@router.get("/events/{event_id}/related", response_model=list[SecurityEventResponse])
def get_related_events(
    event_id: str,
    db: DbSession,
    limit: int = Query(20, ge=1, le=50),
) -> Any:
    """Find related events sharing source IP, destination IP, host, or user."""
    ev = db.execute(select(SecurityEvent).where(SecurityEvent.event_id == event_id)).scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Security event not found.")

    match_clauses = []
    if ev.source_ip:
        match_clauses.append(SecurityEvent.source_ip == ev.source_ip)
    if ev.destination_ip:
        match_clauses.append(SecurityEvent.destination_ip == ev.destination_ip)
    if ev.host:
        match_clauses.append(SecurityEvent.host == ev.host)
    if ev.username:
        match_clauses.append(SecurityEvent.username == ev.username)

    if not match_clauses:
        return []

    stmt = (
        select(SecurityEvent)
        .where(SecurityEvent.id != ev.id)
        .where(or_(*match_clauses))
        .order_by(SecurityEvent.timestamp.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


# ---------------------------------------------------------------------------
# Correlation Rules & Alerts
# ---------------------------------------------------------------------------
@router.get("/rules", response_model=list[LogCorrelationRuleResponse])
def list_correlation_rules(
    db: DbSession,
) -> Any:
    """List all correlation rules."""
    rules = db.execute(select(LogCorrelationRule).order_by(LogCorrelationRule.id.asc())).scalars().all()
    if not rules:
        rules = SiemCorrelationEngine.seed_default_rules(db)
    return rules


@router.post("/rules", response_model=LogCorrelationRuleResponse, status_code=status.HTTP_201_CREATED)
def create_correlation_rule(
    payload: LogCorrelationRuleCreate,
    db: DbSession,
) -> Any:
    """Create a new custom correlation rule."""
    existing = db.execute(
        select(LogCorrelationRule).where(LogCorrelationRule.stable_id == payload.stable_id)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Rule with this stable_id already exists.")

    rule = LogCorrelationRule(
        stable_id=payload.stable_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        severity=payload.severity,
        confidence=payload.confidence,
        status=LogCorrelationRuleStatus.ENABLED.value,
        version="1.0.0",
        logic=payload.logic,
        time_window_seconds=payload.time_window_seconds,
        explanation=payload.explanation,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/rules/{rule_id}", response_model=LogCorrelationRuleResponse)
def update_correlation_rule(
    rule_id: int,
    payload: LogCorrelationRuleUpdate,
    db: DbSession,
) -> Any:
    """Update correlation rule properties or toggle status."""
    rule = db.execute(select(LogCorrelationRule).where(LogCorrelationRule.id == rule_id)).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Correlation rule not found.")

    if payload.name is not None:
        rule.name = payload.name
    if payload.description is not None:
        rule.description = payload.description
    if payload.severity is not None:
        rule.severity = payload.severity
    if payload.confidence is not None:
        rule.confidence = payload.confidence
    if payload.status is not None:
        rule.status = payload.status
    if payload.logic is not None:
        rule.logic = payload.logic
    if payload.time_window_seconds is not None:
        rule.time_window_seconds = payload.time_window_seconds
    if payload.explanation is not None:
        rule.explanation = payload.explanation

    db.commit()
    db.refresh(rule)
    return rule


@router.post("/rules/{rule_id}/test")
def test_correlation_rule(
    rule_id: int,
    db: DbSession,
    dataset_id: int | None = Query(None),
) -> Any:
    """Test a correlation rule against a dataset and return preview of matched alerts."""
    rule = db.execute(select(LogCorrelationRule).where(LogCorrelationRule.id == rule_id)).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Correlation rule not found.")

    alerts = SiemCorrelationEngine._evaluate_rule(db, rule, dataset_id=dataset_id)
    return {
        "rule_id": rule.stable_id,
        "matches_count": len(alerts),
        "alerts_generated": [
            {
                "alert_id": a.alert_id,
                "title": a.title,
                "severity": a.severity,
                "event_count": a.event_count,
                "evidence_summary": a.evidence_summary,
            }
            for a in alerts
        ],
    }


@router.get("/correlations", response_model=list[CorrelationAlertResponse])
def list_correlation_alerts(
    db: DbSession,
    dataset_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Any:
    """List synthesized correlation alerts."""
    stmt = select(CorrelationAlert)
    if dataset_id:
        stmt = stmt.where(CorrelationAlert.dataset_id == dataset_id)
    if status_filter:
        stmt = stmt.where(CorrelationAlert.status == status_filter)

    stmt = stmt.order_by(CorrelationAlert.timestamp.desc()).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


@router.get("/correlations/{alert_id}", response_model=CorrelationAlertResponse)
def get_correlation_alert(
    alert_id: int,
    db: DbSession,
) -> Any:
    """Fetch details of a correlation alert."""
    alert = db.execute(select(CorrelationAlert).where(CorrelationAlert.id == alert_id)).scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Correlation alert not found.")
    return alert


@router.post("/correlations/run")
def trigger_correlation_run(
    db: DbSession,
    dataset_id: int | None = Query(None),
) -> Any:
    """Run all active correlation rules against target dataset(s)."""
    alerts = SiemCorrelationEngine.run_correlation(db, dataset_id=dataset_id)
    return {
        "status": "COMPLETED",
        "alerts_count": len(alerts),
        "alert_ids": [a.alert_id for a in alerts],
    }


# ---------------------------------------------------------------------------
# Cross-Platform Integrations
# ---------------------------------------------------------------------------
@router.post("/events/{event_id}/start-hunt")
def start_threat_hunt_from_event(
    event_id: str,
    payload: StartHuntFromSiemRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Launch a proactive Threat Hunt in Step 14 initialized from a SIEM event."""
    try:
        hunt = SiemIntegrationService.start_threat_hunt(
            db=db,
            event_id=event_id,
            correlation_alert_id=payload.correlation_alert_id,
            user_id=current_user.id,
            hypothesis_statement=payload.hypothesis_statement,
        )
        return {
            "status": "SUCCESS",
            "hunt_id": hunt.id,
            "hunt_code": hunt.hunt_id,
            "title": hunt.title,
            "redirect_url": f"/threat-hunting/hunts/{hunt.id}",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/events/{event_id}/investigate")
def investigate_event_in_soc(
    event_id: str,
    payload: InvestigateInSocRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Escalate a SIEM event or correlation alert into a SOC Investigation in Step 12."""
    try:
        inv = SiemIntegrationService.investigate_in_soc(
            db=db,
            event_id=event_id,
            correlation_alert_id=payload.correlation_alert_id,
            user_id=current_user.id,
        )
        return {
            "status": "SUCCESS",
            "investigation_id": inv.id,
            "investigation_code": inv.investigation_id,
            "title": inv.title,
            "priority": inv.priority,
            "redirect_url": f"/soc/investigations/{inv.id}",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/events/{event_id}/extract-ioc")
def extract_ioc_from_event(
    event_id: str,
    db: DbSession,
) -> Any:
    """Extract candidate IOCs from event and link to Step 13 Threat Intel repository."""
    try:
        iocs = SiemIntegrationService.extract_and_investigate_ioc(db=db, event_id=event_id)
        return {
            "status": "SUCCESS",
            "event_id": event_id,
            "extracted_iocs": iocs,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Educational Labs & Scenarios
# ---------------------------------------------------------------------------
@router.get("/labs", response_model=list[SIEMLabScenarioResponse])
def list_siem_labs(
    db: DbSession,
) -> Any:
    """List SIEM training labs with difficulty and objectives."""
    labs = db.execute(select(SIEMLabScenario).order_by(SIEMLabScenario.id.asc())).scalars().all()
    if not labs:
        SiemDatasetService.seed_all_siem_data(db)
        labs = db.execute(select(SIEMLabScenario).order_by(SIEMLabScenario.id.asc())).scalars().all()
    return labs


@router.get("/labs/{slug}", response_model=SIEMLabScenarioResponse)
def get_siem_lab(
    slug: str,
    db: DbSession,
) -> Any:
    """Get a specific SIEM lab by slug."""
    lab = db.execute(select(SIEMLabScenario).where(SIEMLabScenario.slug == slug)).scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=404, detail="SIEM lab scenario not found.")
    return lab


@router.post("/labs/{slug}/validate", response_model=SIEMLabValidateResponse)
def validate_siem_lab_submission(
    slug: str,
    payload: SIEMLabValidateRequest,
    db: DbSession,
) -> Any:
    """Validate student's executed query and investigation findings against lab rubric."""
    lab = db.execute(select(SIEMLabScenario).where(SIEMLabScenario.slug == slug)).scalar_one_or_none()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab scenario not found.")

    # Educational rubric evaluation
    score = 0
    criteria = {
        "query_executed": False,
        "relevant_filters_used": False,
        "entity_identified": False,
        "investigation_notes_provided": False,
    }

    if payload.executed_query:
        criteria["query_executed"] = True
        score += 30

    query_str = json.dumps(payload.executed_query).lower()

    # Compare key terms in executed query
    if any(k in query_str for k in ("action", "source_ip", "event_category", "login_failure", "connection_blocked", "dns", "powershell")):
        criteria["relevant_filters_used"] = True
        score += 30

    if payload.identified_entity and len(payload.identified_entity.strip()) >= 3:
        criteria["entity_identified"] = True
        score += 25

    if payload.findings_notes and len(payload.findings_notes.strip()) >= 10:
        criteria["investigation_notes_provided"] = True
        score += 15

    is_success = score >= 70
    feedback = (
        "Outstanding work! Your SIEM search accurately isolated the relevant security events."
        if is_success
        else "Keep exploring! Refine your query filters to hone in on the specific anomalous entity or action."
    )

    return SIEMLabValidateResponse(
        success=is_success,
        score=score,
        feedback=feedback,
        criteria=criteria,
    )
