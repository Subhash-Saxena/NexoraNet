"""Process Tree and Process Investigation Service for synthetic endpoint analysis."""

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.endpoint_security import EndpointEvent


class ProcessTreeService:
    """Builds hierarchical process trees and aggregates process-centric telemetry."""

    @staticmethod
    def build_process_tree(db: Session, host_id: int) -> list[dict[str, Any]]:
        """Construct a hierarchical process tree from synthetic PROCESS events on the host.

        Orphaned or root processes (e.g. PPID 0 or 4, or PPID not present) become top-level nodes.
        """
        # Fetch all process events for this host
        stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.event_category == "PROCESS",
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        events = list(db.scalars(stmt).all())

        # Map by process_id
        nodes_by_pid: dict[int, dict[str, Any]] = {}
        for ev in events:
            pid = ev.process_id or ev.id
            if pid not in nodes_by_pid:
                nodes_by_pid[pid] = {
                    "id": ev.id,
                    "event_id": ev.event_id,
                    "process_name": ev.process_name or "unknown.exe",
                    "process_id": pid,
                    "parent_process_id": ev.parent_process_id,
                    "parent_process_name": ev.parent_process_name,
                    "username": ev.username,
                    "command_summary": ev.command_summary,
                    "file_path": ev.file_path,
                    "file_hash": ev.file_hash,
                    "integrity_level": ev.integrity_level or "STANDARD",
                    "start_time": ev.timestamp.isoformat() if ev.timestamp else None,
                    "end_time": None,
                    "severity": ev.severity,
                    "children": [],
                }
            elif ev.event_type == "PROCESS_END":
                nodes_by_pid[pid]["end_time"] = ev.timestamp.isoformat() if ev.timestamp else None

        # Build parent-child relationships
        roots: list[dict[str, Any]] = []
        for pid, node in nodes_by_pid.items():
            ppid = node["parent_process_id"]
            if ppid is not None and ppid in nodes_by_pid and ppid != pid:
                nodes_by_pid[ppid]["children"].append(node)
            else:
                roots.append(node)

        return roots

    @staticmethod
    def get_process_details(db: Session, host_id: int, process_id: int) -> dict[str, Any] | None:
        """Fetch exhaustive telemetry correlated with a specific process instance."""
        # 1. Primary process start event
        proc_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.process_id == process_id,
                EndpointEvent.event_category == "PROCESS",
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        proc_event = db.scalars(proc_stmt).first()
        if not proc_event:
            return None

        process_name = proc_event.process_name

        # 2. End event if any
        end_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.process_id == process_id,
                EndpointEvent.event_type == "PROCESS_END",
            )
            .order_by(EndpointEvent.timestamp.desc())
        )
        end_event = db.scalars(end_stmt).first()

        # 3. Children processes
        children_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.parent_process_id == process_id,
                EndpointEvent.event_category == "PROCESS",
                EndpointEvent.event_type == "PROCESS_START",
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        children = [
            {
                "id": c.id,
                "event_id": c.event_id,
                "process_id": c.process_id,
                "process_name": c.process_name,
                "command_summary": c.command_summary,
                "integrity_level": c.integrity_level,
                "start_time": c.timestamp.isoformat() if c.timestamp else None,
                "severity": c.severity,
            }
            for c in db.scalars(children_stmt).all()
        ]

        # 4. Parent process event if present
        parent = None
        if proc_event.parent_process_id:
            parent_stmt = (
                select(EndpointEvent)
                .where(
                    EndpointEvent.host_id == host_id,
                    EndpointEvent.process_id == proc_event.parent_process_id,
                    EndpointEvent.event_category == "PROCESS",
                )
                .order_by(EndpointEvent.timestamp.asc())
            )
            p_evt = db.scalars(parent_stmt).first()
            if p_evt:
                parent = {
                    "id": p_evt.id,
                    "event_id": p_evt.event_id,
                    "process_id": p_evt.process_id,
                    "process_name": p_evt.process_name,
                    "command_summary": p_evt.command_summary,
                    "username": p_evt.username,
                    "integrity_level": p_evt.integrity_level,
                    "start_time": p_evt.timestamp.isoformat() if p_evt.timestamp else None,
                }

        # 5. Network activity tied to this process
        net_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.event_category == "NETWORK",
                or_(
                    EndpointEvent.process_id == process_id,
                    EndpointEvent.process_name == process_name,
                ),
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        network_events = [
            {
                "id": n.id,
                "event_id": n.event_id,
                "timestamp": n.timestamp.isoformat() if n.timestamp else None,
                "destination_ip": n.destination_ip,
                "destination_port": n.destination_port,
                "protocol": n.protocol,
                "action": n.action,
                "result": n.result,
                "severity": n.severity,
            }
            for n in db.scalars(net_stmt).all()
        ]

        # 6. DNS activity tied to this process
        dns_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.event_category == "DNS",
                or_(
                    EndpointEvent.process_id == process_id,
                    EndpointEvent.process_name == process_name,
                ),
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        dns_events = [
            {
                "id": d.id,
                "event_id": d.event_id,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None,
                "domain": d.domain,
                "query_type": d.dns_query_type,
                "response": d.dns_response,
                "result": d.result,
                "severity": d.severity,
            }
            for d in db.scalars(dns_stmt).all()
        ]

        # 7. File activity tied to this process
        file_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.event_category == "FILE",
                or_(
                    EndpointEvent.process_id == process_id,
                    EndpointEvent.process_name == process_name,
                ),
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        file_events = [
            {
                "id": f.id,
                "event_id": f.event_id,
                "timestamp": f.timestamp.isoformat() if f.timestamp else None,
                "file_name": f.file_name,
                "file_path": f.file_path,
                "file_action": f.file_action,
                "file_hash": f.file_hash,
                "severity": f.severity,
            }
            for f in db.scalars(file_stmt).all()
        ]

        # 8. Related alerts
        alerts_stmt = (
            select(EndpointEvent)
            .where(
                EndpointEvent.host_id == host_id,
                EndpointEvent.severity.in_(["HIGH", "CRITICAL"]),
                or_(
                    EndpointEvent.process_id == process_id,
                    EndpointEvent.process_name == process_name,
                ),
            )
            .order_by(EndpointEvent.timestamp.asc())
        )
        alerts = [
            {
                "id": a.id,
                "event_id": a.event_id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "event_type": a.event_type,
                "severity": a.severity,
                "raw_reference": a.raw_event_reference,
            }
            for a in db.scalars(alerts_stmt).all()
        ]

        return {
            "process": {
                "id": proc_event.id,
                "event_id": proc_event.event_id,
                "process_name": proc_event.process_name,
                "process_id": process_id,
                "parent_process_id": proc_event.parent_process_id,
                "parent_process_name": proc_event.parent_process_name,
                "username": proc_event.username,
                "command_summary": proc_event.command_summary,
                "file_path": proc_event.file_path,
                "file_hash": proc_event.file_hash,
                "integrity_level": proc_event.integrity_level or "STANDARD",
                "start_time": proc_event.timestamp.isoformat() if proc_event.timestamp else None,
                "end_time": end_event.timestamp.isoformat() if end_event and end_event.timestamp else None,
                "severity": proc_event.severity,
                "raw_reference": proc_event.raw_event_reference,
            },
            "parent": parent,
            "children": children,
            "network_activity": network_events,
            "dns_activity": dns_events,
            "file_activity": file_events,
            "related_alerts": alerts,
        }
