"""Endpoint Security & Host Investigation Engine API Endpoints."""

import json
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.endpoint_security import (
    EndpointEvent,
    EndpointHost,
    EndpointScenario,
)
from app.schemas.endpoint_security import (
    EndpointAuthenticationResponse,
    EndpointConclusionCreate,
    EndpointConclusionResponse,
    EndpointEventListResponse,
    EndpointEventResponse,
    EndpointEvidenceCreate,
    EndpointEvidenceResponse,
    EndpointFindingCreate,
    EndpointFindingResponse,
    EndpointHostListResponse,
    EndpointHostResponse,
    EndpointHypothesisCreate,
    EndpointHypothesisResponse,
    EndpointHypothesisUpdate,
    EndpointInvestigationCreate,
    EndpointInvestigationListResponse,
    EndpointInvestigationResponse,
    EndpointInvestigationUpdate,
    EndpointScenarioResponse,
    ScenarioValidateRequest,
)
from app.services.endpoint_security.dataset_service import DatasetService
from app.services.endpoint_security.host_service import HostService
from app.services.endpoint_security.integration_service import (
    EndpointIntegrationService,
)
from app.services.endpoint_security.investigation_service import InvestigationService
from app.services.endpoint_security.process_tree_service import ProcessTreeService
from app.services.endpoint_security.telemetry_service import TelemetryService

router = APIRouter()


# ---------------------------------------------------------------------------
# Overview & Platform Stats
# ---------------------------------------------------------------------------
@router.get("/stats", response_model=dict[str, Any])
@router.get("/overview", response_model=dict[str, Any])
def get_endpoint_stats(db: DbSession) -> dict[str, Any]:
    """Return platform-wide synthetic endpoint telemetry dashboard metrics."""
    return HostService.get_endpoint_stats(db)


# ---------------------------------------------------------------------------
# Host Inventory & Detail
# ---------------------------------------------------------------------------
@router.get("/hosts", response_model=EndpointHostListResponse)
def list_hosts(
    db: DbSession,
    platform: str | None = Query(None, description="WINDOWS or LINUX"),
    status: str | None = Query(None, description="ONLINE, OFFLINE, UNKNOWN"),
    environment: str | None = Query(None, description="WORKSTATION, SERVER, TRAINING_VM"),
    risk_level: str | None = Query(None, description="LOW, MEDIUM, HIGH, CRITICAL, UNKNOWN"),
    search: str | None = Query(None, description="Search hostname, display name, IP"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointHostListResponse:
    """List synthetic endpoint hosts with filters and pagination."""
    items, total = HostService.list_hosts(
        db, platform, status, environment, risk_level, search, skip, limit
    )
    return EndpointHostListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}", response_model=EndpointHostResponse)
def get_host(db: DbSession, host_id: str) -> EndpointHost:
    """Fetch single host by integer ID, stable_id (HOST-WIN-001), or hostname."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return host


@router.get("/hosts/{host_id}/overview", response_model=dict[str, Any])
def get_host_overview(db: DbSession, host_id: str) -> dict[str, Any]:
    """Retrieve comprehensive multi-dimensional telemetry overview for a host."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return HostService.get_host_overview(db, host)


# ---------------------------------------------------------------------------
# Host-Centric Telemetry
# ---------------------------------------------------------------------------
@router.get("/hosts/{host_id}/events", response_model=EndpointEventListResponse)
def list_host_events(
    db: DbSession,
    host_id: str,
    event_category: str | None = Query(None),
    event_type: str | None = Query(None),
    username: str | None = Query(None),
    process_name: str | None = Query(None),
    ip: str | None = Query(None),
    domain: str | None = Query(None),
    file_hash: str | None = Query(None),
    severity: str | None = Query(None),
    result: str | None = Query(None),
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Query paginated events specific to a host."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.list_events(
        db=db,
        host_id=host.id,
        event_category=event_category,
        event_type=event_type,
        username=username,
        process_name=process_name,
        ip=ip,
        domain=domain,
        file_hash=file_hash,
        severity=severity,
        result=result,
        search=search,
        skip=skip,
        limit=limit,
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/processes", response_model=list[dict[str, Any]])
def get_process_tree(db: DbSession, host_id: str) -> list[dict[str, Any]]:
    """Construct and return the visual process tree hierarchy for a host."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return ProcessTreeService.build_process_tree(db, host.id)


@router.get("/hosts/{host_id}/processes/{process_id}", response_model=dict[str, Any])
def get_process_details(db: DbSession, host_id: str, process_id: int) -> dict[str, Any]:
    """Retrieve detailed process telemetry including parents, children, and correlated activity."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    details = ProcessTreeService.get_process_details(db, host.id, process_id)
    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    return details


@router.get("/hosts/{host_id}/authentication", response_model=EndpointAuthenticationResponse)
def get_host_authentication(
    db: DbSession,
    host_id: str,
    username: str | None = Query(None),
    result: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointAuthenticationResponse:
    """Fetch authentication attempts and pattern evaluation summary."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    data = TelemetryService.get_authentication_events(
        db, host.id, username, result, skip, limit
    )
    return EndpointAuthenticationResponse(
        total=data["total"],
        events=[EndpointEventResponse.model_validate(e) for e in data["events"]],
        summary=data["summary"],
    )


@router.get("/hosts/{host_id}/network", response_model=EndpointEventListResponse)
def get_host_network(
    db: DbSession,
    host_id: str,
    process_name: str | None = Query(None),
    destination_ip: str | None = Query(None),
    protocol: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Fetch network connections and listener events for a host."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_network_events(
        db, host.id, process_name, destination_ip, protocol, skip, limit
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/dns", response_model=EndpointEventListResponse)
def get_host_dns(
    db: DbSession,
    host_id: str,
    domain: str | None = Query(None),
    process_name: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Fetch DNS query telemetry for a host."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_dns_events(
        db, host.id, domain, process_name, skip, limit
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/files", response_model=EndpointEventListResponse)
def get_host_files(
    db: DbSession,
    host_id: str,
    file_action: str | None = Query(None),
    file_hash: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Fetch file system creation, modification, deletion, and read events."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_file_events(
        db, host.id, file_action, file_hash, skip, limit
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/services", response_model=EndpointEventListResponse)
def get_host_services(
    db: DbSession,
    host_id: str,
    service_action: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Fetch system service state changes and installation telemetry."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_service_events(
        db, host.id, service_action, skip, limit
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/persistence", response_model=EndpointEventListResponse)
def get_host_persistence(
    db: DbSession,
    host_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Fetch scheduled tasks, startup entries, and persistence observations."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_persistence_events(db, host.id, skip, limit)
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/privileges", response_model=EndpointEventListResponse)
def get_host_privileges(
    db: DbSession,
    host_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Fetch privilege changes, elevated processes, and sudo activity."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_privilege_events(db, host.id, skip, limit)
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/hosts/{host_id}/timeline", response_model=EndpointEventListResponse)
def get_host_timeline(
    db: DbSession,
    host_id: str,
    categories: Annotated[list[str] | None, Query()] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> EndpointEventListResponse:
    """Fetch chronological unified host timeline with optional category filters."""
    host = HostService.get_host_by_id_or_stable_id(db, host_id)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")

    items, total = TelemetryService.get_timeline(
        db, host.id, categories=categories, skip=skip, limit=limit
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Global Event Search & Single Event Details
# ---------------------------------------------------------------------------
@router.get("/events", response_model=EndpointEventListResponse)
def search_events(
    db: DbSession,
    event_category: str | None = Query(None),
    event_type: str | None = Query(None),
    username: str | None = Query(None),
    process_name: str | None = Query(None),
    ip: str | None = Query(None),
    domain: str | None = Query(None),
    file_hash: str | None = Query(None),
    severity: str | None = Query(None),
    result: str | None = Query(None),
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointEventListResponse:
    """Search synthetic endpoint events across all hosts with filters."""
    items, total = TelemetryService.list_events(
        db=db,
        event_category=event_category,
        event_type=event_type,
        username=username,
        process_name=process_name,
        ip=ip,
        domain=domain,
        file_hash=file_hash,
        severity=severity,
        result=result,
        search=search,
        skip=skip,
        limit=limit,
    )
    return EndpointEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/events/{event_id}", response_model=EndpointEventResponse)
def get_event(db: DbSession, event_id: str) -> EndpointEvent:
    """Fetch single event by database ID or string event_id."""
    event = TelemetryService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


# ---------------------------------------------------------------------------
# Host Investigations & Workflow
# ---------------------------------------------------------------------------
@router.get("/investigations", response_model=EndpointInvestigationListResponse)
def list_investigations(
    db: DbSession,
    current_user: CurrentUser,
    host_id: int | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EndpointInvestigationListResponse:
    """List investigations owned by the current student."""
    user_id = None if current_user.role == "ADMIN" else current_user.id
    items, total = InvestigationService.list_investigations(
        db, user_id=user_id, host_id=host_id, status=status, priority=priority, skip=skip, limit=limit
    )
    return EndpointInvestigationListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/investigations", response_model=EndpointInvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(
    db: DbSession,
    current_user: CurrentUser,
    payload: EndpointInvestigationCreate,
) -> EndpointInvestigationResponse:
    """Initialize a new host investigation."""
    try:
        inv = InvestigationService.create_investigation(
            db=db,
            user_id=current_user.id,
            host_id=payload.host_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            scenario_slug=payload.scenario_slug,
        )
        return InvestigationService.get_investigation(db, inv.id, current_user.id)  # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/investigations/{investigation_id}", response_model=EndpointInvestigationResponse)
def get_investigation(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
) -> EndpointInvestigationResponse:
    """Get investigation details with hypotheses, evidence, findings, and conclusion."""
    user_id = None if current_user.role == "ADMIN" else current_user.id
    inv = InvestigationService.get_investigation(db, investigation_id, user_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found or access denied")
    return inv  # type: ignore


@router.patch("/investigations/{investigation_id}", response_model=EndpointInvestigationResponse)
def update_investigation(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
    payload: EndpointInvestigationUpdate,
) -> EndpointInvestigationResponse:
    """Update investigation status, priority, or description."""
    user_id = None if current_user.role == "ADMIN" else current_user.id
    inv = InvestigationService.update_investigation(
        db=db,
        investigation_id=investigation_id,
        user_id=user_id or current_user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
    )
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found or access denied")
    return InvestigationService.get_investigation(db, inv.id, user_id)  # type: ignore


@router.post("/investigations/{investigation_id}/hypotheses", response_model=EndpointHypothesisResponse, status_code=status.HTTP_201_CREATED)
def add_hypothesis(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
    payload: EndpointHypothesisCreate,
) -> EndpointHypothesisResponse:
    """Add a working hypothesis to an investigation."""
    try:
        user_id = None if current_user.role == "ADMIN" else current_user.id
        return InvestigationService.add_hypothesis(
            db=db,
            investigation_id=investigation_id,
            user_id=user_id or current_user.id,
            statement=payload.statement,
            status=payload.status,
            confidence=payload.confidence,
            analyst_notes=payload.analyst_notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/investigations/{investigation_id}/hypotheses/{hypothesis_id}", response_model=EndpointHypothesisResponse)
def update_hypothesis(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
    hypothesis_id: int,
    payload: EndpointHypothesisUpdate,
) -> EndpointHypothesisResponse:
    """Update state or confidence of an investigative hypothesis."""
    user_id = None if current_user.role == "ADMIN" else current_user.id
    hyp = InvestigationService.update_hypothesis(
        db=db,
        hypothesis_id=hypothesis_id,
        user_id=user_id or current_user.id,
        status=payload.status,
        confidence=payload.confidence,
        analyst_notes=payload.analyst_notes,
    )
    if not hyp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hypothesis not found or access denied")
    return hyp


@router.post("/investigations/{investigation_id}/evidence", response_model=EndpointEvidenceResponse, status_code=status.HTTP_201_CREATED)
def add_evidence(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
    payload: EndpointEvidenceCreate,
) -> EndpointEvidenceResponse:
    """Attach supporting, contradicting, or context evidence."""
    try:
        user_id = None if current_user.role == "ADMIN" else current_user.id
        return InvestigationService.add_evidence(
            db=db,
            investigation_id=investigation_id,
            user_id=user_id or current_user.id,
            title=payload.title,
            description=payload.description,
            evidence_type=payload.evidence_type,
            relevance=payload.relevance,
            event_id=payload.event_id,
            hypothesis_id=payload.hypothesis_id,
            artifact_data=payload.artifact_data,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/investigations/{investigation_id}/findings", response_model=EndpointFindingResponse, status_code=status.HTTP_201_CREATED)
def add_finding(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
    payload: EndpointFindingCreate,
) -> EndpointFindingResponse:
    """Record an analytical finding milestone."""
    try:
        user_id = None if current_user.role == "ADMIN" else current_user.id
        return InvestigationService.add_finding(
            db=db,
            investigation_id=investigation_id,
            user_id=user_id or current_user.id,
            title=payload.title,
            narrative=payload.narrative,
            mitre_attack_id=payload.mitre_attack_id,
            severity=payload.severity,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/investigations/{investigation_id}/conclusion", response_model=EndpointConclusionResponse)
def submit_conclusion(
    db: DbSession,
    current_user: CurrentUser,
    investigation_id: int,
    payload: EndpointConclusionCreate,
) -> EndpointConclusionResponse:
    """Conclude investigation, evaluate analytical rubric, and generate Training Score."""
    try:
        user_id = None if current_user.role == "ADMIN" else current_user.id
        return InvestigationService.submit_conclusion(
            db=db,
            investigation_id=investigation_id,
            user_id=user_id or current_user.id,
            summary=payload.summary,
            verdict=payload.verdict,
            lessons_learned=payload.lessons_learned,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ---------------------------------------------------------------------------
# Cross-Platform Pivots & Integrations
# ---------------------------------------------------------------------------
@router.post("/events/{event_id}/start-hunt", response_model=dict[str, Any])
@router.post("/events/{event_id}/start-threat-hunt", response_model=dict[str, Any])
def start_threat_hunt(
    db: DbSession,
    current_user: CurrentUser,
    event_id: str,
) -> dict[str, Any]:
    """Launch a Step 14 Threat Hunting campaign initialized with endpoint event telemetry."""
    event = TelemetryService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    hunt = EndpointIntegrationService.start_threat_hunt(db, event, current_user.id)
    return {
        "hunt_id": hunt.hunt_id,
        "title": hunt.title,
        "status": hunt.status,
        "redirect_url": f"/threat-hunting/workspace/{hunt.id}",
    }


@router.post("/events/{event_id}/investigate-in-soc", response_model=dict[str, Any])
def investigate_in_soc(
    db: DbSession,
    current_user: CurrentUser,
    event_id: str,
) -> dict[str, Any]:
    """Escalate an endpoint security event into a Step 12 SOC Investigation case."""
    event = TelemetryService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    soc_inv = EndpointIntegrationService.investigate_in_soc(db, event, current_user.id)
    return {
        "investigation_id": soc_inv.investigation_id,
        "title": soc_inv.title,
        "status": soc_inv.status,
        "redirect_url": f"/soc/investigations/{soc_inv.id}",
    }


@router.post("/events/{event_id}/pivot-intel", response_model=dict[str, Any])
def pivot_to_intel(
    db: DbSession,
    event_id: str,
) -> dict[str, Any]:
    """Extract and correlate file hashes, IPs, and domains with Step 13 Threat Intelligence."""
    event = TelemetryService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return EndpointIntegrationService.pivot_to_threat_intel(db, event)


@router.get("/events/{event_id}/correlate-siem", response_model=list[dict[str, Any]])
def correlate_with_siem(
    db: DbSession,
    event_id: str,
) -> list[dict[str, Any]]:
    """Cross-reference endpoint event with Step 15 SIEM normalized security events."""
    event = TelemetryService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return EndpointIntegrationService.correlate_with_siem(db, event)


@router.get("/events/{event_id}/correlate-pcap", response_model=list[dict[str, Any]])
def correlate_with_pcap(
    db: DbSession,
    event_id: str,
) -> list[dict[str, Any]]:
    """Match endpoint network connection with offline PCAP packet traces."""
    event = TelemetryService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return EndpointIntegrationService.correlate_with_pcap(db, event)


# ---------------------------------------------------------------------------
# Guided Scenarios & Lab Engine
# ---------------------------------------------------------------------------
@router.get("/scenarios", response_model=list[EndpointScenarioResponse])
def list_scenarios(db: DbSession) -> list[dict[str, Any]]:
    """List guided hands-on host investigation scenarios."""
    scenarios = list(
        db.scalars(
            select(EndpointScenario)
            .where(EndpointScenario.is_published.is_(True))
            .order_by(EndpointScenario.id.asc())
        ).all()
    )
    results = []
    for sc in scenarios:
        results.append({
            "id": sc.id,
            "scenario_id": sc.scenario_id,
            "slug": sc.slug,
            "title": sc.title,
            "difficulty": sc.difficulty,
            "category": sc.category,
            "target_host_stable_id": sc.target_host_stable_id,
            "description": sc.description,
            "background": sc.background,
            "objectives": json.loads(sc.objectives_json) if sc.objectives_json else [],
            "hints": json.loads(sc.hints_json) if sc.hints_json else [],
            "estimated_minutes": sc.estimated_minutes,
            "is_published": sc.is_published,
        })
    return results


@router.get("/scenarios/{slug}", response_model=EndpointScenarioResponse)
def get_scenario(db: DbSession, slug: str) -> dict[str, Any]:
    """Retrieve details and objectives of a guided scenario."""
    sc = db.execute(
        select(EndpointScenario).where(EndpointScenario.slug == slug)
    ).scalars().first()
    if not sc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")

    return {
        "id": sc.id,
        "scenario_id": sc.scenario_id,
        "slug": sc.slug,
        "title": sc.title,
        "difficulty": sc.difficulty,
        "category": sc.category,
        "target_host_stable_id": sc.target_host_stable_id,
        "description": sc.description,
        "background": sc.background,
        "objectives": json.loads(sc.objectives_json) if sc.objectives_json else [],
        "hints": json.loads(sc.hints_json) if sc.hints_json else [],
        "estimated_minutes": sc.estimated_minutes,
        "is_published": sc.is_published,
    }


@router.post("/scenarios/{slug}/validate", response_model=dict[str, Any])
def validate_scenario(
    db: DbSession,
    slug: str,
    payload: ScenarioValidateRequest,
) -> dict[str, Any]:
    """Validate student findings against the guided scenario solution rubric."""
    try:
        return DatasetService.validate_scenario(db, slug, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
