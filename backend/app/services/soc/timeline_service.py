"""Chronological Timeline Reconstruction Service.

Builds structured timelines incorporating network packet events,
detection triggers, analyst notes, and status/classification transitions.
"""

from datetime import datetime, timezone
from typing import Any

from app.models.detection import DetectionAlert


def _normalize_dt(dt: datetime | None) -> datetime:
    """Normalize datetime to timezone-aware UTC."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class TimelineService:
    """Reconstructs chronological timelines for SOC alerts and investigations."""

    @classmethod
    def build_alert_timeline(cls, alert: DetectionAlert) -> list[dict[str, Any]]:
        """Reconstruct chronological timeline events for a single alert."""
        events: list[dict[str, Any]] = []

        # 1. First observed network activity
        if alert.first_seen_timestamp:
            first_dt = _normalize_dt(datetime.fromtimestamp(alert.first_seen_timestamp, tz=timezone.utc))
            events.append({
                "timestamp": first_dt,
                "time_display": first_dt.strftime("%H:%M:%S UTC"),
                "event_type": "PACKET_ACTIVITY",
                "title": "Initial Packet Activity Observed",
                "description": f"First matching packet telemetry detected involving {alert.source_ip or 'unknown'} -> {alert.destination_ip or 'unknown'}.",
                "actor_name": "Sensor Telemetry",
            })

        # 2. Detection Trigger
        created_dt = _normalize_dt(alert.created_at)
        events.append({
            "timestamp": created_dt,
            "time_display": created_dt.strftime("%H:%M:%S UTC"),
            "event_type": "DETECTION_TRIGGER",
            "title": f"Detection Rule Triggered: {alert.rule.name if alert.rule else alert.title}",
            "description": f"Alert generated with severity {alert.severity} and {alert.confidence} confidence.",
            "actor_name": "Detection Engine",
        })

        # 3. Status History Transitions
        for hist in alert.status_history:
            h_dt = _normalize_dt(hist.created_at)
            events.append({
                "timestamp": h_dt,
                "time_display": h_dt.strftime("%H:%M:%S UTC"),
                "event_type": "STATUS_TRANSITION",
                "title": f"Status Transition: {hist.previous_status or 'NEW'} -> {hist.new_status}",
                "description": hist.reason or "Status updated by analyst during triage.",
                "actor_name": hist.user.display_name if hist.user else "SOC Analyst",
            })

        # 4. Analyst Notes
        for note in alert.notes:
            n_dt = _normalize_dt(note.created_at)
            events.append({
                "timestamp": n_dt,
                "time_display": n_dt.strftime("%H:%M:%S UTC"),
                "event_type": "ANALYST_NOTE",
                "title": "Analyst Note Recorded",
                "description": note.note,
                "actor_name": note.user.display_name if note.user else "SOC Analyst",
            })

        # Sort chronologically
        events.sort(key=lambda e: e["timestamp"])
        return events


timeline_service = TimelineService()

