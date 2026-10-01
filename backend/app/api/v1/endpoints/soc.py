import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_

from app.api.deps import CurrentUser, DbSession
from app.models.detection import (
    AlertStatusHistory,
    DetectionAlert,
    DetectionRule,
    DetectionRun,
)
from app.models.pcap import ParsedPacket
from app.models.soc import (
    Case,
    Investigation,
    InvestigationAlert,
    SocAuditLog,
    SocChallenge,
)
from app.schemas.common import ModuleStatusResponse
from app.schemas.soc import (
    AlertAcknowledgeRequest,
    AlertBulkActionRequest,
    AlertClassificationRequest,
    CaseAlertAddRequest,
    CaseCreateRequest,
    CaseDetailResponse,
    CaseInvestigationAddRequest,
    CaseNoteCreateRequest,
    CaseUpdateRequest,
    CategoryCoverageItem,
    DetectionCoverageResponse,
    InvestigationAlertAddRequest,
    InvestigationBriefResponse,
    InvestigationCreateRequest,
    InvestigationDetailResponse,
    InvestigationEvidenceAddRequest,
    InvestigationEvidenceResponse,
    InvestigationFindingCreateRequest,
    InvestigationFindingResponse,
    InvestigationHypothesisCreateRequest,
    InvestigationHypothesisResponse,
    InvestigationHypothesisUpdateRequest,
    InvestigationNoteCreateRequest,
    InvestigationNoteResponse,
    InvestigationUpdateRequest,
    SocActivityItem,
    SocAlertDetailResponse,
    SocAlertItem,
    SocAuditLogResponse,
    SocChallengeDetailResponse,
    SocChallengeResponse,
    SocChallengeResultResponse,
    SocChallengeSubmitRequest,
    SocNotificationResponse,
    SocOverviewMetrics,
    SocOverviewResponse,
    SocStatisticsResponse,
    TrainingDatasetItem,
)
from app.services.soc.audit_service import soc_audit_service, soc_notification_service
from app.services.soc.case_service import case_service
from app.services.soc.challenge_service import challenge_service
from app.services.soc.correlation_service import correlation_service
from app.services.soc.investigation_service import investigation_service
from app.services.soc.network_context_service import network_context_service
from app.services.soc.prioritization_service import prioritization_service
from app.services.soc.timeline_service import timeline_service
from app.services.soc.training_dataset_service import training_dataset_service

router = APIRouter()


# ==============================================================================
# Backward Compatibility Endpoint
# ==============================================================================


@router.get("", response_model=ModuleStatusResponse)
@router.get("/", response_model=ModuleStatusResponse, include_in_schema=False)
async def get_soc_status() -> ModuleStatusResponse:
    """Return status and metadata for Mini SOC environment (backward compatibility)."""
    return ModuleStatusResponse(
        module="soc",
        status="planned",
        description="Hands-on Security Operations Center (SOC) simulator with real alert queues, triage workflows, and incident response.",
        planned_phase="Phase 5",
        capabilities=[
            "SIEM alert feed simulation (authentication bursts, C2 beacons, port scans)",
            "Incident timeline reconstruction",
            "Host and network artifact investigation",
            "Incident containment runbooks and post-incident reporting",
        ],
    )


# ==============================================================================
# SOC Overview & Statistics
# ==============================================================================


@router.get("/overview", response_model=SocOverviewResponse)
def get_soc_overview(db: DbSession, current_user: CurrentUser) -> SocOverviewResponse:
    """Retrieve high-level SOC dashboard metrics and recent telemetry."""
    total_alerts = db.query(DetectionAlert).count()
    new_alerts = db.query(DetectionAlert).filter(DetectionAlert.status == "NEW").count()
    ack_alerts = db.query(DetectionAlert).filter(DetectionAlert.status == "ACKNOWLEDGED").count()
    inv_alerts = db.query(DetectionAlert).filter(DetectionAlert.status == "INVESTIGATING").count()
    closed_alerts = db.query(DetectionAlert).filter(DetectionAlert.status == "CLOSED").count()
    fp_alerts = db.query(DetectionAlert).filter(DetectionAlert.status == "FALSE_POSITIVE").count()

    p1_alerts = db.query(DetectionAlert).filter(DetectionAlert.priority == "P1").count()
    p2_alerts = db.query(DetectionAlert).filter(DetectionAlert.priority == "P2").count()
    p3_alerts = db.query(DetectionAlert).filter(DetectionAlert.priority == "P3").count()
    p4_alerts = db.query(DetectionAlert).filter(DetectionAlert.priority == "P4").count()

    open_invs = db.query(Investigation).filter(Investigation.status.in_(["OPEN", "INVESTIGATING"])).count()
    active_cases = db.query(Case).filter(Case.status.in_(["OPEN", "INVESTIGATING"])).count()
    total_pkts = db.query(ParsedPacket).count()
    total_flows = total_pkts // 4 if total_pkts > 0 else 0
    active_rules = db.query(DetectionRule).filter(DetectionRule.status == "ENABLED").count()

    metrics = SocOverviewMetrics(
        total_alerts=total_alerts,
        new_alerts=new_alerts,
        acknowledged_alerts=ack_alerts,
        investigating_alerts=inv_alerts,
        closed_alerts=closed_alerts,
        false_positives=fp_alerts,
        p1_alerts=p1_alerts,
        p2_alerts=p2_alerts,
        p3_alerts=p3_alerts,
        p4_alerts=p4_alerts,
        open_investigations=open_invs,
        active_cases=active_cases,
        packets_analyzed_total=total_pkts,
        flows_analyzed_total=total_flows,
        active_rules_count=active_rules,
    )

    # Priority alerts (P1, P2)
    p_alerts = (
        db.query(DetectionAlert)
        .filter(DetectionAlert.priority.in_(["P1", "P2"]))
        .order_by(DetectionAlert.created_at.desc())
        .limit(5)
        .all()
    )
    priority_items = []
    for a in p_alerts:
        priority_items.append(
            SocAlertItem(
                id=a.id,
                run_id=a.run_id,
                rule_id=a.rule_id,
                rule_code=a.rule.rule_id if a.rule else None,
                capture_id=a.capture_id,
                title=a.title,
                category=a.category,
                severity=a.severity,
                confidence=a.confidence,
                status=a.status,
                classification=getattr(a, "classification", "UNREVIEWED"),
                priority=getattr(a, "priority", "P3"),
                source_ip=a.source_ip,
                source_port=a.source_port,
                destination_ip=a.destination_ip,
                destination_port=a.destination_port,
                protocol=a.protocol,
                first_seen_timestamp=a.first_seen_timestamp,
                last_seen_timestamp=a.last_seen_timestamp,
                packet_count=a.packet_count,
                evidence_count=len(a.evidence),
                created_at=a.created_at,
            )
        )

    # Recent runs
    recent_runs = []
    for r in db.query(DetectionRun).order_by(DetectionRun.created_at.desc()).limit(5).all():
        recent_runs.append({
            "id": r.id,
            "source_type": r.source_type,
            "status": r.status,
            "alerts_generated": r.alerts_generated,
            "packets_analyzed": r.rules_matched,
            "created_at": r.created_at.isoformat(),
        })

    # Recent investigations
    recent_invs = []
    for inv in db.query(Investigation).order_by(Investigation.created_at.desc()).limit(5).all():
        recent_invs.append(
            InvestigationBriefResponse(
                id=inv.id,
                investigation_id=inv.investigation_id,
                title=inv.title,
                status=inv.status,
                priority=inv.priority,
                classification=inv.classification,
                created_at=inv.created_at,
            )
        )

    # Dynamic learning recommendations based on active alert categories
    recs = []
    if db.query(DetectionAlert).filter(DetectionAlert.category == "TCP").first():
        recs.append({
            "title": "Review TCP Three-Way Handshake",
            "description": "Strengthen understanding of TCP SYN/RST dynamics and state tracking.",
            "route": "/learning/lessons/tcp-handshake-fundamentals",
        })
    if db.query(DetectionAlert).filter(DetectionAlert.category == "DNS").first():
        recs.append({
            "title": "Review DNS Resolution & NXDOMAIN",
            "description": "Learn how recursive resolvers handle nonexistent domain inquiries.",
            "route": "/learning/lessons/dns-resolution-process",
        })
    if db.query(DetectionAlert).filter(DetectionAlert.category == "ARP").first():
        recs.append({
            "title": "Review Layer 2 ARP Resolution",
            "description": "Understand MAC address discovery and cache conflict resolution.",
            "route": "/learning/lessons/arp-protocol-analysis",
        })
    if not recs:
        recs.append({
            "title": "Packet Analysis Fundamentals",
            "description": "Inspect 5-tuple conversations and packet dissecting principles.",
            "route": "/packet-analysis",
        })

    return SocOverviewResponse(
        metrics=metrics,
        priority_alerts=priority_items,
        recent_runs=recent_runs,
        recent_investigations=recent_invs,
        learning_recommendations=recs,
    )


@router.get("/statistics", response_model=SocStatisticsResponse)
def get_soc_statistics(db: DbSession, current_user: CurrentUser) -> SocStatisticsResponse:
    """Calculate statistical distributions and charts for the SOC environment."""
    alerts = db.query(DetectionAlert).all()

    by_sev: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    by_cat: dict[str, int] = {}
    by_pri: dict[str, int] = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    by_stat: dict[str, int] = {"NEW": 0, "ACKNOWLEDGED": 0, "INVESTIGATING": 0, "CLOSED": 0, "FALSE_POSITIVE": 0}
    by_class: dict[str, int] = {
        "UNREVIEWED": 0, "BENIGN": 0, "SUSPICIOUS": 0,
        "FALSE_POSITIVE": 0, "REQUIRES_MORE_DATA": 0, "CLOSED": 0,
    }
    by_proto: dict[str, int] = {}
    sources_count: dict[str, int] = {}
    dests_count: dict[str, int] = {}
    total_ev = 0

    for a in alerts:
        # Severity
        if a.severity in by_sev:
            by_sev[a.severity] += 1
        # Category
        by_cat[a.category] = by_cat.get(a.category, 0) + 1
        # Priority
        p = getattr(a, "priority", "P3")
        by_pri[p] = by_pri.get(p, 0) + 1
        # Status
        by_stat[a.status] = by_stat.get(a.status, 0) + 1
        # Classification
        cl = getattr(a, "classification", "UNREVIEWED")
        by_class[cl] = by_class.get(cl, 0) + 1
        # Protocol
        proto = a.protocol or "OTHER"
        by_proto[proto] = by_proto.get(proto, 0) + 1
        # Source & Destination
        if a.source_ip:
            sources_count[a.source_ip] = sources_count.get(a.source_ip, 0) + 1
        if a.destination_ip:
            dests_count[a.destination_ip] = dests_count.get(a.destination_ip, 0) + 1
        total_ev += len(a.evidence)

    top_sources = [
        {"ip": ip, "count": cnt}
        for ip, cnt in sorted(sources_count.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    top_dests = [
        {"ip": ip, "count": cnt}
        for ip, cnt in sorted(dests_count.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    avg_ev = round(total_ev / len(alerts), 1) if alerts else 0.0

    # Trend over time (last 7 days bucketed by date)
    trend: list[dict[str, Any]] = []
    # Simple day grouping for alerts
    day_counts: dict[str, int] = {}
    for a in alerts:
        d_str = a.created_at.strftime("%Y-%m-%d")
        day_counts[d_str] = day_counts.get(d_str, 0) + 1

    for d_str in sorted(day_counts.keys()):
        trend.append({"date": d_str, "alerts": day_counts[d_str]})

    return SocStatisticsResponse(
        alerts_by_severity=by_sev,
        alerts_by_category=by_cat,
        alerts_by_priority=by_pri,
        alerts_by_status=by_stat,
        alerts_by_classification=by_class,
        alerts_by_protocol=by_proto,
        top_sources=top_sources,
        top_destinations=top_dests,
        average_evidence_count=avg_ev,
        average_investigation_duration_minutes=15.0,
        trend_over_time=trend,
    )


@router.get("/activity", response_model=list[SocActivityItem])
def get_soc_activity(db: DbSession, current_user: CurrentUser) -> list[SocActivityItem]:
    """Retrieve consolidated SOC timeline activity stream."""
    items: list[SocActivityItem] = []

    # 1. Recent Audit Logs
    audit_logs = db.query(SocAuditLog).order_by(SocAuditLog.created_at.desc()).limit(20).all()
    for al in audit_logs:
        items.append(
            SocActivityItem(
                id=f"audit-{al.id}",
                activity_type=al.action,
                title=f"{al.actor_name}: {al.action.replace('_', ' ').title()}",
                description=f"Action on {al.object_type} #{al.object_id}",
                timestamp=al.created_at,
                reference_type=al.object_type,
                reference_id=al.object_id,
                actor_name=al.actor_name,
            )
        )

    # 2. Recent Detection Runs
    runs = db.query(DetectionRun).order_by(DetectionRun.created_at.desc()).limit(10).all()
    for r in runs:
        items.append(
            SocActivityItem(
                id=f"run-{r.id}",
                activity_type="DETECTION_RUN",
                title=f"Detection Run #{r.id} Completed",
                description=f"Generated {r.alerts_generated} alerts over {r.source_type} capture.",
                timestamp=r.created_at,
                reference_type="RUN",
                reference_id=str(r.id),
                actor_name="Detection Engine",
            )
        )

    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items[:30]


# ==============================================================================
# Alert Queue & Details Endpoints
# ==============================================================================


@router.get("/alerts", response_model=list[SocAlertItem])
def list_soc_alerts(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = None,
    severity: str | None = None,
    priority: str | None = None,
    status_val: str | None = Query(None, alias="status"),
    classification: str | None = None,
    category: str | None = None,
    protocol: str | None = None,
    source_ip: str | None = None,
    destination_ip: str | None = None,
    capture_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[SocAlertItem]:
    """List alerts in the main analyst queue with comprehensive filtering and search."""
    query = db.query(DetectionAlert)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                DetectionAlert.title.ilike(search_pattern),
                DetectionAlert.source_ip.ilike(search_pattern),
                DetectionAlert.destination_ip.ilike(search_pattern),
                DetectionAlert.dedup_key.ilike(search_pattern),
                DetectionAlert.protocol.ilike(search_pattern),
            )
        )

    if severity:
        query = query.filter(DetectionAlert.severity == severity.upper())
    if priority:
        query = query.filter(DetectionAlert.priority == priority.upper())
    if status_val:
        query = query.filter(DetectionAlert.status == status_val.upper())
    if classification:
        query = query.filter(DetectionAlert.classification == classification.upper())
    if category:
        query = query.filter(DetectionAlert.category == category.upper())
    if protocol:
        query = query.filter(DetectionAlert.protocol == protocol.upper())
    if source_ip:
        query = query.filter(DetectionAlert.source_ip == source_ip.strip())
    if destination_ip:
        query = query.filter(DetectionAlert.destination_ip == destination_ip.strip())
    if capture_id:
        query = query.filter(DetectionAlert.capture_id == capture_id)

    alerts = query.order_by(DetectionAlert.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for a in alerts:
        # Calculate dynamic priority reason
        pri, pri_reason = prioritization_service.calculate_priority(
            severity=a.severity,
            confidence=a.confidence,
            evidence_count=len(a.evidence),
            packet_count=a.packet_count,
        )
        # Update priority if not set or synchronized
        if not a.priority or a.priority != pri.value:
            a.priority = pri.value

        assigned_name = a.assigned_to.display_name if a.assigned_to else None

        result.append(
            SocAlertItem(
                id=a.id,
                run_id=a.run_id,
                rule_id=a.rule_id,
                rule_code=a.rule.rule_id if a.rule else None,
                capture_id=a.capture_id,
                title=a.title,
                category=a.category,
                severity=a.severity,
                confidence=a.confidence,
                status=a.status,
                classification=getattr(a, "classification", "UNREVIEWED"),
                priority=a.priority,
                priority_reason=pri_reason,
                assigned_to_id=a.assigned_to_id,
                assigned_to_name=assigned_name,
                source_ip=a.source_ip,
                source_port=a.source_port,
                destination_ip=a.destination_ip,
                destination_port=a.destination_port,
                protocol=a.protocol,
                first_seen_timestamp=a.first_seen_timestamp,
                last_seen_timestamp=a.last_seen_timestamp,
                packet_count=a.packet_count,
                evidence_count=len(a.evidence),
                created_at=a.created_at,
            )
        )
    return result


@router.get("/alerts/{alert_id}", response_model=SocAlertDetailResponse)
def get_soc_alert_detail(alert_id: int, db: DbSession, current_user: CurrentUser) -> SocAlertDetailResponse:
    """Retrieve complete alert details including evidence, timeline, related alerts, and context."""
    alert = db.query(DetectionAlert).filter(DetectionAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert #{alert_id} not found.")

    # Calculate explainable priority
    pri, pri_reason = prioritization_service.calculate_priority(
        severity=alert.severity,
        confidence=alert.confidence,
        evidence_count=len(alert.evidence),
        packet_count=alert.packet_count,
    )
    if not alert.priority or alert.priority != pri.value:
        alert.priority = pri.value
        db.commit()

    # Evidence mapping
    evidence_list = []
    for ev in alert.evidence:
        payload = None
        if ev.evidence_data:
            try:
                payload = json.loads(ev.evidence_data)
            except (ValueError, TypeError, json.JSONDecodeError):
                payload = None
        evidence_list.append({
            "id": ev.id,
            "evidence_type": ev.evidence_type,
            "packet_id": ev.packet_id,
            "packet_number": ev.packet_number,
            "timestamp": ev.timestamp,
            "summary": ev.description,
            "evidence_payload": payload,
            "created_at": ev.created_at.isoformat(),
        })

    # Notes
    notes_list = [
        {
            "id": n.id,
            "author_name": n.user.display_name if n.user else "Analyst",
            "note": n.note,
            "created_at": n.created_at.isoformat(),
        }
        for n in alert.notes
    ]

    # Status history
    hist_list = [
        {
            "id": h.id,
            "old_status": h.previous_status,
            "new_status": h.new_status,
            "reason": h.reason,
            "created_at": h.created_at.isoformat(),
        }
        for h in alert.status_history
    ]

    # Reconstruct timeline
    timeline_events = timeline_service.build_alert_timeline(alert)

    # Correlated related alerts
    related = correlation_service.find_related_alerts(db, alert, limit=5)

    # Flow / endpoint network context
    net_ctx = network_context_service.get_flow_context(
        db,
        capture_id=alert.capture_id,
        source_ip=alert.source_ip,
        destination_ip=alert.destination_ip,
    )

    # Linked investigations
    inv_links = []
    for ia in db.query(InvestigationAlert).filter(InvestigationAlert.alert_id == alert.id).all():
        inv = ia.investigation
        if inv:
            inv_links.append(
                InvestigationBriefResponse(
                    id=inv.id,
                    investigation_id=inv.investigation_id,
                    title=inv.title,
                    status=inv.status,
                    priority=inv.priority,
                    classification=inv.classification,
                    created_at=inv.created_at,
                )
            )

    investigation_steps = []
    if alert.investigation_steps:
        try:
            investigation_steps = json.loads(alert.investigation_steps)
        except (ValueError, TypeError, json.JSONDecodeError):
            investigation_steps = [alert.investigation_steps]

    return SocAlertDetailResponse(
        id=alert.id,
        run_id=alert.run_id,
        rule_id=alert.rule_id,
        rule_code=alert.rule.rule_id if alert.rule else None,
        capture_id=alert.capture_id,
        title=alert.title,
        category=alert.category,
        severity=alert.severity,
        confidence=alert.confidence,
        status=alert.status,
        classification=getattr(alert, "classification", "UNREVIEWED"),
        priority=alert.priority,
        priority_reason=pri_reason,
        assigned_to_id=alert.assigned_to_id,
        assigned_to_name=alert.assigned_to.display_name if alert.assigned_to else None,
        source_ip=alert.source_ip,
        source_port=alert.source_port,
        destination_ip=alert.destination_ip,
        destination_port=alert.destination_port,
        protocol=alert.protocol,
        first_seen_timestamp=alert.first_seen_timestamp,
        last_seen_timestamp=alert.last_seen_timestamp,
        packet_count=alert.packet_count,
        evidence_count=len(alert.evidence),
        created_at=alert.created_at,
        explanation=alert.explanation,
        mitre_attack_id=alert.mitre_attack_id,
        mitre_technique=alert.mitre_technique,
        investigation_steps=investigation_steps,
        rule_description=alert.rule.description if alert.rule else None,
        evidence=evidence_list,
        notes=notes_list,
        status_history=hist_list,
        timeline=timeline_events,
        related_alerts=related,
        network_context=net_ctx,
        investigations=inv_links,
    )


@router.post("/alerts/{alert_id}/acknowledge", response_model=SocAlertItem)
def acknowledge_alert(
    alert_id: int,
    payload: AlertAcknowledgeRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> SocAlertItem:
    """Acknowledge an alert to mark it queued for analyst inspection."""
    alert = db.query(DetectionAlert).filter(DetectionAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

    old_status = alert.status
    alert.status = "ACKNOWLEDGED"
    alert.assigned_to_id = current_user.id

    # Record history
    hist = AlertStatusHistory(
        alert_id=alert.id,
        user_id=current_user.id,
        previous_status=old_status,
        new_status="ACKNOWLEDGED",
        reason=payload.reason or "Acknowledged by analyst.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(hist)
    db.commit()
    db.refresh(alert)

    soc_audit_service.log_action(
        db,
        actor=current_user,
        action="ACKNOWLEDGE_ALERT",
        object_type="ALERT",
        object_id=alert.id,
        details={"reason": payload.reason},
    )

    return SocAlertItem(
        id=alert.id,
        run_id=alert.run_id,
        rule_id=alert.rule_id,
        rule_code=alert.rule.rule_id if alert.rule else None,
        capture_id=alert.capture_id,
        title=alert.title,
        category=alert.category,
        severity=alert.severity,
        confidence=alert.confidence,
        status=alert.status,
        classification=getattr(alert, "classification", "UNREVIEWED"),
        priority=getattr(alert, "priority", "P3"),
        assigned_to_id=alert.assigned_to_id,
        assigned_to_name=current_user.display_name,
        source_ip=alert.source_ip,
        source_port=alert.source_port,
        destination_ip=alert.destination_ip,
        destination_port=alert.destination_port,
        protocol=alert.protocol,
        first_seen_timestamp=alert.first_seen_timestamp,
        last_seen_timestamp=alert.last_seen_timestamp,
        packet_count=alert.packet_count,
        evidence_count=len(alert.evidence),
        created_at=alert.created_at,
    )


@router.patch("/alerts/{alert_id}/classification", response_model=SocAlertItem)
def update_alert_classification(
    alert_id: int,
    payload: AlertClassificationRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> SocAlertItem:
    """Record an analyst classification decision (BENIGN, SUSPICIOUS, FALSE_POSITIVE, etc.)."""
    alert = db.query(DetectionAlert).filter(DetectionAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

    class_val = payload.classification.value if hasattr(payload.classification, "value") else str(payload.classification)
    alert.classification = class_val

    # If classification is FALSE_POSITIVE or CLOSED, update status accordingly
    old_status = alert.status
    if payload.status:
        alert.status = payload.status.value if hasattr(payload.status, "value") else str(payload.status)
    elif class_val == "FALSE_POSITIVE":
        alert.status = "FALSE_POSITIVE"
    elif class_val in ("CLOSED", "BENIGN"):
        alert.status = "CLOSED"

    # Audit history
    hist = AlertStatusHistory(
        alert_id=alert.id,
        user_id=current_user.id,
        previous_status=old_status,
        new_status=alert.status,
        reason=f"Classification set to {class_val}: {payload.reason}",
        created_at=datetime.now(timezone.utc),
    )
    db.add(hist)
    db.commit()
    db.refresh(alert)

    soc_audit_service.log_action(
        db,
        actor=current_user,
        action="CLASSIFY_ALERT",
        object_type="ALERT",
        object_id=alert.id,
        details={"classification": class_val, "reason": payload.reason},
    )

    return SocAlertItem(
        id=alert.id,
        run_id=alert.run_id,
        rule_id=alert.rule_id,
        rule_code=alert.rule.rule_id if alert.rule else None,
        capture_id=alert.capture_id,
        title=alert.title,
        category=alert.category,
        severity=alert.severity,
        confidence=alert.confidence,
        status=alert.status,
        classification=alert.classification,
        priority=getattr(alert, "priority", "P3"),
        assigned_to_id=alert.assigned_to_id,
        assigned_to_name=alert.assigned_to.display_name if alert.assigned_to else None,
        source_ip=alert.source_ip,
        source_port=alert.source_port,
        destination_ip=alert.destination_ip,
        destination_port=alert.destination_port,
        protocol=alert.protocol,
        first_seen_timestamp=alert.first_seen_timestamp,
        last_seen_timestamp=alert.last_seen_timestamp,
        packet_count=alert.packet_count,
        evidence_count=len(alert.evidence),
        created_at=alert.created_at,
    )


@router.post("/alerts/bulk-action")
def bulk_alert_action(
    payload: AlertBulkActionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Execute safe bulk operations across multiple alerts."""
    alerts = db.query(DetectionAlert).filter(DetectionAlert.id.in_(payload.alert_ids)).all()
    count = 0

    action = payload.action.upper()
    for a in alerts:
        if action == "ACKNOWLEDGE":
            a.status = "ACKNOWLEDGED"
            a.assigned_to_id = current_user.id
            count += 1
        elif action == "ASSIGN" and payload.assigned_to_id is not None:
            a.assigned_to_id = payload.assigned_to_id
            count += 1
        elif action == "CLOSE":
            a.status = "CLOSED"
            a.classification = "CLOSED"
            count += 1
        elif action == "SET_CLASSIFICATION" and payload.classification:
            cl_val = payload.classification.value if hasattr(payload.classification, "value") else str(payload.classification)
            a.classification = cl_val
            if payload.status:
                a.status = payload.status.value if hasattr(payload.status, "value") else str(payload.status)
            count += 1

    db.commit()

    soc_audit_service.log_action(
        db,
        actor=current_user,
        action=f"BULK_{action}",
        object_type="ALERT_BATCH",
        object_id=f"count:{count}",
        details={"alert_ids": payload.alert_ids, "action": action, "reason": payload.reason},
    )

    return {"status": "SUCCESS", "action": action, "affected_alerts": count}


# ==============================================================================
# Investigation Endpoints
# ==============================================================================


@router.get("/investigations", response_model=list[InvestigationBriefResponse])
def list_investigations(
    db: DbSession,
    current_user: CurrentUser,
    status_val: str | None = Query(None, alias="status"),
    priority: str | None = None,
    limit: int = 50,
) -> list[InvestigationBriefResponse]:
    """List investigations with optional status and priority filtering."""
    q = db.query(Investigation)
    if status_val:
        q = q.filter(Investigation.status == status_val.upper())
    if priority:
        q = q.filter(Investigation.priority == priority.upper())
    invs = q.order_by(Investigation.created_at.desc()).limit(limit).all()
    return invs


@router.post("/investigations", response_model=InvestigationDetailResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(
    payload: InvestigationCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationDetailResponse:
    """Create a new investigation."""
    inv = investigation_service.create_investigation(
        db=db,
        creator=current_user,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        alert_ids=payload.alert_ids,
        case_id=payload.case_id,
    )
    return get_investigation_detail(inv.id, db, current_user)


@router.get("/investigations/{investigation_id}", response_model=InvestigationDetailResponse)
def get_investigation_detail(
    investigation_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationDetailResponse:
    """Get full details of an ongoing investigation."""
    inv = investigation_service.get_investigation(db, investigation_id)

    # Alerts
    alerts = []
    for ia in inv.alerts:
        a = ia.alert
        if a:
            alerts.append(
                SocAlertItem(
                    id=a.id,
                    run_id=a.run_id,
                    rule_id=a.rule_id,
                    rule_code=a.rule.rule_id if a.rule else None,
                    capture_id=a.capture_id,
                    title=a.title,
                    category=a.category,
                    severity=a.severity,
                    confidence=a.confidence,
                    status=a.status,
                    classification=getattr(a, "classification", "UNREVIEWED"),
                    priority=getattr(a, "priority", "P3"),
                    source_ip=a.source_ip,
                    source_port=a.source_port,
                    destination_ip=a.destination_ip,
                    destination_port=a.destination_port,
                    protocol=a.protocol,
                    first_seen_timestamp=a.first_seen_timestamp,
                    last_seen_timestamp=a.last_seen_timestamp,
                    packet_count=a.packet_count,
                    evidence_count=len(a.evidence),
                    created_at=a.created_at,
                )
            )

    # Hypotheses
    import json
    hyps = []
    for h in inv.hypotheses:
        ev_ids = []
        if h.supporting_evidence_ids:
            try:
                ev_ids = json.loads(h.supporting_evidence_ids)
            except (ValueError, TypeError, json.JSONDecodeError):
                ev_ids = []
        hyps.append(
            InvestigationHypothesisResponse(
                id=h.id,
                investigation_id=h.investigation_id,
                hypothesis_text=h.hypothesis_text,
                status=h.status,
                reasoning=h.reasoning,
                supporting_evidence_ids=ev_ids,
                created_by_name=h.created_by.display_name if h.created_by else None,
                created_at=h.created_at,
                updated_at=h.updated_at,
            )
        )

    # Findings
    findings = [
        InvestigationFindingResponse(
            id=f.id,
            investigation_id=f.investigation_id,
            title=f.title,
            description=f.description,
            evidence_summary=f.evidence_summary,
            confidence=f.confidence,
            created_by_name=f.created_by.display_name if f.created_by else None,
            created_at=f.created_at,
        )
        for f in inv.findings
    ]

    # Evidence
    evidence = []
    for e in inv.evidence:
        payload_data = None
        if e.evidence_data:
            try:
                payload_data = json.loads(e.evidence_data)
            except (ValueError, TypeError, json.JSONDecodeError):
                payload_data = None
        evidence.append(
            InvestigationEvidenceResponse(
                id=e.id,
                investigation_id=e.investigation_id,
                evidence_type=e.evidence_type,
                reference_id=e.reference_id,
                capture_id=e.capture_id,
                packet_number=e.packet_number,
                description=e.description,
                evidence_data=payload_data,
                created_at=e.created_at,
            )
        )

    # Notes
    notes = [
        InvestigationNoteResponse(
            id=n.id,
            investigation_id=n.investigation_id,
            user_id=n.user_id,
            author_name=n.user.display_name if n.user else None,
            note=n.note,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )
        for n in inv.notes
    ]

    # Cases
    case_refs = [
        {"case_id": ci.case.case_id, "title": ci.case.title, "status": ci.case.status}
        for ci in inv.case_investigations
        if ci.case
    ]

    return InvestigationDetailResponse(
        id=inv.id,
        investigation_id=inv.investigation_id,
        title=inv.title,
        description=inv.description,
        status=inv.status,
        priority=inv.priority,
        classification=inv.classification,
        created_by_id=inv.created_by_id,
        created_by_name=inv.created_by.display_name if inv.created_by else None,
        assigned_to_id=inv.assigned_to_id,
        assigned_to_name=inv.assigned_to.display_name if inv.assigned_to else None,
        started_at=inv.started_at,
        closed_at=inv.closed_at,
        conclusion=inv.conclusion,
        recommendations=inv.recommendations,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        alerts=alerts,
        evidence=evidence,
        hypotheses=hyps,
        findings=findings,
        notes=notes,
        cases=case_refs,
    )


@router.patch("/investigations/{investigation_id}", response_model=InvestigationDetailResponse)
def update_investigation(
    investigation_id: int,
    payload: InvestigationUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationDetailResponse:
    """Update investigation metadata or status."""
    investigation_service.update_investigation(
        db=db,
        actor=current_user,
        investigation_id=investigation_id,
        title=payload.title,
        description=payload.description,
        status_val=payload.status,
        priority=payload.priority,
        classification=payload.classification,
        conclusion=payload.conclusion,
        recommendations=payload.recommendations,
        assigned_to_id=payload.assigned_to_id,
    )
    return get_investigation_detail(investigation_id, db, current_user)


@router.post("/investigations/{investigation_id}/alerts")
def add_alert_to_investigation(
    investigation_id: int,
    payload: InvestigationAlertAddRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Associate an alert with an ongoing investigation."""
    ia = investigation_service.add_alert(
        db=db,
        actor=current_user,
        investigation_id=investigation_id,
        alert_id=payload.alert_id,
        relationship_type=payload.relationship_type,
    )
    return {"status": "SUCCESS", "investigation_id": ia.investigation_id, "alert_id": ia.alert_id}


@router.post("/investigations/{investigation_id}/evidence")
def add_evidence_to_investigation(
    investigation_id: int,
    payload: InvestigationEvidenceAddRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Attach evidence artifact reference to investigation."""
    ev = investigation_service.add_evidence(
        db=db,
        actor=current_user,
        investigation_id=investigation_id,
        evidence_type=payload.evidence_type,
        description=payload.description,
        reference_id=payload.reference_id,
        capture_id=payload.capture_id,
        packet_number=payload.packet_number,
        evidence_data=payload.evidence_data,
    )
    return {"status": "SUCCESS", "id": ev.id, "type": ev.evidence_type}


@router.post("/investigations/{investigation_id}/hypotheses", response_model=InvestigationHypothesisResponse)
def create_hypothesis(
    investigation_id: int,
    payload: InvestigationHypothesisCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationHypothesisResponse:
    """Formulate an investigative hypothesis."""
    hyp = investigation_service.create_hypothesis(
        db=db,
        actor=current_user,
        investigation_id=investigation_id,
        hypothesis_text=payload.hypothesis_text,
        status_val=payload.status,
        reasoning=payload.reasoning,
        supporting_evidence_ids=payload.supporting_evidence_ids,
    )
    return InvestigationHypothesisResponse(
        id=hyp.id,
        investigation_id=hyp.investigation_id,
        hypothesis_text=hyp.hypothesis_text,
        status=hyp.status,
        reasoning=hyp.reasoning,
        supporting_evidence_ids=payload.supporting_evidence_ids,
        created_by_name=current_user.display_name,
        created_at=hyp.created_at,
        updated_at=hyp.updated_at,
    )


@router.patch("/investigations/{investigation_id}/hypotheses/{hypothesis_id}", response_model=InvestigationHypothesisResponse)
def update_hypothesis(
    investigation_id: int,
    hypothesis_id: int,
    payload: InvestigationHypothesisUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationHypothesisResponse:
    """Update hypothesis testing status or evidence reasoning."""
    hyp = investigation_service.update_hypothesis(
        db=db,
        actor=current_user,
        hypothesis_id=hypothesis_id,
        status_val=payload.status,
        reasoning=payload.reasoning,
        supporting_evidence_ids=payload.supporting_evidence_ids,
    )
    import json
    ev_ids = []
    if hyp.supporting_evidence_ids:
        try:
            ev_ids = json.loads(hyp.supporting_evidence_ids)
        except (ValueError, TypeError, json.JSONDecodeError):
            ev_ids = []
    return InvestigationHypothesisResponse(
        id=hyp.id,
        investigation_id=hyp.investigation_id,
        hypothesis_text=hyp.hypothesis_text,
        status=hyp.status,
        reasoning=hyp.reasoning,
        supporting_evidence_ids=ev_ids,
        created_by_name=current_user.display_name,
        created_at=hyp.created_at,
        updated_at=hyp.updated_at,
    )


@router.post("/investigations/{investigation_id}/findings", response_model=InvestigationFindingResponse)
def create_finding(
    investigation_id: int,
    payload: InvestigationFindingCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationFindingResponse:
    """Log a validated finding."""
    finding = investigation_service.create_finding(
        db=db,
        actor=current_user,
        investigation_id=investigation_id,
        title=payload.title,
        description=payload.description,
        evidence_summary=payload.evidence_summary,
        confidence=payload.confidence,
    )
    return InvestigationFindingResponse(
        id=finding.id,
        investigation_id=finding.investigation_id,
        title=finding.title,
        description=finding.description,
        evidence_summary=finding.evidence_summary,
        confidence=finding.confidence,
        created_by_name=current_user.display_name,
        created_at=finding.created_at,
    )


@router.post("/investigations/{investigation_id}/notes", response_model=InvestigationNoteResponse)
def add_investigation_note(
    investigation_id: int,
    payload: InvestigationNoteCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> InvestigationNoteResponse:
    """Add analyst notes to an investigation."""
    note = investigation_service.add_note(
        db=db,
        actor=current_user,
        investigation_id=investigation_id,
        note_text=payload.note,
    )
    return InvestigationNoteResponse(
        id=note.id,
        investigation_id=note.investigation_id,
        user_id=note.user_id,
        author_name=current_user.display_name,
        note=note.note,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get("/investigations/{investigation_id}/report")
def export_investigation_report(
    investigation_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Generate and export a formal JSON forensic report."""
    return investigation_service.generate_report(db, investigation_id)


# ==============================================================================
# Case Management Endpoints
# ==============================================================================


@router.get("/cases")
def list_cases(
    db: DbSession,
    current_user: CurrentUser,
    status_val: str | None = Query(None, alias="status"),
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List high-level cases."""
    q = db.query(Case)
    if status_val:
        q = q.filter(Case.status == status_val.upper())
    cases = q.order_by(Case.created_at.desc()).limit(limit).all()
    return [
        {
            "id": c.id,
            "case_id": c.case_id,
            "title": c.title,
            "status": c.status,
            "priority": c.priority,
            "alerts_count": len(c.alerts),
            "investigations_count": len(c.investigations),
            "created_at": c.created_at.isoformat(),
        }
        for c in cases
    ]


@router.post("/cases", status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Create a new case."""
    case = case_service.create_case(
        db=db,
        creator=current_user,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        alert_ids=payload.alert_ids,
        investigation_ids=payload.investigation_ids,
    )
    return {"id": case.id, "case_id": case.case_id, "title": case.title, "status": case.status}


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
def get_case_detail(
    case_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> CaseDetailResponse:
    """Retrieve detailed case information."""
    case = case_service.get_case(db, case_id)

    alerts = []
    for ca in case.alerts:
        a = ca.alert
        if a:
            alerts.append(
                SocAlertItem(
                    id=a.id,
                    run_id=a.run_id,
                    rule_id=a.rule_id,
                    rule_code=a.rule.rule_id if a.rule else None,
                    capture_id=a.capture_id,
                    title=a.title,
                    category=a.category,
                    severity=a.severity,
                    confidence=a.confidence,
                    status=a.status,
                    classification=getattr(a, "classification", "UNREVIEWED"),
                    priority=getattr(a, "priority", "P3"),
                    source_ip=a.source_ip,
                    source_port=a.source_port,
                    destination_ip=a.destination_ip,
                    destination_port=a.destination_port,
                    protocol=a.protocol,
                    first_seen_timestamp=a.first_seen_timestamp,
                    last_seen_timestamp=a.last_seen_timestamp,
                    packet_count=a.packet_count,
                    evidence_count=len(a.evidence),
                    created_at=a.created_at,
                )
            )

    invs = [
        InvestigationBriefResponse(
            id=ci.investigation.id,
            investigation_id=ci.investigation.investigation_id,
            title=ci.investigation.title,
            status=ci.investigation.status,
            priority=ci.investigation.priority,
            classification=ci.investigation.classification,
            created_at=ci.investigation.created_at,
        )
        for ci in case.investigations
        if ci.investigation
    ]

    notes = [
        {
            "id": n.id,
            "author_name": n.user.display_name if n.user else "Analyst",
            "note": n.note,
            "created_at": n.created_at.isoformat(),
        }
        for n in case.notes
    ]

    return CaseDetailResponse(
        id=case.id,
        case_id=case.case_id,
        title=case.title,
        description=case.description,
        status=case.status,
        priority=case.priority,
        created_by_name=case.created_by.display_name if case.created_by else None,
        assigned_to_name=case.assigned_to.display_name if case.assigned_to else None,
        summary=case.summary,
        closed_at=case.closed_at,
        created_at=case.created_at,
        updated_at=case.updated_at,
        alerts=alerts,
        investigations=invs,
        notes=notes,
    )


@router.patch("/cases/{case_id}", response_model=CaseDetailResponse)
def update_case(
    case_id: int,
    payload: CaseUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> CaseDetailResponse:
    """Update case metadata or status."""
    case_service.update_case(
        db=db,
        actor=current_user,
        case_id=case_id,
        title=payload.title,
        description=payload.description,
        status_val=payload.status,
        priority=payload.priority,
        summary=payload.summary,
        assigned_to_id=payload.assigned_to_id,
    )
    return get_case_detail(case_id, db, current_user)


@router.post("/cases/{case_id}/alerts")
def add_alert_to_case(
    case_id: int,
    payload: CaseAlertAddRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Link an alert to a case."""
    ca = case_service.add_alert(db, current_user, case_id, payload.alert_id)
    return {"status": "SUCCESS", "case_id": ca.case_id, "alert_id": ca.alert_id}


@router.post("/cases/{case_id}/investigations")
def add_investigation_to_case(
    case_id: int,
    payload: CaseInvestigationAddRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Link an investigation to a case."""
    ci = case_service.add_investigation(db, current_user, case_id, payload.investigation_id)
    return {"status": "SUCCESS", "case_id": ci.case_id, "investigation_id": ci.investigation_id}


@router.post("/cases/{case_id}/notes")
def add_case_note(
    case_id: int,
    payload: CaseNoteCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Add executive note to a case."""
    note = case_service.add_note(db, current_user, case_id, payload.note)
    return {"status": "SUCCESS", "id": note.id, "created_at": note.created_at.isoformat()}


# ==============================================================================
# Detection Coverage & Challenges
# ==============================================================================


@router.get("/detection-coverage", response_model=DetectionCoverageResponse)
def get_detection_coverage(db: DbSession, current_user: CurrentUser) -> DetectionCoverageResponse:
    """Retrieve educational detection rule coverage across protocol domains."""
    rules = db.query(DetectionRule).all()
    categories_map: dict[str, list[DetectionRule]] = {}
    for r in rules:
        categories_map.setdefault(r.category, []).append(r)

    items: list[CategoryCoverageItem] = []
    for cat, r_list in categories_map.items():
        sev_counts: dict[str, int] = {}
        techniques = set()
        active = 0
        for r in r_list:
            if r.status == "ENABLED":
                active += 1
            sev_counts[r.severity] = sev_counts.get(r.severity, 0) + 1
            if r.mitre_attack_id:
                techniques.add(f"{r.mitre_attack_id} ({r.mitre_technique or 'Technique'})")

        items.append(
            CategoryCoverageItem(
                category=cat,
                total_rules=len(r_list),
                active_rules=active,
                severity_distribution=sev_counts,
                mitre_techniques=sorted(techniques),
            )
        )

    items.sort(key=lambda x: x.total_rules, reverse=True)
    return DetectionCoverageResponse(
        categories=items,
        total_rules=len(rules),
        active_rules=sum(1 for r in rules if r.status == "ENABLED"),
    )


@router.get("/challenges", response_model=list[SocChallengeResponse])
def list_soc_challenges(db: DbSession, current_user: CurrentUser) -> list[SocChallengeResponse]:
    """List educational SOC scenario challenges."""
    return db.query(SocChallenge).order_by(SocChallenge.id.asc()).all()


@router.get("/challenges/{challenge_id}", response_model=SocChallengeDetailResponse)
def get_soc_challenge(challenge_id: int, db: DbSession, current_user: CurrentUser) -> SocChallengeDetailResponse:
    """Retrieve detailed instructions and telemetry references for a challenge."""
    ch = db.query(SocChallenge).filter(SocChallenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found.")

    expected_obs = []
    if ch.expected_observations:
        try:
            expected_obs = json.loads(ch.expected_observations)
        except (ValueError, TypeError, json.JSONDecodeError):
            expected_obs = []

    # Get sample alerts associated with the capture
    sample_alerts = []
    if ch.capture_id:
        alerts = db.query(DetectionAlert).filter(DetectionAlert.capture_id == ch.capture_id).limit(5).all()
        for a in alerts:
            sample_alerts.append(
                SocAlertItem(
                    id=a.id,
                    run_id=a.run_id,
                    rule_id=a.rule_id,
                    rule_code=a.rule.rule_id if a.rule else None,
                    capture_id=a.capture_id,
                    title=a.title,
                    category=a.category,
                    severity=a.severity,
                    confidence=a.confidence,
                    status=a.status,
                    classification=getattr(a, "classification", "UNREVIEWED"),
                    priority=getattr(a, "priority", "P3"),
                    source_ip=a.source_ip,
                    source_port=a.source_port,
                    destination_ip=a.destination_ip,
                    destination_port=a.destination_port,
                    protocol=a.protocol,
                    first_seen_timestamp=a.first_seen_timestamp,
                    last_seen_timestamp=a.last_seen_timestamp,
                    packet_count=a.packet_count,
                    evidence_count=len(a.evidence),
                    created_at=a.created_at,
                )
            )

    return SocChallengeDetailResponse(
        id=ch.id,
        slug=ch.slug,
        title=ch.title,
        description=ch.description,
        scenario_type=ch.scenario_type,
        difficulty=ch.difficulty,
        capture_id=ch.capture_id,
        instructions=ch.instructions,
        created_at=ch.created_at,
        expected_observations=expected_obs,
        sample_alerts=sample_alerts,
        capture_name=ch.capture.name if ch.capture else None,
    )


@router.post("/challenges/{challenge_id}/submit", response_model=SocChallengeResultResponse)
def submit_soc_challenge(
    challenge_id: int,
    payload: SocChallengeSubmitRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> SocChallengeResultResponse:
    """Submit an investigation for scoring and receive educational feedback."""
    attempt = challenge_service.evaluate_submission(
        db=db,
        actor=current_user,
        challenge_id=challenge_id,
        investigation_id=payload.investigation_id,
        identified_evidence=payload.identified_evidence,
        observations=payload.observations,
        hypothesis=payload.hypothesis,
        classification=payload.classification,
        conclusion=payload.conclusion,
    )

    import json
    breakdown = json.loads(attempt.score_breakdown) if attempt.score_breakdown else {}
    feedback_data = json.loads(attempt.feedback) if attempt.feedback else {}

    return SocChallengeResultResponse(
        attempt_id=attempt.id,
        challenge_id=attempt.challenge_id,
        status=attempt.status,
        score=attempt.score,
        score_breakdown=breakdown,
        what_you_did_well=feedback_data.get("what_you_did_well", []),
        evidence_identified=feedback_data.get("evidence_identified", []),
        investigation_steps_completed=feedback_data.get("investigation_steps_completed", []),
        suggested_review=feedback_data.get("suggested_review", []),
    )


# ==============================================================================
# Training Datasets & Demo Mode
# ==============================================================================


@router.get("/datasets", response_model=list[TrainingDatasetItem])
def list_training_datasets(db: DbSession, current_user: CurrentUser) -> list[TrainingDatasetItem]:
    """List synthetic educational training datasets."""
    return training_dataset_service.list_datasets(db)


@router.post("/datasets/load")
def load_training_dataset(
    dataset_id: str = Query(..., description="Identifier of dataset to load"),
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> dict[str, Any]:
    """Execute detection engine over the dataset capture to generate alerts."""
    return training_dataset_service.load_dataset(db, current_user, dataset_id)


@router.post("/datasets/reset")
def reset_training_dataset(db: DbSession, current_user: CurrentUser) -> dict[str, Any]:
    """Safely purge synthetic SOC data without deleting user accounts, curriculum progress, or exams."""
    purged = training_dataset_service.reset_training_data(db, current_user)
    return {"status": "SUCCESS", "message": "Synthetic training data reset.", "purged_records": purged}


# ==============================================================================
# Audit Logs & Notifications
# ==============================================================================


@router.get("/audit-logs", response_model=list[SocAuditLogResponse])
def get_audit_logs(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=200),
) -> list[SocAuditLogResponse]:
    """Retrieve immutable SOC audit trail entries."""
    logs = soc_audit_service.list_logs(db, limit=limit)
    res = []
    for l in logs:
        details_dict = None
        if l.details:
            try:
                details_dict = json.loads(l.details)
            except (ValueError, TypeError, json.JSONDecodeError):
                details_dict = None
        res.append(
            SocAuditLogResponse(
                id=l.id,
                actor_name=l.actor_name,
                action=l.action,
                object_type=l.object_type,
                object_id=l.object_id,
                details=details_dict,
                created_at=l.created_at,
            )
        )
    return res


@router.get("/notifications", response_model=list[SocNotificationResponse])
def get_notifications(
    db: DbSession,
    current_user: CurrentUser,
    unread_only: bool = False,
    limit: int = 30,
) -> list[SocNotificationResponse]:
    """List in-app analyst notifications."""
    notifs = soc_notification_service.list_notifications(
        db, user_id=current_user.id, unread_only=unread_only, limit=limit
    )
    return notifs


@router.patch("/notifications/{notification_id}/read", response_model=SocNotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> SocNotificationResponse:
    """Mark a notification as read."""
    n = soc_notification_service.mark_as_read(db, notification_id)
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return n
