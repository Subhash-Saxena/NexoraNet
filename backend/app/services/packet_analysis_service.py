"""High-level packet analysis orchestrator connecting file storage, parser, filters, and investigation telemetry."""

import json
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.pcap_config import pcap_settings
from app.models.enums import CaptureStatus
from app.models.pcap import (
    Capture,
    CaptureBookmark,
    CaptureFinding,
    CaptureNote,
    ParsedPacket,
)
from app.models.user import User
from app.schemas.pcap import (
    BookmarkCreateRequest,
    BookmarkResponse,
    CaptureDetailResponse,
    CaptureSummaryResponse,
    FindingCreateRequest,
    FindingResponse,
    InvestigationReportResponse,
    NoteCreateRequest,
    NoteResponse,
    PacketListResponse,
    ParsedPacketDetail,
    ParsedPacketSummary,
)
from app.services.conversation_service import conversation_service
from app.services.packet_filter_service import (
    FilterValidationError,
    packet_filter_service,
)
from app.services.packet_observation_service import packet_observation_service
from app.services.pcap_parser_service import pcap_parser_service
from app.services.pcap_statistics_service import pcap_statistics_service


class PacketAnalysisService:
    """Coordinates capture lifecycles, queries, filters, and investigation reporting."""

    def create_upload_capture(
        self,
        db: Session,
        raw_bytes: bytes,
        original_filename: str,
        user: User | None = None,
        custom_name: str | None = None,
        description: str | None = None,
    ) -> Capture:
        """Securely validate and persist an uploaded PCAP file."""
        # 1. Size check
        if len(raw_bytes) > pcap_settings.MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(
                f"Capture exceeds the maximum allowed size of {pcap_settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."
            )

        # 2. Extension validation
        sanitized_name = Path(original_filename).name
        ext = Path(sanitized_name).suffix.lower()

        if ext in pcap_settings.DISALLOWED_EXTENSIONS:
            raise ValueError(f"Prohibited file type: {ext}")
        if ext not in pcap_settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported capture file format '{ext}'. Expected .pcap or .pcapng.")

        # 3. Secure internal filename to avoid path traversal
        pcap_settings.CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
        unique_id = uuid.uuid4().hex
        secure_filename = f"capture_{unique_id}{ext}"
        storage_path = pcap_settings.CAPTURES_DIR / secure_filename

        # 4. Write binary data
        with open(storage_path, "wb") as f:
            f.write(raw_bytes)

        # 5. Insert Capture record
        name = custom_name or Path(sanitized_name).stem.replace("_", " ").title()
        capture = Capture(
            user_id=user.id if user else None,
            name=name,
            filename=sanitized_name,
            storage_path=str(storage_path),
            file_size=len(raw_bytes),
            format=ext.lstrip("."),
            status=CaptureStatus.UPLOADED,
            description=description,
        )
        db.add(capture)
        db.commit()
        db.refresh(capture)

        # 6. Parse and normalize capture into relational records
        return pcap_parser_service.parse_and_index_capture(db, capture)

    def list_captures(self, db: Session, user: User | None = None) -> list[CaptureSummaryResponse]:
        """List all accessible captures (user's captures + prebuilt sample library)."""
        query = db.query(Capture)
        if user:
            query = query.filter((Capture.user_id == user.id) | (Capture.is_sample == True))
        else:
            query = query.filter(Capture.is_sample == True)

        captures = query.order_by(Capture.is_sample.desc(), Capture.created_at.desc()).all()
        return [CaptureSummaryResponse.model_validate(c) for c in captures]

    def get_capture(self, db: Session, capture_id: int) -> Capture:
        """Fetch capture by ID with existence check."""
        capture = db.query(Capture).filter(Capture.id == capture_id).first()
        if not capture:
            raise ValueError(f"Capture with ID {capture_id} not found.")
        return capture

    def get_capture_detail(self, db: Session, capture_id: int) -> CaptureDetailResponse:
        """Return rich capture summary and safety notices."""
        capture = self.get_capture(db, capture_id)
        meta = json.loads(capture.summary_metadata) if capture.summary_metadata else {}
        resp = CaptureDetailResponse.model_validate(capture)
        resp.summary_metadata = meta
        return resp

    def delete_capture(self, db: Session, capture_id: int, user: User | None = None) -> None:
        """Delete capture record and purge underlying storage file."""
        capture = self.get_capture(db, capture_id)
        if capture.is_sample:
            raise ValueError("Reference sample captures cannot be deleted.")

        # Remove physical file if exists
        try:
            Path(capture.storage_path).unlink(missing_ok=True)
        except OSError:
            pass

        db.delete(capture)
        db.commit()

    def get_packets(
        self,
        db: Session,
        capture_id: int,
        filter_str: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PacketListResponse:
        """Query and paginate packets with optional safe display-filter AST evaluation."""
        self.get_capture(db, capture_id)
        page = max(1, page)
        page_size = min(max(10, page_size), 500)

        query = db.query(ParsedPacket).filter(ParsedPacket.capture_id == capture_id)

        # Apply safe filter grammar if provided
        if filter_str and filter_str.strip():
            cleaned_filter = filter_str.strip()
            if len(cleaned_filter) > pcap_settings.MAX_FILTER_QUERY_LENGTH:
                raise FilterValidationError("Filter expression exceeds maximum allowed length.")
            ast = packet_filter_service.parse(cleaned_filter)
            if ast:
                sql_criterion = packet_filter_service.build_sql_criterion(ast)
                query = query.filter(sql_criterion)

        total_matched = query.count()
        total_pages = max(1, (total_matched + page_size - 1) // page_size)
        offset = (page - 1) * page_size

        packets = (
            query.order_by(ParsedPacket.packet_number.asc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        packet_summaries = [ParsedPacketSummary.model_validate(p) for p in packets]

        return PacketListResponse(
            capture_id=capture_id,
            total_matched=total_matched,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            filter_applied=filter_str,
            packets=packet_summaries,
        )

    def get_packet_detail(self, db: Session, capture_id: int, packet_number: int) -> ParsedPacketDetail:
        """Retrieve full decoded layer hierarchy for a specific packet."""
        pkt = (
            db.query(ParsedPacket)
            .filter(ParsedPacket.capture_id == capture_id)
            .filter(ParsedPacket.packet_number == packet_number)
            .first()
        )
        if not pkt:
            raise ValueError(f"Packet #{packet_number} not found in capture {capture_id}.")

        layers = json.loads(pkt.layers) if pkt.layers else ["Frame"]
        layer_details = json.loads(pkt.layer_details) if pkt.layer_details else {}
        tcp_flags = json.loads(pkt.tcp_flags) if pkt.tcp_flags else []

        resp = ParsedPacketDetail.model_validate(pkt)
        resp.layers = layers
        resp.layer_details = layer_details
        resp.tcp_flags = tcp_flags
        return resp

    # --- Investigation Telemetry (Bookmarks, Notes, Findings, Report) ---

    def create_bookmark(self, db: Session, capture_id: int, req: BookmarkCreateRequest, user: User | None = None) -> BookmarkResponse:
        self.get_capture(db, capture_id)
        bookmark = CaptureBookmark(
            capture_id=capture_id,
            user_id=user.id if user else None,
            packet_number=req.packet_number,
            note=req.note,
            tags=json.dumps(req.tags) if req.tags else None,
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        resp = BookmarkResponse.model_validate(bookmark)
        resp.tags = req.tags
        return resp

    def list_bookmarks(self, db: Session, capture_id: int) -> list[BookmarkResponse]:
        bookmarks = db.query(CaptureBookmark).filter(CaptureBookmark.capture_id == capture_id).all()
        results: list[BookmarkResponse] = []
        for b in bookmarks:
            r = BookmarkResponse.model_validate(b)
            r.tags = json.loads(b.tags) if b.tags else []
            results.append(r)
        return results

    def create_note(self, db: Session, capture_id: int, req: NoteCreateRequest, user: User | None = None) -> NoteResponse:
        self.get_capture(db, capture_id)
        note = CaptureNote(
            capture_id=capture_id,
            user_id=user.id if user else None,
            target_type=req.target_type,
            target_id=req.target_id,
            title=req.title,
            content=req.content,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return NoteResponse.model_validate(note)

    def list_notes(self, db: Session, capture_id: int) -> list[NoteResponse]:
        notes = db.query(CaptureNote).filter(CaptureNote.capture_id == capture_id).order_by(CaptureNote.created_at.desc()).all()
        return [NoteResponse.model_validate(n) for n in notes]

    def create_finding(self, db: Session, capture_id: int, req: FindingCreateRequest, user: User | None = None) -> FindingResponse:
        self.get_capture(db, capture_id)
        finding = CaptureFinding(
            capture_id=capture_id,
            user_id=user.id if user else None,
            title=req.title,
            description=req.description,
            severity=str(req.severity),
            evidence_packets=json.dumps(req.evidence_packets) if req.evidence_packets else None,
            source_endpoint=req.source_endpoint,
            destination_endpoint=req.destination_endpoint,
            hypothesis=req.hypothesis,
            conclusion=req.conclusion,
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        resp = FindingResponse.model_validate(finding)
        resp.evidence_packets = req.evidence_packets
        return resp

    def list_findings(self, db: Session, capture_id: int) -> list[FindingResponse]:
        findings = db.query(CaptureFinding).filter(CaptureFinding.capture_id == capture_id).order_by(CaptureFinding.created_at.desc()).all()
        results: list[FindingResponse] = []
        for f in findings:
            r = FindingResponse.model_validate(f)
            r.evidence_packets = json.loads(f.evidence_packets) if f.evidence_packets else []
            results.append(r)
        return results

    def generate_investigation_report(self, db: Session, capture_id: int) -> InvestigationReportResponse:
        """Consolidate entire packet capture analysis into an offline SOC report."""
        capture = self.get_capture(db, capture_id)
        stats = pcap_statistics_service.get_statistics(db, capture)
        endpoints = pcap_statistics_service.get_endpoints(db, capture_id)[:10]
        conversations = conversation_service.get_conversations(db, capture_id)[:15]
        observations = packet_observation_service.analyze_observations(db, capture_id)
        bookmarks = self.list_bookmarks(db, capture_id)
        notes = self.list_notes(db, capture_id)
        findings = self.list_findings(db, capture_id)

        return InvestigationReportResponse(
            capture=CaptureSummaryResponse.model_validate(capture),
            statistics=stats,
            top_endpoints=endpoints,
            conversations=conversations,
            observations=observations,
            bookmarks=bookmarks,
            notes=notes,
            findings=findings,
        )


packet_analysis_service = PacketAnalysisService()
