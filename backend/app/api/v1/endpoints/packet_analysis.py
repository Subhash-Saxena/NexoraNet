"""FastAPI endpoints for offline PCAP packet capture uploads, inspection, display filtering, and SOC investigation."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ModuleStatusResponse
from app.schemas.pcap import (
    BookmarkCreateRequest,
    BookmarkResponse,
    CaptureDetailResponse,
    CaptureStatisticsResponse,
    CaptureSummaryResponse,
    ConversationItem,
    EndpointItem,
    FindingCreateRequest,
    FindingResponse,
    InvestigationReportResponse,
    NoteCreateRequest,
    NoteResponse,
    ObservationResponse,
    PacketListResponse,
    ParsedPacketDetail,
    PortItem,
    TimelineBucketItem,
)
from app.services.conversation_service import conversation_service
from app.services.packet_analysis_service import packet_analysis_service
from app.services.packet_filter_service import FilterValidationError
from app.services.packet_observation_service import packet_observation_service
from app.services.pcap_parser_service import pcap_parser_service
from app.services.pcap_statistics_service import pcap_statistics_service

router = APIRouter()


@router.get("", response_model=ModuleStatusResponse)
@router.get("/", response_model=ModuleStatusResponse, include_in_schema=False)
@router.get("/status", response_model=ModuleStatusResponse)
async def get_packet_analysis_status() -> ModuleStatusResponse:
    """Return status and metadata for PCAP inspection and packet analyzer."""
    return ModuleStatusResponse(
        module="packet-analysis",
        status="planned",
        description="Browser-based offline PCAP parser, protocol layer dissector, and SOC investigation engine.",
        planned_phase="Phase 4",
        capabilities=[
            "Safe offline PCAP/PCAPNG parsing without raw packet transmission",
            "5-layer OSI decapsulation (Ethernet, ARP, IPv4/IPv6, TCP, UDP, ICMP, DNS, HTTP, TLS metadata)",
            "Deterministic display-filter AST evaluator without eval()",
            "5-tuple conversation flows and TCP 3-way handshake state analysis",
            "Rule-based neutral pattern observation engine",
            "SOC investigation workspace with bookmarks, notes, findings, and JSON report export",
        ],
    )


@router.post("/captures", response_model=CaptureDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_capture(
    db: DbSession,
    current_user: CurrentUser,
    file: Annotated[UploadFile, File(description="PCAP or PCAPNG packet capture file")],
    name: Annotated[str | None, Query(description="Optional custom capture title")] = None,
    description: Annotated[str | None, Query(description="Optional description")] = None,
) -> CaptureDetailResponse:
    """Upload a PCAP/PCAPNG file, validate file format and size limits, and parse into normalized packets."""
    try:
        raw_bytes = await file.read()
        capture = packet_analysis_service.create_upload_capture(
            db=db,
            raw_bytes=raw_bytes,
            original_filename=file.filename or "uploaded.pcap",
            user=current_user,
            custom_name=name,
            description=description,
        )
        return packet_analysis_service.get_capture_detail(db, capture.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (OSError, RuntimeError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process capture file: {e!s}",
        )


@router.get("/captures", response_model=list[CaptureSummaryResponse])
async def list_captures(
    db: DbSession,
    current_user: CurrentUser,
) -> list[CaptureSummaryResponse]:
    """Retrieve catalog of accessible captures (user uploads and prebuilt sample library)."""
    return packet_analysis_service.list_captures(db, user=current_user)


@router.get("/captures/{capture_id}", response_model=CaptureDetailResponse)
async def get_capture(
    capture_id: int,
    db: DbSession,
) -> CaptureDetailResponse:
    """Retrieve macro summary and status of a specific capture."""
    try:
        return packet_analysis_service.get_capture_detail(db, capture_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/captures/{capture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_capture(
    capture_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a user-uploaded capture and purge stored binary file."""
    try:
        packet_analysis_service.delete_capture(db, capture_id, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/captures/{capture_id}/parse", response_model=CaptureDetailResponse)
async def trigger_reparse_capture(
    capture_id: int,
    db: DbSession,
) -> CaptureDetailResponse:
    """Trigger re-parsing of an existing stored capture."""
    try:
        capture = packet_analysis_service.get_capture(db, capture_id)
        updated = pcap_parser_service.parse_and_index_capture(db, capture)
        return packet_analysis_service.get_capture_detail(db, updated.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/packets", response_model=PacketListResponse)
async def list_packets(
    capture_id: int,
    db: DbSession,
    filter: Annotated[str | None, Query(description="Display filter query e.g. 'tcp.flags.syn && ip.addr == 10.0.0.5'")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=10, le=500, description="Items per page")] = 50,
) -> PacketListResponse:
    """Query, filter, and paginate normalized packet records."""
    try:
        return packet_analysis_service.get_packets(
            db=db,
            capture_id=capture_id,
            filter_str=filter,
            page=page,
            page_size=page_size,
        )
    except FilterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/packets/{packet_number}", response_model=ParsedPacketDetail)
async def get_packet_detail(
    capture_id: int,
    packet_number: int,
    db: DbSession,
) -> ParsedPacketDetail:
    """Retrieve decoded protocol header layers and detailed frame trees."""
    try:
        return packet_analysis_service.get_packet_detail(db, capture_id, packet_number)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/statistics", response_model=CaptureStatisticsResponse)
async def get_capture_statistics(
    capture_id: int,
    db: DbSession,
) -> CaptureStatisticsResponse:
    """Retrieve traffic metrics, protocol distribution, and top talkers."""
    try:
        capture = packet_analysis_service.get_capture(db, capture_id)
        return pcap_statistics_service.get_statistics(db, capture)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/conversations", response_model=list[ConversationItem])
async def get_capture_conversations(
    capture_id: int,
    db: DbSession,
) -> list[ConversationItem]:
    """Retrieve 5-tuple conversations, TCP handshake states, and flow ladder steps."""
    try:
        packet_analysis_service.get_capture(db, capture_id)
        return conversation_service.get_conversations(db, capture_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/endpoints", response_model=list[EndpointItem])
async def get_capture_endpoints(
    capture_id: int,
    db: DbSession,
) -> list[EndpointItem]:
    """Retrieve IP endpoints with packet/byte volume and active protocols."""
    try:
        packet_analysis_service.get_capture(db, capture_id)
        return pcap_statistics_service.get_endpoints(db, capture_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/ports", response_model=list[PortItem])
async def get_capture_ports(
    capture_id: int,
    db: DbSession,
) -> list[PortItem]:
    """Retrieve transport port frequencies and service hints."""
    try:
        packet_analysis_service.get_capture(db, capture_id)
        return pcap_statistics_service.get_ports(db, capture_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/timeline", response_model=list[TimelineBucketItem])
async def get_capture_timeline(
    capture_id: int,
    db: DbSession,
    buckets: Annotated[int, Query(ge=5, le=100, description="Number of temporal time buckets")] = 30,
) -> list[TimelineBucketItem]:
    """Retrieve temporal traffic density buckets for burst analysis."""
    try:
        capture = packet_analysis_service.get_capture(db, capture_id)
        return pcap_statistics_service.get_timeline(db, capture, bucket_count=buckets)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/observations", response_model=list[ObservationResponse])
async def get_capture_observations(
    capture_id: int,
    db: DbSession,
) -> list[ObservationResponse]:
    """Evaluate deterministic SOC pattern observation rules against captured traffic."""
    try:
        packet_analysis_service.get_capture(db, capture_id)
        return packet_observation_service.analyze_observations(db, capture_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Investigation Workspace (Bookmarks, Notes, Findings, Report) ---


@router.post("/captures/{capture_id}/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    capture_id: int,
    req: BookmarkCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> BookmarkResponse:
    """Bookmark an interesting packet for SOC investigation."""
    try:
        return packet_analysis_service.create_bookmark(db, capture_id, req, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/bookmarks", response_model=list[BookmarkResponse])
async def list_bookmarks(
    capture_id: int,
    db: DbSession,
) -> list[BookmarkResponse]:
    """List bookmarked packets for a capture."""
    return packet_analysis_service.list_bookmarks(db, capture_id)


@router.post("/captures/{capture_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    capture_id: int,
    req: NoteCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> NoteResponse:
    """Attach an analyst note to a packet, endpoint, conversation, or capture."""
    try:
        return packet_analysis_service.create_note(db, capture_id, req, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/notes", response_model=list[NoteResponse])
async def list_notes(
    capture_id: int,
    db: DbSession,
) -> list[NoteResponse]:
    """List investigation notes."""
    return packet_analysis_service.list_notes(db, capture_id)


@router.post("/captures/{capture_id}/findings", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(
    capture_id: int,
    req: FindingCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> FindingResponse:
    """Record an investigation finding with evidence packets, hypothesis, and conclusion."""
    try:
        return packet_analysis_service.create_finding(db, capture_id, req, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/captures/{capture_id}/findings", response_model=list[FindingResponse])
async def list_findings(
    capture_id: int,
    db: DbSession,
) -> list[FindingResponse]:
    """List recorded investigation findings."""
    return packet_analysis_service.list_findings(db, capture_id)


@router.get("/captures/{capture_id}/report", response_model=InvestigationReportResponse)
async def get_investigation_report(
    capture_id: int,
    db: DbSession,
) -> InvestigationReportResponse:
    """Generate consolidated offline investigation summary report in JSON."""
    try:
        return packet_analysis_service.generate_investigation_report(db, capture_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
