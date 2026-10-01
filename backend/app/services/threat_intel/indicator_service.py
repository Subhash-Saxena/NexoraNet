"""Indicator of Compromise (IOC) Management and Correlation Service."""

import json
from datetime import datetime, timezone
from typing import Any

from app.models.detection import DetectionAlert
from app.models.enums import (
    IndicatorClassification,
    IndicatorRelationshipType,
    IndicatorStatus,
    IndicatorType,
    IntelligenceFreshness,
    ThreatIntelConfidence,
)
from app.models.pcap import Capture
from app.models.soc import Investigation
from app.models.threat_intel import (
    EnrichmentCache,
    Indicator,
    IndicatorObservation,
    IndicatorRelationship,
    IndicatorTimeline,
    ThreatIntelSource,
)
from app.models.user import User
from app.services.threat_intel.normalization_service import normalization_service
from app.services.threat_intel.providers.synthetic_provider import (
    synthetic_threat_intel_provider,
)
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session


class IndicatorService:
    """Manages the full lifecycle of threat indicators and correlations."""

    @classmethod
    def generate_indicator_id(cls, db: Session) -> str:
        """Generate human-readable sequential identifier e.g. IOC-2026-0001."""
        year = datetime.now(timezone.utc).year
        count = db.query(Indicator).count() + 1
        return f"IOC-{year}-{count:04d}"

    @classmethod
    def calculate_freshness(cls, last_seen: datetime | None) -> IntelligenceFreshness:
        """Evaluate temporal freshness of indicator observation."""
        if not last_seen:
            return IntelligenceFreshness.UNKNOWN

        now = datetime.now(timezone.utc)
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)

        delta = (now - last_seen).total_seconds()
        if delta < 86400 * 7:  # Within 7 days
            return IntelligenceFreshness.FRESH
        elif delta < 86400 * 30:  # Within 30 days
            return IntelligenceFreshness.RECENT
        else:
            return IntelligenceFreshness.STALE

    @classmethod
    def get_or_create_indicator(
        cls,
        db: Session,
        raw_val: str,
        indicator_type: IndicatorType | str | None = None,
        source_name: str = "NexoraNet Synthetic Threat Intelligence",
        context: dict[str, Any] | None = None,
        actor: User | None = None,
    ) -> Indicator:
        """Retrieve existing indicator by normalized value or create and enrich a new one."""
        target_type = (
            IndicatorType(indicator_type)
            if indicator_type and hasattr(IndicatorType, str(indicator_type))
            else None
        )
        norm_result = normalization_service.normalize(raw_val, target_type)
        norm_val = norm_result["normalized_value"]

        indicator = db.query(Indicator).filter(Indicator.normalized_value == norm_val).first()

        now_utc = datetime.now(timezone.utc)

        if not indicator:
            # Query source record
            src_obj = db.query(ThreatIntelSource).filter(ThreatIntelSource.name == source_name).first()
            source_id = src_obj.id if src_obj else None

            indicator_id_str = cls.generate_indicator_id(db)

            indicator = Indicator(
                indicator_id=indicator_id_str,
                indicator_type=norm_result["indicator_type"],
                hash_type=norm_result["hash_type"],
                value=norm_result["value"],
                normalized_value=norm_val,
                display_value=norm_result["display_value"],
                source_id=source_id,
                source_name=source_name,
                classification=IndicatorClassification.UNKNOWN.value,
                confidence=ThreatIntelConfidence.LOW.value,
                severity="INFO",
                status=IndicatorStatus.ACTIVE.value,
                first_seen=now_utc,
                last_seen=now_utc,
                is_synthetic=True,
            )
            db.add(indicator)
            db.flush()

            # Initial extraction timeline event
            tl_extracted = IndicatorTimeline(
                indicator_id=indicator.id,
                event_type="EXTRACTED",
                title=f"Indicator Extracted: {indicator.display_value}",
                description=f"Extracted as {indicator.indicator_type} from operational telemetry.",
                actor_name=actor.display_name if actor else "IOC Extraction Engine",
                event_timestamp=now_utc,
            )
            db.add(tl_extracted)

            # Auto-enrich against synthetic intelligence
            enrichment = synthetic_threat_intel_provider.lookup_indicator(
                indicator.indicator_type,
                indicator.normalized_value,
            )
            if enrichment:
                indicator.classification = enrichment.classification
                indicator.confidence = enrichment.confidence
                indicator.severity = enrichment.severity
                indicator.description = enrichment.explanation
                indicator.tags = json.dumps(enrichment.tags)
                indicator.mitre_attack_id = enrichment.mitre_attack_id
                indicator.mitre_technique = enrichment.mitre_technique

                tl_enriched = IndicatorTimeline(
                    indicator_id=indicator.id,
                    event_type="ENRICHED",
                    title="Threat Intelligence Enriched",
                    description=f"Classified as {enrichment.classification} ({enrichment.confidence} confidence): {enrichment.explanation}",
                    actor_name="Synthetic Intelligence Provider",
                    event_timestamp=now_utc,
                )
                db.add(tl_enriched)
        else:
            indicator.last_seen = now_utc

        # Record observation if contextual telemetry passed
        if context:
            obs = IndicatorObservation(
                indicator_id=indicator.id,
                capture_id=context.get("capture_id"),
                packet_number=context.get("packet_number"),
                alert_id=context.get("alert_id"),
                investigation_id=context.get("investigation_id"),
                case_id=context.get("case_id"),
                observation_type=context.get("observation_type", "PCAP_TELEMETRY"),
                context_data=json.dumps(context) if context else None,
                observed_at=now_utc,
            )
            db.add(obs)

            tl_observed = IndicatorTimeline(
                indicator_id=indicator.id,
                event_type="OBSERVED",
                title="Telemetry Activity Observed",
                description=context.get("context", f"Observed in {context.get('observation_type', 'telemetry')}."),
                actor_name="Sensor Telemetry",
                event_timestamp=now_utc,
            )
            db.add(tl_observed)

        db.commit()
        db.refresh(indicator)
        return indicator

    @classmethod
    def enrich_indicator(cls, db: Session, indicator_id: int) -> Indicator:
        """Explicitly re-query intelligence providers and update reputation cache."""
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

        result = synthetic_threat_intel_provider.lookup_indicator(
            indicator.indicator_type,
            indicator.normalized_value,
        )

        now_utc = datetime.now(timezone.utc)
        if result:
            indicator.classification = result.classification
            indicator.confidence = result.confidence
            indicator.severity = result.severity
            indicator.description = result.explanation
            indicator.tags = json.dumps(result.tags)
            indicator.mitre_attack_id = result.mitre_attack_id
            indicator.mitre_technique = result.mitre_technique

            # Save in cache
            cache_entry = db.query(EnrichmentCache).filter(
                EnrichmentCache.normalized_value == indicator.normalized_value,
                EnrichmentCache.provider == result.provider,
            ).first()
            if not cache_entry:
                cache_entry = EnrichmentCache(
                    indicator_type=indicator.indicator_type,
                    normalized_value=indicator.normalized_value,
                    provider=result.provider,
                    classification=result.classification,
                    confidence=result.confidence,
                    categories=json.dumps(result.categories),
                    tags=json.dumps(result.tags),
                    raw_metadata=json.dumps(result.raw_metadata),
                    retrieved_at=now_utc,
                )
                db.add(cache_entry)
            else:
                cache_entry.classification = result.classification
                cache_entry.confidence = result.confidence
                cache_entry.retrieved_at = now_utc

            tl = IndicatorTimeline(
                indicator_id=indicator.id,
                event_type="ENRICHED",
                title="Intelligence Reputation Refreshed",
                description=f"Enriched via {result.provider}: {result.classification}.",
                actor_name="Threat Intel Engine",
                event_timestamp=now_utc,
            )
            db.add(tl)
            db.commit()
            db.refresh(indicator)
        return indicator

    @classmethod
    def update_classification(
        cls,
        db: Session,
        indicator_id: int,
        classification: IndicatorClassification | str,
        reason: str,
        status_val: IndicatorStatus | str | None = None,
        actor: User | None = None,
    ) -> Indicator:
        """Update analyst classification and document reasoning."""
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

        cls_val = classification.value if hasattr(classification, "value") else str(classification)
        old_cls = indicator.classification
        indicator.classification = cls_val

        if cls_val == IndicatorClassification.FALSE_POSITIVE.value:
            indicator.false_positive_reason = reason
            indicator.status = IndicatorStatus.FALSE_POSITIVE.value
        elif status_val:
            indicator.status = status_val.value if hasattr(status_val, "value") else str(status_val)

        tl = IndicatorTimeline(
            indicator_id=indicator.id,
            event_type="CLASSIFIED",
            title=f"Analyst Classification: {old_cls} -> {cls_val}",
            description=f"Reason: {reason}",
            actor_name=actor.display_name if actor else "SOC Analyst",
            event_timestamp=datetime.now(timezone.utc),
        )
        db.add(tl)
        db.commit()
        db.refresh(indicator)
        return indicator

    @classmethod
    def add_relationship(
        cls,
        db: Session,
        source_id: int,
        target_id: int,
        rel_type: IndicatorRelationshipType | str = IndicatorRelationshipType.RELATED_TO,
        description: str | None = None,
        confidence: str = "MEDIUM",
    ) -> IndicatorRelationship:
        """Form a structural correlation relationship between two indicators."""
        if source_id == target_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot link indicator to itself.")

        rel_type_str = rel_type.value if hasattr(rel_type, "value") else str(rel_type)

        existing = db.query(IndicatorRelationship).filter(
            IndicatorRelationship.source_indicator_id == source_id,
            IndicatorRelationship.target_indicator_id == target_id,
            IndicatorRelationship.relationship_type == rel_type_str,
        ).first()

        if existing:
            return existing

        rel = IndicatorRelationship(
            source_indicator_id=source_id,
            target_indicator_id=target_id,
            relationship_type=rel_type_str,
            description=description,
            confidence=confidence,
            created_at=datetime.now(timezone.utc),
        )
        db.add(rel)
        db.commit()
        db.refresh(rel)
        return rel

    @classmethod
    def get_indicator_graph(cls, db: Session, indicator_id: int) -> dict[str, Any]:
        """Compile a graph of connected nodes (indicators, alerts, investigations, cases) and links."""
        root = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not root:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

        nodes: list[dict[str, Any]] = []
        links: list[dict[str, Any]] = []
        added_node_ids = set()

        def add_node(node_id: str, label: str, node_type: str, severity: str = "INFO", details: dict[str, Any] | None = None):
            if node_id not in added_node_ids:
                added_node_ids.add(node_id)
                nodes.append({
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "severity": severity,
                    "details": details or {},
                })

        # Root Node
        root_node_id = f"ioc-{root.id}"
        add_node(
            root_node_id,
            root.display_value,
            root.indicator_type,
            root.severity,
            {"classification": root.classification, "indicator_id": root.indicator_id},
        )

        # Related Indicators (Outgoing)
        for rel in root.outgoing_relationships:
            target = rel.target_indicator
            if target:
                target_node_id = f"ioc-{target.id}"
                add_node(
                    target_node_id,
                    target.display_value,
                    target.indicator_type,
                    target.severity,
                    {"classification": target.classification},
                )
                links.append({
                    "source": root_node_id,
                    "target": target_node_id,
                    "label": rel.relationship_type,
                })

        # Related Indicators (Incoming)
        for rel in root.incoming_relationships:
            source = rel.source_indicator
            if source:
                source_node_id = f"ioc-{source.id}"
                add_node(
                    source_node_id,
                    source.display_value,
                    source.indicator_type,
                    source.severity,
                    {"classification": source.classification},
                )
                links.append({
                    "source": source_node_id,
                    "target": root_node_id,
                    "label": rel.relationship_type,
                })

        # Observations -> Alerts
        for obs in root.observations:
            if obs.alert:
                alert_node_id = f"alert-{obs.alert.id}"
                add_node(
                    alert_node_id,
                    f"Alert #{obs.alert.id}: {obs.alert.title}",
                    "ALERT",
                    obs.alert.severity,
                    {"alert_id": obs.alert.id},
                )
                links.append({
                    "source": root_node_id,
                    "target": alert_node_id,
                    "label": "TRIGGERED_ALERT",
                })

            if obs.investigation:
                inv_node_id = f"inv-{obs.investigation.id}"
                add_node(
                    inv_node_id,
                    f"Inv: {obs.investigation.investigation_id}",
                    "INVESTIGATION",
                    "INFO",
                    {"investigation_id": obs.investigation.id},
                )
                links.append({
                    "source": root_node_id,
                    "target": inv_node_id,
                    "label": "INVESTIGATED_IN",
                })

            if obs.case:
                case_node_id = f"case-{obs.case.id}"
                add_node(
                    case_node_id,
                    f"Case: {obs.case.case_id}",
                    "CASE",
                    "INFO",
                    {"case_id": obs.case.id},
                )
                links.append({
                    "source": root_node_id,
                    "target": case_node_id,
                    "label": "INCLUDED_IN_CASE",
                })

        return {
            "root_indicator_id": root.id,
            "nodes": nodes,
            "links": links,
        }

    @classmethod
    def correlate_indicator(cls, db: Session, indicator_id: int) -> dict[str, Any]:
        """Correlate indicator across captures, alerts, investigations, and cases."""
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

        # Find all alerts with matching source or destination IP
        matching_alerts = (
            db.query(DetectionAlert)
            .filter(
                or_(
                    DetectionAlert.source_ip == indicator.normalized_value,
                    DetectionAlert.destination_ip == indicator.normalized_value,
                )
            )
            .all()
        )

        alert_ids = [a.id for a in matching_alerts]

        # Find investigations linked to these alerts
        matching_investigations = []
        if alert_ids:
            invs = (
                db.query(Investigation)
                .join(Investigation.alerts)
                .filter(Investigation.alerts.any(alert_id__in=alert_ids))
                .all()
            )
            matching_investigations = invs

        # Associated captures
        capture_ids = {a.capture_id for a in matching_alerts if a.capture_id}
        captures = db.query(Capture).filter(Capture.id.in_(capture_ids)).all() if capture_ids else []

        return {
            "indicator_id": indicator.id,
            "value": indicator.display_value,
            "normalized_value": indicator.normalized_value,
            "classification": indicator.classification,
            "total_correlated_alerts": len(matching_alerts),
            "alerts": [
                {
                    "id": a.id,
                    "title": a.title,
                    "severity": a.severity,
                    "priority": a.priority,
                    "classification": a.classification,
                    "created_at": a.created_at.isoformat(),
                }
                for a in matching_alerts[:25]
            ],
            "total_correlated_investigations": len(matching_investigations),
            "investigations": [
                {
                    "id": inv.id,
                    "investigation_id": inv.investigation_id,
                    "title": inv.title,
                    "status": inv.status,
                    "priority": inv.priority,
                }
                for inv in matching_investigations[:15]
            ],
            "captures": [
                {
                    "id": c.id,
                    "name": c.name,
                    "packet_count": c.packet_count,
                }
                for c in captures
            ],
            "correlation_summary": (
                f"Indicator '{indicator.display_value}' was correlated with {len(matching_alerts)} alerts "
                f"across {len(captures)} network captures in the offline training dataset."
            ),
        }


indicator_service = IndicatorService()
