"""Pre-built Training Datasets, Demo Mode, and Safe Reset Service for Step 12 SOC."""

from typing import Any, ClassVar

from app.models.detection import (
    AlertEvidence,
    AlertNote,
    AlertStatusHistory,
    DetectionAlert,
    DetectionRun,
)
from app.models.pcap import Capture
from app.models.soc import (
    Case,
    CaseAlert,
    CaseInvestigation,
    CaseNote,
    Investigation,
    InvestigationAlert,
    InvestigationEvidence,
    InvestigationFinding,
    InvestigationHypothesis,
    InvestigationNote,
    SocChallengeAttempt,
    SocNotification,
)
from app.models.user import User
from app.services.detection.detection_run_service import DetectionRunService
from app.services.soc.audit_service import soc_audit_service
from sqlalchemy.orm import Session


class TrainingDatasetService:
    """Provides synthetic datasets and safe reset routines for educational SOC exercises."""

    DATASETS: ClassVar[list[dict[str, Any]]] = [
        {
            "dataset_id": "tcp_investigation",
            "name": "TCP Investigation Lab",
            "category": "TCP",
            "description": "Port scan reconnaissance, SYN bursts without handshakes, and TCP reset teardowns.",
            "target_capture_name": "noteworthy_syn_pattern.pcap",
        },
        {
            "dataset_id": "dns_investigation",
            "name": "DNS Investigation Lab",
            "category": "DNS",
            "description": "High-volume NXDOMAIN resolution bursts, randomized subdomain queries, and external resolver queries.",
            "target_capture_name": "dns_lookup.pcap",
        },
        {
            "dataset_id": "arp_investigation",
            "name": "ARP Mapping Conflict Lab",
            "category": "ARP",
            "description": "Layer 2 conflicting MAC addresses claiming ownership of a default gateway IP.",
            "target_capture_name": "arp_resolution.pcap",
        },
        {
            "dataset_id": "mixed_investigation",
            "name": "Mixed Network Investigation",
            "category": "Mixed",
            "description": "Multi-host mixed LAN telemetry featuring HTTP, DNS, TCP handshakes, and asymmetric flow volumes.",
            "target_capture_name": "multi_host_traffic.pcap",
        },
        {
            "dataset_id": "benign_activity",
            "name": "Benign Network Activity",
            "category": "Baseline",
            "description": "Clean three-way handshakes, ICMP diagnostics, and web browsing that test false positive differentiation.",
            "target_capture_name": "basic_ping.pcap",
        },
    ]

    @classmethod
    def list_datasets(cls, db: Session) -> list[dict[str, Any]]:
        """List all educational datasets with availability status."""
        results = []
        for ds in cls.DATASETS:
            cap = db.query(Capture).filter(Capture.filename == ds["target_capture_name"]).first()
            pkt_count = cap.packet_count if cap else 0
            alert_count = db.query(DetectionAlert).filter(DetectionAlert.capture_id == cap.id).count() if cap else 0

            results.append({
                "dataset_id": ds["dataset_id"],
                "name": ds["name"],
                "category": ds["category"],
                "description": ds["description"],
                "packet_count": pkt_count,
                "alert_count": alert_count,
                "is_active": alert_count > 0,
            })
        return results

    @classmethod
    def load_dataset(cls, db: Session, actor: User, dataset_id: str) -> dict[str, Any]:
        """Trigger an offline detection run against the dataset's reference PCAP to populate alerts."""
        target = next((d for d in cls.DATASETS if d["dataset_id"] == dataset_id), None)
        if not target:
            raise ValueError(f"Dataset {dataset_id} not found.")

        cap = db.query(Capture).filter(Capture.filename == target["target_capture_name"]).first()
        if not cap:
            # Fallback to any ready sample capture
            cap = db.query(Capture).filter(Capture.is_sample.is_(True), Capture.status == "READY").first()
            if not cap:
                return {
                    "dataset_id": dataset_id,
                    "status": "NO_CAPTURE_AVAILABLE",
                    "message": "No sample PCAP found in database to load dataset.",
                    "alerts_generated": 0,
                }

        # Run detection engine over the capture
        run_res = DetectionRunService.execute_run(
            db=db,
            user_id=actor.id,
            source_type="PCAP",
            capture_id=cap.id,
        )

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="LOAD_TRAINING_DATASET",
            object_type="DATASET",
            object_id=dataset_id,
            details={"capture_id": cap.id, "alerts_generated": run_res.alerts_generated},
        )

        return {
            "dataset_id": dataset_id,
            "status": "LOADED",
            "capture_id": cap.id,
            "alerts_generated": run_res.alerts_generated,
            "packets_analyzed": run_res.packets_analyzed,
            "message": f"Successfully loaded '{target['name']}' with {run_res.alerts_generated} generated alerts.",
        }

    @classmethod
    def reset_training_data(cls, db: Session, actor: User) -> dict[str, int]:
        """Safely purge synthetic SOC data without deleting users, curriculum progress, or mock test data."""
        deleted_counts = {}

        # 1. Purge challenge attempts
        deleted_counts["challenge_attempts"] = db.query(SocChallengeAttempt).delete()

        # 2. Purge case associations & cases
        deleted_counts["case_notes"] = db.query(CaseNote).delete()
        deleted_counts["case_alerts"] = db.query(CaseAlert).delete()
        deleted_counts["case_investigations"] = db.query(CaseInvestigation).delete()
        deleted_counts["cases"] = db.query(Case).delete()

        # 3. Purge investigation associations & investigations
        deleted_counts["investigation_notes"] = db.query(InvestigationNote).delete()
        deleted_counts["investigation_findings"] = db.query(InvestigationFinding).delete()
        deleted_counts["investigation_hypotheses"] = db.query(InvestigationHypothesis).delete()
        deleted_counts["investigation_evidence"] = db.query(InvestigationEvidence).delete()
        deleted_counts["investigation_alerts"] = db.query(InvestigationAlert).delete()
        deleted_counts["investigations"] = db.query(Investigation).delete()

        # 4. Purge detection alerts, notes, status history, and runs
        deleted_counts["alert_notes"] = db.query(AlertNote).delete()
        deleted_counts["alert_status_history"] = db.query(AlertStatusHistory).delete()
        deleted_counts["alert_evidence"] = db.query(AlertEvidence).delete()
        deleted_counts["detection_alerts"] = db.query(DetectionAlert).delete()
        deleted_counts["detection_runs"] = db.query(DetectionRun).delete()

        # 5. Purge notifications
        deleted_counts["soc_notifications"] = db.query(SocNotification).delete()

        db.commit()

        soc_audit_service.log_action(
            db,
            actor=actor,
            action="RESET_TRAINING_DATA",
            object_type="SYSTEM",
            object_id="SOC_TRAINING_ENVIRONMENT",
            details=deleted_counts,
        )

        return deleted_counts


training_dataset_service = TrainingDatasetService()
