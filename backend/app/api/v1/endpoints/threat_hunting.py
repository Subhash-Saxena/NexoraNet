"""FastAPI endpoints for Step 14 Threat Hunting & Investigation Workspace."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.detection import DetectionAlert
from app.models.enums import HuntStatus
from app.models.threat_hunting import (
    HuntDataset,
    HuntEvent,
    ThreatHunt,
    ThreatHuntEvidence,
    ThreatHuntFinding,
    ThreatHuntNote,
)
from app.models.threat_intel import Indicator
from app.schemas.threat_hunting import (
    DatasetAnalyticsResponse,
    DatasetCreate,
    DatasetResponse,
    EntityGraphResponse,
    HuntConclusionRequest,
    HuntCreate,
    HuntDetailResponse,
    HuntEvidenceCreate,
    HuntEvidenceResponse,
    HuntEvidenceUpdate,
    HuntFindingCreate,
    HuntFindingResponse,
    HuntHypothesisCreate,
    HuntHypothesisResponse,
    HuntHypothesisUpdate,
    HuntLaunchFromAlert,
    HuntLaunchFromIOC,
    HuntNoteCreate,
    HuntNoteResponse,
    HuntOverviewResponse,
    HuntQueryRequest,
    HuntQueryResponse,
    HuntResponse,
    HuntScenarioResponse,
    HuntScoreResponse,
    HuntTimelineResponse,
    PivotRequest,
    PivotResponse,
)
from app.services.threat_hunting import (
    HuntDatasetService,
    HuntInvestigationService,
    HuntQueryEngine,
    HuntScenarioService,
    HuntScoringService,
    ThreatHuntService,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Overview Metrics
# ---------------------------------------------------------------------------
@router.get("/overview", response_model=HuntOverviewResponse)
def get_threat_hunting_overview(db: DbSession, current_user: CurrentUser):
    """Retrieve high-level dashboard metrics for threat hunting workspace."""
    total_hunts = db.scalar(select(func.count(ThreatHunt.id)).where(ThreatHunt.user_id == current_user.id)) or 0
    active_hunts = (
        db.scalar(
            select(func.count(ThreatHunt.id)).where(
                ThreatHunt.user_id == current_user.id,
                ThreatHunt.status.in_([HuntStatus.RUNNING.value, HuntStatus.READY.value]),
            )
        )
        or 0
    )
    completed_hunts = (
        db.scalar(
            select(func.count(ThreatHunt.id)).where(
                ThreatHunt.user_id == current_user.id,
                ThreatHunt.status == HuntStatus.COMPLETED.value,
            )
        )
        or 0
    )
    total_datasets = db.scalar(select(func.count(HuntDataset.id))) or 0
    total_events = db.scalar(select(func.count(HuntEvent.id))) or 0
    total_scenarios = len(HuntScenarioService.SCENARIOS)

    recent_hunts = ThreatHuntService.list_hunts(db, user_id=current_user.id, limit=5)

    return HuntOverviewResponse(
        total_hunts=total_hunts,
        active_hunts=active_hunts,
        completed_hunts=completed_hunts,
        total_datasets=total_datasets,
        total_events=total_events,
        total_scenarios=total_scenarios,
        recent_hunts=recent_hunts,
    )


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------
@router.get("/datasets", response_model=list[DatasetResponse])
def list_datasets(
    db: DbSession,
    dataset_type: str | None = Query(None, description="Filter by HuntDatasetType"),
    status: str | None = Query(None, description="Filter by status"),
):
    """List all available defensive telemetry datasets."""
    return HuntDatasetService.list_datasets(db, dataset_type=dataset_type, status=status)


@router.get("/datasets/{dataset_id}", response_model=DatasetAnalyticsResponse)
def get_dataset_analytics(dataset_id: int, db: DbSession):
    """Retrieve telemetry metrics and protocol distributions for a dataset."""
    analytics = HuntDatasetService.get_dataset_analytics(db, dataset_id)
    if not analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return analytics


@router.post("/datasets", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(payload: DatasetCreate, db: DbSession, current_user: CurrentUser):
    """Register a new telemetry dataset."""
    existing = HuntDatasetService.get_dataset_by_code(db, payload.dataset_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset with code '{payload.dataset_id}' already exists",
        )
    return HuntDatasetService.create_dataset(
        db=db,
        dataset_id=payload.dataset_id,
        name=payload.name,
        description=payload.description,
        dataset_type=payload.dataset_type,
        source=payload.source,
        metadata=payload.metadata,
    )


# ---------------------------------------------------------------------------
# Guided Scenarios
# ---------------------------------------------------------------------------
@router.get("/scenarios", response_model=list[HuntScenarioResponse])
def list_scenarios(difficulty: str | None = Query(None, description="Filter by difficulty")):
    """List guided MITRE-mapped educational threat hunting training scenarios."""
    return HuntScenarioService.list_scenarios(difficulty=difficulty)


@router.get("/scenarios/{slug}", response_model=HuntScenarioResponse)
def get_scenario(slug: str):
    """Retrieve detailed briefing for a training scenario."""
    scenario = HuntScenarioService.get_scenario(slug)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return scenario


@router.post("/scenarios/{slug}/launch", response_model=HuntResponse, status_code=status.HTTP_201_CREATED)
def launch_scenario(slug: str, db: DbSession, current_user: CurrentUser):
    """Launch a threat hunt pre-configured from an educational training scenario."""
    scenario = HuntScenarioService.get_scenario(slug)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")

    target_ds = HuntDatasetService.get_dataset_by_code(db, scenario["dataset_code"])
    target_ds_id = target_ds.id if target_ds else None

    hunt = HuntScenarioService.launch_scenario(
        db=db,
        user_id=current_user.id,
        slug=slug,
        target_dataset_id=target_ds_id,
    )
    return hunt


# ---------------------------------------------------------------------------
# Hunts Management
# ---------------------------------------------------------------------------
@router.get("/hunts", response_model=list[HuntResponse])
def list_hunts(
    db: DbSession,
    current_user: CurrentUser,
    status: str | None = Query(None),
    difficulty: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List threat hunting sessions belonging to the authenticated user."""
    return ThreatHuntService.list_hunts(
        db,
        user_id=current_user.id,
        status=status,
        difficulty=difficulty,
        limit=limit,
        offset=offset,
    )


@router.post("/hunts", response_model=HuntResponse, status_code=status.HTTP_201_CREATED)
def create_hunt(payload: HuntCreate, db: DbSession, current_user: CurrentUser):
    """Create a custom threat hunting campaign."""
    return ThreatHuntService.create_hunt(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        objective=payload.objective,
        dataset_id=payload.dataset_id,
        difficulty=payload.difficulty,
        scenario_slug=payload.scenario_slug,
        initial_pivot_type=payload.initial_pivot_type,
        initial_pivot_value=payload.initial_pivot_value,
    )


@router.post("/launch-from-alert", response_model=HuntResponse, status_code=status.HTTP_201_CREATED)
def launch_from_alert(payload: HuntLaunchFromAlert, db: DbSession, current_user: CurrentUser):
    """Initiate a threat hunt campaign directly from a Detection Alert."""
    alert = db.get(DetectionAlert, payload.alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    title = payload.title or f"Hunt: Alert - {alert.title}"
    pivot_val = alert.source_ip or alert.destination_ip or str(alert.id)
    hunt = ThreatHuntService.create_hunt(
        db=db,
        user_id=current_user.id,
        title=title,
        description=f"Initiated from Detection Alert #{alert.id}: {alert.description}",
        objective=f"Hunt for broader campaign activity related to {pivot_val} across network telemetry.",
        dataset_id=payload.dataset_id,
        difficulty="INTERMEDIATE",
        initial_pivot_type="IP" if alert.source_ip else "ALERT",
        initial_pivot_value=pivot_val,
    )
    return hunt


@router.post("/launch-from-ioc", response_model=HuntResponse, status_code=status.HTTP_201_CREATED)
def launch_from_ioc(payload: HuntLaunchFromIOC, db: DbSession, current_user: CurrentUser):
    """Initiate a threat hunt campaign directly from a Threat Intelligence Indicator."""
    ioc = db.get(Indicator, payload.ioc_id)
    if not ioc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")

    title = payload.title or f"Hunt: IOC - {ioc.value}"
    hunt = ThreatHuntService.create_hunt(
        db=db,
        user_id=current_user.id,
        title=title,
        description=f"Initiated from Threat Intel Indicator {ioc.indicator_id} ({ioc.indicator_type}): {ioc.description or ioc.value}",
        objective=f"Sweep enterprise network telemetry for presence or beaconing patterns matching {ioc.value}.",
        dataset_id=payload.dataset_id,
        difficulty="INTERMEDIATE",
        initial_pivot_type=ioc.indicator_type,
        initial_pivot_value=ioc.value,
    )
    return hunt


@router.get("/hunts/{hunt_id}", response_model=HuntDetailResponse)
def get_hunt_detail(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """Retrieve full threat hunt state including dataset, hypotheses, evidence, findings, and notes."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return hunt


@router.post("/hunts/{hunt_id}/start", response_model=HuntResponse)
def start_hunt(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """Start or resume a threat hunting investigation."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return ThreatHuntService.start_hunt(db, hunt_id)


@router.post("/hunts/{hunt_id}/pause", response_model=HuntResponse)
def pause_hunt(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """Pause an active threat hunt session."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return ThreatHuntService.pause_hunt(db, hunt_id)


@router.post("/hunts/{hunt_id}/complete", response_model=HuntResponse)
def complete_hunt(hunt_id: int, payload: HuntConclusionRequest, db: DbSession, current_user: CurrentUser):
    """Conclude a threat hunt with analytical disposition."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return ThreatHuntService.complete_hunt(
        db,
        hunt_id=hunt_id,
        conclusion=payload.conclusion,
        conclusion_disposition=payload.conclusion_disposition,
    )


# ---------------------------------------------------------------------------
# Query Engine & Telemetry Exploration
# ---------------------------------------------------------------------------
@router.post("/hunts/{hunt_id}/query", response_model=HuntQueryResponse)
def execute_hunt_query(
    hunt_id: int,
    payload: HuntQueryRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Execute safe structured or free-text query against hunt telemetry."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")

    ds_id = payload.dataset_id or hunt.dataset_id
    conditions_dicts = [c.model_dump() for c in payload.conditions] if payload.conditions else None

    # Log query into hunt history
    query_repr = payload.query_string or (
        f"{payload.conjunction.upper()} across {len(conditions_dicts)} conditions" if conditions_dicts else "ALL"
    )
    ThreatHuntService.log_query(db, hunt_id, query_repr)

    result = HuntQueryEngine.execute_hunt_query(
        db=db,
        dataset_id=ds_id,
        conditions=conditions_dicts,
        query_string=payload.query_string,
        search_text=payload.search_text,
        conjunction=payload.conjunction,
        limit=payload.limit,
        offset=payload.offset,
        sort_by=payload.sort_by,
        sort_desc=payload.sort_desc,
    )
    return result


@router.get("/hunts/{hunt_id}/timeline", response_model=HuntTimelineResponse)
def get_hunt_timeline(
    hunt_id: int,
    db: DbSession,
    current_user: CurrentUser,
    interval: str = Query("minute", pattern="^(minute|hour|day)$"),
):
    """Retrieve aggregated chronological timeline and milestone events."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return ThreatHuntService.build_hunt_timeline(db, hunt, interval=interval)


@router.get("/hunts/{hunt_id}/entities", response_model=EntityGraphResponse)
def get_entity_graph(
    hunt_id: int,
    db: DbSession,
    current_user: CurrentUser,
    focus: str | None = Query(None, description="Focus entity label"),
    max_depth: int = Query(2, ge=1, le=3),
    max_nodes: int = Query(50, ge=5, le=100),
):
    """Retrieve bounded entity relationship graph around hunt entities."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return ThreatHuntService.build_entity_graph(
        db, hunt, focus_entity=focus, max_depth=max_depth, max_nodes=max_nodes
    )


@router.post("/hunts/{hunt_id}/pivot", response_model=PivotResponse)
def pivot_hunt_entity(
    hunt_id: int,
    payload: PivotRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Correlate an entity (IP, Domain, Port) across telemetry, alerts, and indicators."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")
    return ThreatHuntService.pivot_entity(
        db, hunt, entity_type=payload.entity_type, entity_value=payload.entity_value
    )


# ---------------------------------------------------------------------------
# Hypotheses
# ---------------------------------------------------------------------------
@router.get("/hunts/{hunt_id}/hypotheses", response_model=list[HuntHypothesisResponse])
def list_hypotheses(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """List analytical hypotheses for the hunt session."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.list_hypotheses(db, hunt_id)


@router.post(
    "/hunts/{hunt_id}/hypotheses",
    response_model=HuntHypothesisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hypothesis(
    hunt_id: int,
    payload: HuntHypothesisCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Formulate a new analytical hypothesis."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.create_hypothesis(
        db=db,
        hunt_id=hunt_id,
        title=payload.title,
        description=payload.description,
        confidence=payload.confidence,
    )


@router.put("/hypotheses/{hypothesis_id}", response_model=HuntHypothesisResponse)
def update_hypothesis(
    hypothesis_id: int,
    payload: HuntHypothesisUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update hypothesis status, confidence, or analyst reasoning."""
    hyp = HuntInvestigationService.get_hypothesis(db, hypothesis_id)
    if not hyp or hyp.hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hypothesis not found")
    return HuntInvestigationService.update_hypothesis(
        db=db,
        hypothesis_id=hypothesis_id,
        status=payload.status,
        confidence=payload.confidence,
        analyst_reasoning=payload.analyst_reasoning,
        title=payload.title,
        description=payload.description,
    )


@router.delete("/hypotheses/{hypothesis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hypothesis(hypothesis_id: int, db: DbSession, current_user: CurrentUser):
    """Delete a hypothesis."""
    hyp = HuntInvestigationService.get_hypothesis(db, hypothesis_id)
    if not hyp or hyp.hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hypothesis not found")
    HuntInvestigationService.delete_hypothesis(db, hypothesis_id)


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
@router.get("/hunts/{hunt_id}/evidence", response_model=list[HuntEvidenceResponse])
def list_evidence(
    hunt_id: int,
    db: DbSession,
    current_user: CurrentUser,
    hypothesis_id: int | None = Query(None),
):
    """List collected evidence records."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.list_evidence(db, hunt_id=hunt_id, hypothesis_id=hypothesis_id)


@router.post(
    "/hunts/{hunt_id}/evidence",
    response_model=HuntEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_evidence(
    hunt_id: int,
    payload: HuntEvidenceCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Collect and bind evidence to a hunt and hypothesis."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.add_evidence(
        db=db,
        hunt_id=hunt_id,
        evidence_type=payload.evidence_type,
        source_id=payload.source_id,
        description=payload.description,
        hypothesis_id=payload.hypothesis_id,
        relevance=payload.relevance,
        analyst_note=payload.analyst_note,
        data_snapshot=payload.data_snapshot,
    )


@router.put("/evidence/{evidence_id}", response_model=HuntEvidenceResponse)
def update_evidence(
    evidence_id: int,
    payload: HuntEvidenceUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update evidence relevance or analyst notes."""
    ev = db.get(ThreatHuntEvidence, evidence_id)
    if not ev or ev.hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    return HuntInvestigationService.update_evidence(
        db=db,
        evidence_id=evidence_id,
        relevance=payload.relevance,
        analyst_note=payload.analyst_note,
        hypothesis_id=payload.hypothesis_id,
    )


@router.delete("/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evidence(evidence_id: int, db: DbSession, current_user: CurrentUser):
    """Delete an evidence item."""
    ev = db.get(ThreatHuntEvidence, evidence_id)
    if not ev or ev.hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    HuntInvestigationService.delete_evidence(db, evidence_id)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------
@router.get("/hunts/{hunt_id}/findings", response_model=list[HuntFindingResponse])
def list_findings(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """List structured discoveries and detection gap findings."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.list_findings(db, hunt_id)


@router.post(
    "/hunts/{hunt_id}/findings",
    response_model=HuntFindingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_finding(
    hunt_id: int,
    payload: HuntFindingCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Document a new finding."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.create_finding(
        db=db,
        hunt_id=hunt_id,
        title=payload.title,
        description=payload.description,
        finding_type=payload.finding_type,
        confidence=payload.confidence,
        evidence_count=payload.evidence_count,
        mitigation_recommendation=payload.mitigation_recommendation,
    )


@router.delete("/findings/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_finding(finding_id: int, db: DbSession, current_user: CurrentUser):
    """Delete a finding."""
    f = db.get(ThreatHuntFinding, finding_id)
    if not f or f.hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")
    HuntInvestigationService.delete_finding(db, finding_id)


# ---------------------------------------------------------------------------
# Analyst Notes
# ---------------------------------------------------------------------------
@router.get("/hunts/{hunt_id}/notes", response_model=list[HuntNoteResponse])
def list_notes(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """List analyst journal entries."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.list_notes(db, hunt_id)


@router.post(
    "/hunts/{hunt_id}/notes",
    response_model=HuntNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_note(
    hunt_id: int,
    payload: HuntNoteCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Append a note to the hunt journal."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    return HuntInvestigationService.add_note(
        db=db,
        hunt_id=hunt_id,
        user_id=current_user.id,
        author_name=current_user.display_name or current_user.username,
        content=payload.content,
        related_event_id=payload.related_event_id,
        related_alert_id=payload.related_alert_id,
        related_ioc_id=payload.related_ioc_id,
        related_hypothesis_id=payload.related_hypothesis_id,
    )


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: DbSession, current_user: CurrentUser):
    """Delete a journal note."""
    n = db.get(ThreatHuntNote, note_id)
    if not n or n.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    HuntInvestigationService.delete_note(db, note_id)


# ---------------------------------------------------------------------------
# Conclusion & Educational Scoring
# ---------------------------------------------------------------------------
@router.post("/hunts/{hunt_id}/conclusion", response_model=HuntScoreResponse)
def submit_conclusion(
    hunt_id: int,
    payload: HuntConclusionRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Submit conclusion narrative, finalize hunt, and calculate training rubric score."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")

    ThreatHuntService.complete_hunt(
        db,
        hunt_id=hunt_id,
        conclusion=payload.conclusion,
        conclusion_disposition=payload.conclusion_disposition,
    )
    score_result = HuntScoringService.evaluate_hunt(db, hunt)
    return score_result


@router.get("/hunts/{hunt_id}/score", response_model=HuntScoreResponse)
def get_hunt_score(hunt_id: int, db: DbSession, current_user: CurrentUser):
    """Retrieve educational rubric score and breakdown."""
    hunt = ThreatHuntService.get_hunt(db, hunt_id)
    if not hunt or hunt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat hunt session not found")

    if hunt.score is None:
        return HuntScoringService.evaluate_hunt(db, hunt)

    breakdown = {}
    if hunt.score_breakdown:
        try:
            breakdown = json.loads(hunt.score_breakdown)
        except (json.JSONDecodeError, TypeError, ValueError):
            breakdown = {}

    score = hunt.score or 0.0
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    return HuntScoreResponse(
        hunt_id=hunt.hunt_id,
        total_score=score,
        max_score=100,
        grade=grade,
        breakdown=breakdown,
    )
