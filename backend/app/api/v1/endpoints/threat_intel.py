"""API endpoints for Step 13 Threat Intelligence & IOC Investigation."""

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import func, or_

from app.api.deps import CurrentUser, DbSession
from app.models.soc import Case
from app.models.threat_intel import (
    Indicator,
    IndicatorNote,
    IndicatorObservation,
    IndicatorRelationship,
    IndicatorTimeline,
    ThreatIntelChallenge,
    ThreatIntelSource,
    WatchlistItem,
)
from app.schemas.threat_intel import (
    ChallengeAttemptResponse,
    ChallengeSubmitRequest,
    ImportResponse,
    IndicatorBriefResponse,
    IndicatorClassificationUpdateRequest,
    IndicatorCreateRequest,
    IndicatorDetailResponse,
    IndicatorNoteCreateRequest,
    IndicatorNoteResponse,
    IndicatorObservationResponse,
    IndicatorRelationshipResponse,
    IndicatorTimelineResponse,
    RelationshipCreateRequest,
    ThreatIntelChallengeBriefResponse,
    ThreatIntelChallengeDetailResponse,
    ThreatIntelGraphResponse,
    ThreatIntelOverviewResponse,
    ThreatIntelSourceResponse,
    WatchlistCreateRequest,
    WatchlistResponse,
)
from app.services.threat_intel.challenge_service import challenge_service
from app.services.threat_intel.import_export_service import import_export_service
from app.services.threat_intel.indicator_service import indicator_service
from app.services.threat_intel.watchlist_service import watchlist_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Overview & Metrics
# ---------------------------------------------------------------------------
@router.get("/overview", response_model=ThreatIntelOverviewResponse)
def get_threat_intel_overview(db: DbSession, current_user: CurrentUser) -> Any:
    """Retrieve high-level summary metrics of threat intelligence indicators and activity."""
    total_indicators = db.query(Indicator).count()

    # Classification counts
    cls_counts = (
        db.query(Indicator.classification, func.count(Indicator.id))
        .group_by(Indicator.classification)
        .all()
    )
    by_classification = {k: v for k, v in cls_counts}

    # Type counts
    type_counts = (
        db.query(Indicator.indicator_type, func.count(Indicator.id))
        .group_by(Indicator.indicator_type)
        .all()
    )
    by_type = {k: v for k, v in type_counts}

    # Severity counts
    sev_counts = (
        db.query(Indicator.severity, func.count(Indicator.id))
        .group_by(Indicator.severity)
        .all()
    )
    by_severity = {k: v for k, v in sev_counts}

    now_utc = datetime.now(timezone.utc)
    active_watchlists = (
        db.query(WatchlistItem)
        .filter((WatchlistItem.expires_at.is_(None)) | (WatchlistItem.expires_at > now_utc))
        .count()
    )

    total_challenges = db.query(ThreatIntelChallenge).count()

    recent_indicators = (
        db.query(Indicator)
        .order_by(Indicator.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_indicators": total_indicators,
        "by_classification": by_classification,
        "by_type": by_type,
        "by_severity": by_severity,
        "active_watchlists": active_watchlists,
        "total_challenges": total_challenges,
        "recent_indicators": recent_indicators,
    }


# ---------------------------------------------------------------------------
# Indicators CRUD & Actions
# ---------------------------------------------------------------------------
@router.get("/indicators", response_model=list[IndicatorBriefResponse])
def list_indicators(
    db: DbSession,
    indicator_type: str | None = Query(None, description="Filter by indicator type"),
    classification: str | None = Query(None, description="Filter by classification"),
    confidence: str | None = Query(None, description="Filter by confidence"),
    severity: str | None = Query(None, description="Filter by severity"),
    indicator_status: str | None = Query(None, alias="status", description="Filter by status"),
    search: str | None = Query(None, description="Search by value, ID, or description"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Any:
    """List threat intelligence indicators with optional filtering and pagination."""
    query = db.query(Indicator)

    if indicator_type:
        query = query.filter(Indicator.indicator_type == indicator_type.upper())
    if classification:
        query = query.filter(Indicator.classification == classification.upper())
    if confidence:
        query = query.filter(Indicator.confidence == confidence.upper())
    if severity:
        query = query.filter(Indicator.severity == severity.upper())
    if indicator_status:
        query = query.filter(Indicator.status == indicator_status.upper())
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Indicator.value.ilike(search_filter),
                Indicator.display_value.ilike(search_filter),
                Indicator.indicator_id.ilike(search_filter),
                Indicator.description.ilike(search_filter),
            )
        )

    return query.order_by(Indicator.created_at.desc()).offset(offset).limit(limit).all()


@router.post("/indicators", response_model=IndicatorDetailResponse, status_code=status.HTTP_201_CREATED)
def create_indicator(
    payload: IndicatorCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Normalize and ingest a new threat indicator."""
    indicator = indicator_service.get_or_create_indicator(
        db=db,
        raw_val=payload.raw_value,
        indicator_type=payload.indicator_type,
        source_name=payload.source_name,
        actor=current_user,
    )

    if payload.description:
        indicator.description = payload.description
    if payload.tags:
        indicator.tags = json.dumps(payload.tags)
    db.commit()
    db.refresh(indicator)

    is_watched = watchlist_service.is_watched(db, indicator.id, current_user.id)
    resp = IndicatorDetailResponse.model_validate(indicator)
    resp.is_watched = is_watched
    return resp


@router.get("/indicators/{indicator_id}", response_model=IndicatorDetailResponse)
def get_indicator(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve full indicator details, including observations, relationships, timeline, and analyst notes."""
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

    is_watched = watchlist_service.is_watched(db, indicator.id, current_user.id)
    resp = IndicatorDetailResponse.model_validate(indicator)
    resp.is_watched = is_watched
    return resp


@router.post("/indicators/{indicator_id}/enrich", response_model=IndicatorDetailResponse)
def enrich_indicator(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Explicitly query synthetic intelligence to enrich indicator reputation."""
    indicator = indicator_service.enrich_indicator(db=db, indicator_id=indicator_id)
    is_watched = watchlist_service.is_watched(db, indicator.id, current_user.id)
    resp = IndicatorDetailResponse.model_validate(indicator)
    resp.is_watched = is_watched
    return resp


@router.patch("/indicators/{indicator_id}/classification", response_model=IndicatorDetailResponse)
def update_indicator_classification(
    indicator_id: int,
    payload: IndicatorClassificationUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Update analyst classification and document reasoning."""
    indicator = indicator_service.update_classification(
        db=db,
        indicator_id=indicator_id,
        classification=payload.classification,
        reason=payload.reason,
        status_val=payload.status,
        actor=current_user,
    )
    is_watched = watchlist_service.is_watched(db, indicator.id, current_user.id)
    resp = IndicatorDetailResponse.model_validate(indicator)
    resp.is_watched = is_watched
    return resp


@router.get("/indicators/{indicator_id}/evidence", response_model=list[IndicatorObservationResponse])
def get_indicator_evidence(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve telemetry observations associated with an indicator."""
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")
    return db.query(IndicatorObservation).filter(IndicatorObservation.indicator_id == indicator_id).order_by(IndicatorObservation.created_at.desc()).all()


@router.get("/indicators/{indicator_id}/alerts")
def get_indicator_correlated_alerts(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve detection alerts correlated with this indicator."""
    correlation = indicator_service.correlate_indicator(db=db, indicator_id=indicator_id)
    return {
        "indicator_id": indicator_id,
        "total_alerts": correlation["total_correlated_alerts"],
        "alerts": correlation["alerts"],
    }


@router.get("/indicators/{indicator_id}/investigations")
def get_indicator_correlated_investigations(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve active SOC investigations correlated with this indicator."""
    correlation = indicator_service.correlate_indicator(db=db, indicator_id=indicator_id)
    return {
        "indicator_id": indicator_id,
        "total_investigations": correlation["total_correlated_investigations"],
        "investigations": correlation["investigations"],
    }


@router.get("/indicators/{indicator_id}/cases")
def get_indicator_correlated_cases(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve cases referencing this indicator via observations."""
    obs = (
        db.query(IndicatorObservation)
        .filter(IndicatorObservation.indicator_id == indicator_id, IndicatorObservation.case_id.is_not(None))
        .all()
    )
    case_ids = {o.case_id for o in obs if o.case_id}
    cases = db.query(Case).filter(Case.id.in_(case_ids)).all() if case_ids else []
    return {
        "indicator_id": indicator_id,
        "total_cases": len(cases),
        "cases": [
            {
                "id": c.id,
                "case_id": c.case_id,
                "title": c.title,
                "severity": c.severity,
                "status": c.status,
            }
            for c in cases
        ],
    }


@router.get("/indicators/{indicator_id}/relationships", response_model=list[IndicatorRelationshipResponse])
def get_indicator_relationships(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve outgoing structural relationships from this indicator."""
    return db.query(IndicatorRelationship).filter(IndicatorRelationship.source_indicator_id == indicator_id).all()


@router.post("/indicators/{indicator_id}/relationships", response_model=IndicatorRelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_indicator_relationship(
    indicator_id: int,
    payload: RelationshipCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Form a correlation relationship between two indicators."""
    return indicator_service.add_relationship(
        db=db,
        source_id=indicator_id,
        target_id=payload.target_indicator_id,
        rel_type=payload.relationship_type,
        description=payload.description,
        confidence=payload.confidence,
    )


@router.get("/indicators/{indicator_id}/timeline", response_model=list[IndicatorTimelineResponse])
def get_indicator_timeline(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve chronological timeline events for an indicator."""
    return db.query(IndicatorTimeline).filter(IndicatorTimeline.indicator_id == indicator_id).order_by(IndicatorTimeline.event_timestamp.asc()).all()


@router.get("/indicators/{indicator_id}/notes", response_model=list[IndicatorNoteResponse])
def get_indicator_notes(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve analyst notes attached to an indicator."""
    return db.query(IndicatorNote).filter(IndicatorNote.indicator_id == indicator_id).order_by(IndicatorNote.created_at.desc()).all()


@router.post("/indicators/{indicator_id}/notes", response_model=IndicatorNoteResponse, status_code=status.HTTP_201_CREATED)
def create_indicator_note(
    indicator_id: int,
    payload: IndicatorNoteCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Add a documented observation or analyst note to an indicator."""
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

    note = IndicatorNote(
        indicator_id=indicator_id,
        user_id=current_user.id,
        author_name=current_user.display_name or current_user.username,
        note=payload.note,
        created_at=datetime.now(timezone.utc),
    )
    db.add(note)

    # Timeline event
    tl = IndicatorTimeline(
        indicator_id=indicator_id,
        event_type="NOTE_ADDED",
        title="Analyst Note Added",
        description=f"Note by {note.author_name}: {payload.note[:80]}...",
        actor_name=note.author_name,
        event_timestamp=datetime.now(timezone.utc),
    )
    db.add(tl)
    db.commit()
    db.refresh(note)
    return note


@router.get("/indicators/{indicator_id}/graph", response_model=ThreatIntelGraphResponse)
def get_indicator_graph(
    indicator_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve network graph representing nodes (indicators, alerts, cases) and correlation links."""
    return indicator_service.get_indicator_graph(db=db, indicator_id=indicator_id)


# ---------------------------------------------------------------------------
# Search & Sources
# ---------------------------------------------------------------------------
@router.get("/search", response_model=list[IndicatorBriefResponse])
def search_threat_intel(
    db: DbSession,
    q: str = Query(..., min_length=1, description="Search query string"),
    indicator_type: str | None = Query(None, description="Optional type filter"),
    classification: str | None = Query(None, description="Optional classification filter"),
) -> Any:
    """Search indicators across values, normalized values, descriptions, and tags."""
    query = db.query(Indicator)

    search_filter = f"%{q.strip()}%"
    query = query.filter(
        or_(
            Indicator.value.ilike(search_filter),
            Indicator.normalized_value.ilike(search_filter),
            Indicator.display_value.ilike(search_filter),
            Indicator.description.ilike(search_filter),
            Indicator.tags.ilike(search_filter),
        )
    )

    if indicator_type:
        query = query.filter(Indicator.indicator_type == indicator_type.upper())
    if classification:
        query = query.filter(Indicator.classification == classification.upper())

    return query.limit(50).all()


@router.get("/sources", response_model=list[ThreatIntelSourceResponse])
def list_threat_intel_sources(
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve all configured threat intelligence origin feeds."""
    return db.query(ThreatIntelSource).all()


# ---------------------------------------------------------------------------
# Watchlist
# ---------------------------------------------------------------------------
@router.get("/watchlist", response_model=list[WatchlistResponse])
def get_watchlist(
    db: DbSession,
    current_user: CurrentUser,
    include_expired: bool = False,
) -> Any:
    """Retrieve indicators on the current user's active watchlist."""
    return watchlist_service.list_watchlist(db=db, user_id=current_user.id, include_expired=include_expired)


@router.post("/watchlist/{indicator_id}", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    indicator_id: int,
    payload: WatchlistCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Add an indicator to the current analyst's watchlist."""
    return watchlist_service.add_to_watchlist(
        db=db,
        indicator_id=indicator_id,
        user=current_user,
        reason=payload.reason,
        expires_at=payload.expires_at,
    )


@router.delete("/watchlist/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    watchlist_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Remove an indicator from the watchlist."""
    watchlist_service.remove_from_watchlist(db=db, watchlist_id=watchlist_id, user=current_user)


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------
@router.post("/import", response_model=ImportResponse)
async def import_indicators(
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),  # noqa: B008
) -> Any:
    """Safely import threat intelligence indicators from JSON, JSONL, or CSV file."""
    content = await file.read()
    filename = file.filename or "import.json"

    fmt = "json"
    if filename.endswith(".csv"):
        fmt = "csv"
    elif filename.endswith((".jsonl", ".ndjson")):
        fmt = "jsonl"

    return import_export_service.import_indicators(
        db=db,
        raw_content=content,
        file_format=fmt,
        actor=current_user,
    )


@router.get("/export")
def export_indicators(
    db: DbSession,
    current_user: CurrentUser,
    file_format: str = Query("json", description="csv or json"),
    classification: str | None = Query(None),
    indicator_type: str | None = Query(None),
) -> Response:
    """Export threat intelligence repository in sanitized CSV or JSON format."""
    content, media_type = import_export_service.export_indicators(
        db=db,
        file_format=file_format,
        classification=classification,
        indicator_type=indicator_type,
    )
    filename = f"threat_intel_export.{'csv' if file_format.lower() == 'csv' else 'json'}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------
@router.get("/challenges", response_model=list[ThreatIntelChallengeBriefResponse])
def list_challenges(
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """List available threat intelligence training challenges."""
    return challenge_service.list_challenges(db=db)


@router.get("/challenges/{slug}", response_model=ThreatIntelChallengeDetailResponse)
def get_challenge(
    slug: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve details for a specific threat intelligence investigation scenario."""
    return challenge_service.get_challenge_by_slug(db=db, slug=slug)


@router.post("/challenges/{slug}/submit", response_model=ChallengeAttemptResponse)
def submit_challenge_attempt(
    slug: str,
    payload: ChallengeSubmitRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Submit student hypothesis and conclusion for rubric evaluation."""
    return challenge_service.evaluate_attempt(
        db=db,
        slug=slug,
        user=current_user,
        selected_classification=payload.selected_classification,
        hypothesis_text=payload.hypothesis_text,
        evidence_notes=payload.evidence_notes,
        conclusion=payload.conclusion,
    )


@router.get("/challenges/{slug}/attempts", response_model=list[ChallengeAttemptResponse])
def get_challenge_attempts(
    slug: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve prior attempts submitted by current user for this challenge."""
    challenge = challenge_service.get_challenge_by_slug(db=db, slug=slug)
    return challenge_service.get_user_attempts(db=db, user_id=current_user.id, challenge_id=challenge.id)
