"""Deterministic Alert Correlation Service.

Identifies related alerts based on shared network entities, temporal proximity,
and protocol relationships without asserting unjustified attack chains.
"""

from app.models.detection import DetectionAlert
from sqlalchemy.orm import Session


class CorrelationService:
    """Finds correlated alerts using deterministic relationship heuristics."""

    @classmethod
    def find_related_alerts(
        cls,
        db: Session,
        alert: DetectionAlert,
        limit: int = 10,
    ) -> list[dict[str, any]]:
        """Query alerts related by source IP, destination IP, capture, or time window."""
        related = []
        seen_ids = {alert.id}

        # Query candidates in the same capture or with matching source/destination IPs
        query = db.query(DetectionAlert).filter(DetectionAlert.id != alert.id)

        conditions = []
        if alert.source_ip:
            conditions.append(DetectionAlert.source_ip == alert.source_ip)
            conditions.append(DetectionAlert.destination_ip == alert.source_ip)
        if alert.destination_ip:
            conditions.append(DetectionAlert.destination_ip == alert.destination_ip)
            conditions.append(DetectionAlert.source_ip == alert.destination_ip)
        if alert.capture_id:
            conditions.append(DetectionAlert.capture_id == alert.capture_id)

        if conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*conditions))

        candidates = query.order_by(DetectionAlert.created_at.desc()).limit(30).all()

        for cand in candidates:
            if cand.id in seen_ids:
                continue

            reasons = []
            # Check shared source IP
            if alert.source_ip and cand.source_ip == alert.source_ip:
                reasons.append(f"Shared source endpoint {alert.source_ip}")
            # Check shared destination IP
            if alert.destination_ip and cand.destination_ip == alert.destination_ip:
                reasons.append(f"Shared destination endpoint {alert.destination_ip}")
            # Check communication between endpoints (A -> B and B -> A)
            if (
                alert.source_ip
                and alert.destination_ip
                and cand.source_ip == alert.destination_ip
                and cand.destination_ip == alert.source_ip
            ):
                reasons.append("Reciprocal communication between endpoints")
            # Check category overlap
            if cand.category == alert.category:
                reasons.append(f"Matching category {cand.category}")
            # Check capture context
            if alert.capture_id and cand.capture_id == alert.capture_id:
                reasons.append(f"Observed in same capture #{alert.capture_id}")

            if reasons:
                seen_ids.add(cand.id)
                related.append({
                    "id": cand.id,
                    "title": cand.title,
                    "category": cand.category,
                    "severity": cand.severity,
                    "priority": getattr(cand, "priority", "P3"),
                    "status": cand.status,
                    "source_ip": cand.source_ip,
                    "destination_ip": cand.destination_ip,
                    "correlation_reason": "; ".join(reasons) + ". (Potentially related activity; requires analyst validation)",
                    "created_at": cand.created_at,
                })

            if len(related) >= limit:
                break

        return related


correlation_service = CorrelationService()
