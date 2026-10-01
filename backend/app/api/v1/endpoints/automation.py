"""Educational SOAR Automation API Endpoints.

Provides endpoints for Playbook Catalog, Sequential Step Execution,
Manual Approval Gates, Dry-Run Testing, and Security Automation KPIs.
Strictly offline educational simulation.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.models.soar import AutomationAuditLog, PlaybookExecution
from app.schemas.soar import (
    ApprovalActionRequest,
    AutomationAuditLogResponse,
    AutomationPlaybookCreate,
    AutomationPlaybookDetailResponse,
    AutomationPlaybookResponse,
    DryRunRequest,
    DryRunResponse,
    PlaybookExecutionDetailResponse,
    PlaybookExecutionResponse,
    PlaybookExecutionTriggerRequest,
    SoarMetricsResponse,
)
from app.services.soar.approval_service import ApprovalService
from app.services.soar.execution_engine import ExecutionEngine
from app.services.soar.playbook_service import PlaybookService

router = APIRouter()


# ------------------------------------------------------------------------------
# 1. Playbook Catalog & Management
# ------------------------------------------------------------------------------
@router.get(
    "/playbooks",
    response_model=list[AutomationPlaybookResponse],
    summary="List available automation playbooks",
)
def list_playbooks(
    db: DbSession,
    category: str | None = Query(None, description="Filter by playbook category"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status (ENABLED, DISABLED)"),
    trigger_type: str | None = Query(None, description="Filter by trigger type"),
) -> Any:
    """Retrieve educational SOAR playbooks matching optional filters."""
    playbooks = PlaybookService.list_playbooks(
        db=db,
        category=category,
        status=status_filter,
        trigger_type=trigger_type,
    )
    result = []
    for pb in playbooks:
        item = AutomationPlaybookResponse.model_validate(pb)
        item.steps_count = len(pb.steps)
        result.append(item)
    return result


@router.get(
    "/playbooks/{playbook_id}",
    response_model=AutomationPlaybookDetailResponse,
    summary="Get playbook details with steps",
)
def get_playbook_detail(
    playbook_id: str,
    db: DbSession,
) -> Any:
    """Retrieve full playbook definition including sequential automation steps."""
    pb = PlaybookService.get_playbook(db=db, identifier=playbook_id)
    if not pb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playbook '{playbook_id}' not found.",
        )
    resp = AutomationPlaybookDetailResponse.model_validate(pb)
    resp.steps_count = len(pb.steps)
    return resp


@router.post(
    "/playbooks",
    response_model=AutomationPlaybookDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom automation playbook",
)
def create_playbook(
    payload: AutomationPlaybookCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Author a new custom educational SOAR playbook."""
    pb = PlaybookService.create_playbook(
        db=db,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        trigger_type=payload.trigger_type,
        trigger_filter=payload.trigger_filter,
        risk_level=payload.risk_level,
        requires_approval=payload.requires_approval,
        steps_data=payload.steps,
        created_by=current_user.username if current_user else "analyst",
    )
    resp = AutomationPlaybookDetailResponse.model_validate(pb)
    resp.steps_count = len(pb.steps)
    return resp


@router.post(
    "/playbooks/{playbook_id}/dry-run",
    response_model=DryRunResponse,
    summary="Simulate dry-run execution of a playbook",
)
def dry_run_playbook(
    playbook_id: str,
    payload: DryRunRequest,
    db: DbSession,
) -> Any:
    """Safely test playbook condition branching and variable binding without side effects."""
    try:
        return PlaybookService.dry_run_playbook(
            db=db,
            playbook_id=playbook_id,
            mock_input=payload.mock_input,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/playbooks/{playbook_id}/status",
    response_model=AutomationPlaybookResponse,
    summary="Update playbook status (ENABLE/DISABLE)",
)
def update_playbook_status(
    playbook_id: str,
    new_status: str = Query(..., description="ENABLED or DISABLED"),
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> Any:
    """Toggle playbook operational status."""
    try:
        pb = PlaybookService.update_playbook_status(db=db, playbook_id=playbook_id, status=new_status)
        resp = AutomationPlaybookResponse.model_validate(pb)
        resp.steps_count = len(pb.steps)
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ------------------------------------------------------------------------------
# 2. Executions & Orchestration
# ------------------------------------------------------------------------------
@router.get(
    "/executions",
    response_model=list[PlaybookExecutionResponse],
    summary="List playbook execution logs",
)
def list_executions(
    db: DbSession,
    status_filter: str | None = Query(None, alias="status"),
    playbook_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """Retrieve history of SOAR automation executions."""
    query = db.query(PlaybookExecution)
    if status_filter:
        query = query.filter(PlaybookExecution.status == status_filter)
    if playbook_id:
        if playbook_id.isdigit():
            query = query.filter(PlaybookExecution.playbook_id == int(playbook_id))
        else:
            query = query.join(PlaybookExecution.playbook).filter(
                PlaybookExecution.playbook.has(playbook_id=playbook_id)
            )

    executions = query.order_by(PlaybookExecution.created_at.desc()).limit(limit).all()
    results = []
    for ex in executions:
        item = PlaybookExecutionResponse.model_validate(ex)
        if ex.playbook:
            item.playbook_identifier = ex.playbook.playbook_id
            item.playbook_name = ex.playbook.name
        results.append(item)
    return results


@router.get(
    "/executions/{execution_id}",
    response_model=PlaybookExecutionDetailResponse,
    summary="Get execution details with step-by-step logs",
)
def get_execution_detail(
    execution_id: str,
    db: DbSession,
) -> Any:
    """Retrieve execution progress, step-by-step audit logs, and accumulated artifacts."""
    ex = db.query(PlaybookExecution).filter(PlaybookExecution.execution_id == execution_id).first()
    if not ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution '{execution_id}' not found.",
        )
    resp = PlaybookExecutionDetailResponse.model_validate(ex)
    if ex.playbook:
        resp.playbook_identifier = ex.playbook.playbook_id
        resp.playbook_name = ex.playbook.name
    return resp


@router.post(
    "/executions/trigger",
    response_model=PlaybookExecutionDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger automated playbook execution",
)
def trigger_playbook_execution(
    payload: PlaybookExecutionTriggerRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Initiate a deterministic educational SOAR playbook run."""
    try:
        execution = ExecutionEngine.trigger_playbook(
            db=db,
            playbook_id=payload.playbook_id,
            trigger_source=payload.trigger_source,
            source_id=payload.source_id,
            requested_by=current_user.username if current_user else "analyst",
            idempotency_key=payload.idempotency_key,
            initial_context=payload.context,
        )
        resp = PlaybookExecutionDetailResponse.model_validate(execution)
        if execution.playbook:
            resp.playbook_identifier = execution.playbook.playbook_id
            resp.playbook_name = execution.playbook.name
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ------------------------------------------------------------------------------
# 3. Analyst Approval Gates
# ------------------------------------------------------------------------------
@router.post(
    "/executions/{execution_id}/approve",
    response_model=PlaybookExecutionDetailResponse,
    summary="Approve pending execution authorization gate",
)
def approve_execution(
    execution_id: str,
    payload: ApprovalActionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Authorize a paused execution to proceed through sensitive automation steps."""
    try:
        approver = current_user.username if current_user else "analyst"
        ApprovalService.approve(
            db=db,
            execution_id=execution_id,
            approver=approver,
            reason=payload.reason,
        )
        # Resume execution
        execution = ExecutionEngine.resume_execution(
            db=db,
            execution_id=execution_id,
            actor=approver,
        )
        resp = PlaybookExecutionDetailResponse.model_validate(execution)
        if execution.playbook:
            resp.playbook_identifier = execution.playbook.playbook_id
            resp.playbook_name = execution.playbook.name
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/executions/{execution_id}/reject",
    response_model=PlaybookExecutionResponse,
    summary="Reject pending execution authorization gate",
)
def reject_execution(
    execution_id: str,
    payload: ApprovalActionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Reject and abort execution gate."""
    try:
        rejector = current_user.username if current_user else "analyst"
        execution = ApprovalService.reject(
            db=db,
            execution_id=execution_id,
            rejector=rejector,
            reason=payload.reason,
        )
        resp = PlaybookExecutionResponse.model_validate(execution)
        if execution.playbook:
            resp.playbook_identifier = execution.playbook.playbook_id
            resp.playbook_name = execution.playbook.name
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/executions/{execution_id}/cancel",
    response_model=PlaybookExecutionResponse,
    summary="Cancel active execution",
)
def cancel_execution(
    execution_id: str,
    payload: ApprovalActionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Cancel execution manually."""
    try:
        actor = current_user.username if current_user else "analyst"
        execution = ApprovalService.cancel(
            db=db,
            execution_id=execution_id,
            actor=actor,
            reason=payload.reason,
        )
        resp = PlaybookExecutionResponse.model_validate(execution)
        if execution.playbook:
            resp.playbook_identifier = execution.playbook.playbook_id
            resp.playbook_name = execution.playbook.name
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ------------------------------------------------------------------------------
# 4. Metrics & Audit Trail
# ------------------------------------------------------------------------------
@router.get(
    "/metrics",
    response_model=SoarMetricsResponse,
    summary="Get SOAR automation KPIs and performance metrics",
)
def get_soar_metrics(
    db: DbSession,
) -> Any:
    """Calculate SOAR automation KPIs, hours saved, and execution statistics."""
    return PlaybookService.get_metrics(db=db)


@router.get(
    "/audit-logs",
    response_model=list[AutomationAuditLogResponse],
    summary="Query immutable automation audit log entries",
)
def get_audit_logs(
    db: DbSession,
    execution_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
) -> Any:
    """Retrieve immutable security audit trail for all automation actions."""
    query = db.query(AutomationAuditLog)
    if execution_id:
        query = query.filter(AutomationAuditLog.execution_id == execution_id)
    return query.order_by(AutomationAuditLog.timestamp.desc()).limit(limit).all()
