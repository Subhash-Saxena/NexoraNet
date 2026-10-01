"""NexoraNet Hands-on Lab Service.

Coordinates lab lifecycle, step execution, scoring recalculation,
answer submission, attempt histories, and aggregate student telemetry.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.enums import AttemptStatus, DifficultyLevel, LabStatus
from app.models.lab import Lab, LabStep
from app.models.progress import LabAttempt, LabStepSubmission
from app.models.user import User
from app.schemas.lab import (
    LabAttemptBrief,
    LabAttemptDetail,
    LabBriefResponse,
    LabDetailResponse,
    LabQuestionBrief,
    LabStepDetail,
    LabStepSubmissionBrief,
    LabStepSubmissionDetail,
    LabTelemetryResponse,
    StepSubmitResponse,
)
from app.services.lab_validator import (
    shield_answer_data_for_student,
    validate_lab_answer,
)

logger = logging.getLogger("nexoranet.lab_service")


def get_current_dev_user(db: Session) -> User:
    """Retrieve active development user for zero-auth prototype workflows."""
    user = db.query(User).filter(User.username == "student_dev").first()
    if not user:
        user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No student user accounts found in database. Please run seeding script.",
        )
    return user


def _parse_json_list(val: str | None) -> list[str]:
    """Parse JSON array or newline-delimited text into list of strings."""
    if not val:
        return []
    try:
        parsed = json.loads(val)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
        return [str(parsed)]
    except (json.JSONDecodeError, TypeError, ValueError):
        return [line.strip() for line in val.split("\n") if line.strip()]


def list_labs(
    db: Session,
    user_id: int,
    difficulty: DifficultyLevel | None = None,
    topic_id: int | None = None,
    environment: str | None = None,
    status_filter: str | None = None,
    q: str | None = None,
) -> list[LabBriefResponse]:
    """
    List published labs with user attempt status and score summaries.
    """
    query = (
        db.query(Lab)
        .options(
            joinedload(Lab.topic),
            selectinload(Lab.steps),
        )
        .filter(Lab.is_published.is_(True), Lab.status == LabStatus.PUBLISHED)
    )

    if difficulty:
        query = query.filter(Lab.difficulty == difficulty)
    if topic_id:
        query = query.filter(Lab.topic_id == topic_id)
    if environment:
        query = query.filter(func.upper(Lab.environment_type) == environment.upper())
    if q:
        search_term = f"%{q.strip().lower()}%"
        query = query.filter(
            func.lower(Lab.title).like(search_term)
            | func.lower(Lab.description).like(search_term)
        )

    labs = query.order_by(Lab.id).all()

    # Pre-fetch user attempts for these labs
    lab_ids = [lab.id for lab in labs]
    attempts_map: dict[int, list[LabAttempt]] = {}
    if lab_ids:
        attempts = (
            db.query(LabAttempt)
            .filter(LabAttempt.user_id == user_id, LabAttempt.lab_id.in_(lab_ids))
            .order_by(LabAttempt.id.desc())
            .all()
        )
        for att in attempts:
            attempts_map.setdefault(att.lab_id, []).append(att)

    result: list[LabBriefResponse] = []
    for lab in labs:
        lab_attempts = attempts_map.get(lab.id, [])
        user_status = "NOT_STARTED"
        latest_score: float | None = None

        if lab_attempts:
            # Check if any attempt is completed
            completed_att = next((a for a in lab_attempts if a.status == AttemptStatus.COMPLETED), None)
            if completed_att:
                user_status = "COMPLETED"
                latest_score = completed_att.percentage
            elif any(a.status == AttemptStatus.IN_PROGRESS for a in lab_attempts):
                user_status = "IN_PROGRESS"
                latest_score = lab_attempts[0].percentage
            else:
                user_status = lab_attempts[0].status.value
                latest_score = lab_attempts[0].percentage

        if status_filter and status_filter.upper() != "ALL" and user_status.upper() != status_filter.upper():
            continue

        total_pts = sum(s.points for s in lab.steps)
        result.append(
            LabBriefResponse(
                id=lab.id,
                topic_id=lab.topic_id,
                topic_title=lab.topic.title if lab.topic else "General Networking",
                topic_slug=lab.topic.slug if lab.topic else "general",
                title=lab.title,
                slug=lab.slug,
                description=lab.description,
                difficulty=lab.difficulty,
                estimated_minutes=lab.estimated_minutes,
                environment_type=lab.environment_type,
                status=lab.status,
                is_published=lab.is_published,
                total_steps=len(lab.steps),
                total_points=total_pts,
                user_status=user_status,
                latest_score_percentage=latest_score,
            )
        )

    return result


def get_lab_detail(
    db: Session,
    user_id: int,
    lab_id_or_slug: str | int,
) -> LabDetailResponse:
    """
    Retrieve complete lab workspace data with sanitized question models
    and the user's active or latest attempt context.
    """
    query = (
        db.query(Lab)
        .options(
            joinedload(Lab.topic),
            selectinload(Lab.steps).selectinload(LabStep.questions),
        )
        .filter(Lab.is_published.is_(True))
    )

    if isinstance(lab_id_or_slug, int) or str(lab_id_or_slug).isdigit():
        lab = query.filter(Lab.id == int(lab_id_or_slug)).first()
    else:
        lab = query.filter(Lab.slug == str(lab_id_or_slug)).first()

    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab '{lab_id_or_slug}' was not found.",
        )

    # Fetch user's latest attempt for this lab
    active_attempt = (
        db.query(LabAttempt)
        .options(selectinload(LabAttempt.step_submissions))
        .filter(LabAttempt.user_id == user_id, LabAttempt.lab_id == lab.id)
        .order_by(LabAttempt.id.desc())
        .first()
    )

    submissions_map: dict[int, LabStepSubmission] = {}
    if active_attempt:
        for sub in active_attempt.step_submissions:
            # Map by step_id (keep latest or correct)
            if sub.step_id not in submissions_map or sub.is_correct:
                submissions_map[sub.step_id] = sub

    steps_payload: list[LabStepDetail] = []
    total_points = 0

    for step in sorted(lab.steps, key=lambda s: s.step_number):
        total_points += step.points
        sub = submissions_map.get(step.id)

        # Build questions for step
        q_payload: list[LabQuestionBrief] = []
        for q in sorted(step.questions, key=lambda q: q.order_index):
            safe_cfg = shield_answer_data_for_student(
                q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                q.answer_data,
            )
            q_payload.append(
                LabQuestionBrief(
                    id=q.id,
                    step_id=q.step_id,
                    question_text=q.question_text,
                    question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
                    points=q.points,
                    order_index=q.order_index,
                    safe_input_config=safe_cfg,
                )
            )

        # Primary safe input configuration for the step
        # If questions exist, use the first question's safe config, or fall back to step validation type
        if step.questions:
            primary_q = step.questions[0]
            step_safe_cfg = shield_answer_data_for_student(
                primary_q.question_type.value if hasattr(primary_q.question_type, "value") else str(primary_q.question_type),
                primary_q.answer_data,
            )
        else:
            step_safe_cfg = shield_answer_data_for_student(step.validation_type, {})

        sub_brief = (
            LabStepSubmissionBrief(
                id=sub.id,
                step_id=sub.step_id,
                submitted_answer=sub.submitted_answer,
                is_correct=sub.is_correct,
                points_earned=sub.points_earned,
                hint_used=sub.hint_used,
                feedback=sub.feedback,
                submitted_at=sub.submitted_at,
            )
            if sub
            else None
        )

        steps_payload.append(
            LabStepDetail(
                id=step.id,
                step_number=step.step_number,
                title=step.title,
                description=step.description,
                instructions=step.instructions,
                hint=step.hint,
                expected_observation=step.expected_observation,
                validation_type=step.validation_type,
                points=step.points,
                is_required=step.is_required,
                safe_input_config=step_safe_cfg,
                questions=q_payload,
                is_completed=sub.is_correct if sub else False,
                points_earned=sub.points_earned if sub else 0.0,
                latest_submission=sub_brief,
            )
        )

    return LabDetailResponse(
        id=lab.id,
        topic_id=lab.topic_id,
        topic_title=lab.topic.title if lab.topic else "General Networking",
        topic_slug=lab.topic.slug if lab.topic else "general",
        title=lab.title,
        slug=lab.slug,
        description=lab.description,
        difficulty=lab.difficulty,
        estimated_minutes=lab.estimated_minutes,
        environment_type=lab.environment_type,
        instructions=lab.instructions,
        objectives=_parse_json_list(lab.objectives),
        prerequisites=_parse_json_list(lab.prerequisites),
        status=lab.status,
        is_published=lab.is_published,
        total_steps=len(steps_payload),
        total_points=total_points,
        steps=steps_payload,
        active_attempt_id=active_attempt.id if active_attempt else None,
        active_attempt_status=active_attempt.status.value if active_attempt else None,
        active_attempt_score=active_attempt.score if active_attempt else 0.0,
        active_attempt_percentage=active_attempt.percentage if active_attempt else 0.0,
        active_attempt_time_taken=active_attempt.time_taken_seconds if active_attempt else None,
        attempt_number=active_attempt.attempt_number if active_attempt else 1,
    )


def start_lab(
    db: Session,
    user_id: int,
    lab_id_or_slug: str | int,
) -> LabDetailResponse:
    """
    Start or resume a student attempt for the target lab (idempotent).
    """
    # 1. Resolve lab
    if isinstance(lab_id_or_slug, int) or str(lab_id_or_slug).isdigit():
        lab = db.query(Lab).filter(Lab.id == int(lab_id_or_slug)).first()
    else:
        lab = db.query(Lab).filter(Lab.slug == str(lab_id_or_slug)).first()

    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab '{lab_id_or_slug}' was not found.",
        )

    # 2. Check for active IN_PROGRESS attempt
    active_attempt = (
        db.query(LabAttempt)
        .filter(
            LabAttempt.user_id == user_id,
            LabAttempt.lab_id == lab.id,
            LabAttempt.status == AttemptStatus.IN_PROGRESS,
        )
        .first()
    )

    if not active_attempt:
        # Calculate attempt number
        prev_attempts_count = (
            db.query(func.count(LabAttempt.id))
            .filter(LabAttempt.user_id == user_id, LabAttempt.lab_id == lab.id)
            .scalar()
            or 0
        )
        total_points = sum(s.points for s in lab.steps if s.is_required) or 10.0

        active_attempt = LabAttempt(
            user_id=user_id,
            lab_id=lab.id,
            attempt_number=prev_attempts_count + 1,
            status=AttemptStatus.IN_PROGRESS,
            score=0.0,
            total_points=float(total_points),
            percentage=0.0,
            started_at=datetime.now(timezone.utc),
        )
        db.add(active_attempt)
        db.commit()
        db.refresh(active_attempt)
        logger.info(
            "Created LabAttempt #%d for user %d in lab %s",
            active_attempt.attempt_number,
            user_id,
            lab.title,
        )

    return get_lab_detail(db, user_id, lab.id)


def submit_lab_step(
    db: Session,
    user_id: int,
    attempt_id: int,
    step_id: int,
    submitted_answer: Any,
    hint_used: bool = False,
) -> StepSubmitResponse:
    """
    Validate a step's submitted answer, record submission idempotently,
    recalculate attempt score, and transition to COMPLETED if all required steps pass.
    """
    # 1. Fetch attempt and security check
    attempt = (
        db.query(LabAttempt)
        .options(
            joinedload(LabAttempt.lab).selectinload(Lab.steps),
            selectinload(LabAttempt.step_submissions),
        )
        .filter(LabAttempt.id == attempt_id)
        .first()
    )
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab attempt #{attempt_id} was not found.",
        )

    if attempt.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized attempt access.",
        )

    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This attempt is already finalized. Please start a retry to submit new answers.",
        )

    # 2. Fetch step and verify association
    step = (
        db.query(LabStep)
        .options(selectinload(LabStep.questions))
        .filter(LabStep.id == step_id, LabStep.lab_id == attempt.lab_id)
        .first()
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step #{step_id} does not belong to this lab.",
        )

    # 3. Determine validation rule & run validation
    question = step.questions[0] if step.questions else None
    if question:
        vtype = question.question_type.value if hasattr(question.question_type, "value") else str(question.question_type)
        raw_answer_data = question.answer_data
        step_pts = question.points
    else:
        vtype = step.validation_type
        raw_answer_data = step.hint or "{}"
        step_pts = step.points

    val_result = validate_lab_answer(
        validation_type=vtype,
        submitted_answer=submitted_answer,
        answer_data=raw_answer_data,
        points=step_pts,
    )

    # 4. Idempotent recording of submission
    now = datetime.now(timezone.utc)
    submission = (
        db.query(LabStepSubmission)
        .filter(
            LabStepSubmission.attempt_id == attempt.id,
            LabStepSubmission.step_id == step.id,
        )
        .first()
    )

    answer_repr = (
        json.dumps(submitted_answer)
        if isinstance(submitted_answer, (dict, list))
        else str(submitted_answer)
    )

    if not submission:
        submission = LabStepSubmission(
            attempt_id=attempt.id,
            step_id=step.id,
            question_id=question.id if question else None,
            attempt_number=attempt.attempt_number,
            submitted_answer=answer_repr,
            is_correct=val_result.is_correct,
            points_earned=val_result.points_earned,
            hint_used=hint_used,
            feedback=val_result.feedback,
            submitted_at=now,
        )
        db.add(submission)
    else:
        # If previously correct, do not overwrite with incorrect
        if not (submission.is_correct and not val_result.is_correct):
            submission.submitted_answer = answer_repr
            submission.is_correct = val_result.is_correct
            submission.points_earned = val_result.points_earned
            submission.feedback = val_result.feedback
            submission.submitted_at = now
            if hint_used:
                submission.hint_used = True

    db.flush()

    # 5. Recalculate Attempt Progress & Score
    all_subs = (
        db.query(LabStepSubmission)
        .filter(LabStepSubmission.attempt_id == attempt.id)
        .all()
    )
    earned_points = sum(s.points_earned for s in all_subs)
    total_possible_points = sum(s.points for s in attempt.lab.steps if s.is_required) or 10.0

    pct = round((earned_points / total_possible_points) * 100, 1)
    attempt.score = earned_points
    attempt.total_points = float(total_possible_points)
    attempt.percentage = min(pct, 100.0)

    # Check if all required steps are completed correctly
    required_step_ids = {s.id for s in attempt.lab.steps if s.is_required}
    correct_step_ids = {s.step_id for s in all_subs if s.is_correct}
    is_completed = required_step_ids.issubset(correct_step_ids)

    if is_completed:
        attempt.status = AttemptStatus.COMPLETED
        attempt.completed_at = now
        started = attempt.started_at
        if started:
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            attempt.time_taken_seconds = max(1, int((now - started).total_seconds()))

    db.commit()
    db.refresh(attempt)

    return StepSubmitResponse(
        step_id=step.id,
        attempt_id=attempt.id,
        is_correct=val_result.is_correct,
        points_earned=val_result.points_earned,
        max_points=val_result.max_points,
        feedback=val_result.feedback,
        explanation=val_result.explanation,
        attempt_score=attempt.score,
        attempt_total_points=attempt.total_points,
        attempt_percentage=attempt.percentage,
        is_lab_completed=attempt.status == AttemptStatus.COMPLETED,
    )


def retry_lab(
    db: Session,
    user_id: int,
    attempt_id: int,
) -> LabDetailResponse:
    """
    Abandon or finalize active attempt and launch a brand new attempt
    while fully preserving past submission records.
    """
    old_attempt = db.query(LabAttempt).filter(LabAttempt.id == attempt_id).first()
    if not old_attempt or old_attempt.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target lab attempt not found.",
        )

    if old_attempt.status == AttemptStatus.IN_PROGRESS:
        old_attempt.status = AttemptStatus.ABANDONED
        db.flush()

    # Create new attempt
    lab = old_attempt.lab
    total_points = sum(s.points for s in lab.steps if s.is_required) or 10.0
    new_attempt = LabAttempt(
        user_id=user_id,
        lab_id=lab.id,
        attempt_number=old_attempt.attempt_number + 1,
        status=AttemptStatus.IN_PROGRESS,
        score=0.0,
        total_points=float(total_points),
        percentage=0.0,
        started_at=datetime.now(timezone.utc),
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return get_lab_detail(db, user_id, lab.id)


def list_user_attempts(
    db: Session,
    user_id: int,
) -> list[LabAttemptBrief]:
    """
    List historical lab attempts for the active student.
    """
    attempts = (
        db.query(LabAttempt)
        .options(joinedload(LabAttempt.lab))
        .filter(LabAttempt.user_id == user_id)
        .order_by(LabAttempt.started_at.desc())
        .all()
    )

    return [
        LabAttemptBrief(
            id=a.id,
            lab_id=a.lab_id,
            lab_title=a.lab.title if a.lab else "Unknown Lab",
            lab_slug=a.lab.slug if a.lab else "unknown",
            lab_difficulty=a.lab.difficulty.value if a.lab and hasattr(a.lab.difficulty, "value") else "BEGINNER",
            lab_environment=a.lab.environment_type if a.lab else "LOCAL_SYSTEM",
            attempt_number=a.attempt_number,
            status=a.status,
            score=a.score,
            total_points=a.total_points,
            percentage=a.percentage,
            started_at=a.started_at,
            completed_at=a.completed_at,
            time_taken_seconds=a.time_taken_seconds,
        )
        for a in attempts
    ]


def get_attempt_detail(
    db: Session,
    user_id: int,
    attempt_id: int,
) -> LabAttemptDetail:
    """
    Full review of an attempt with submitted answers and evaluations.
    """
    attempt = (
        db.query(LabAttempt)
        .options(
            joinedload(LabAttempt.lab).selectinload(Lab.steps),
            selectinload(LabAttempt.step_submissions).joinedload(LabStepSubmission.step),
            selectinload(LabAttempt.step_submissions).joinedload(LabStepSubmission.question),
        )
        .filter(LabAttempt.id == attempt_id)
        .first()
    )
    if not attempt or attempt.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab attempt not found.",
        )

    subs_payload: list[LabStepSubmissionDetail] = []
    for sub in attempt.step_submissions:
        step = sub.step
        explanation = None
        if sub.question and sub.question.explanation:
            explanation = sub.question.explanation
        elif step and step.hint:
            explanation = step.hint

        subs_payload.append(
            LabStepSubmissionDetail(
                step_id=sub.step_id,
                step_number=step.step_number if step else 1,
                step_title=step.title if step else f"Step {sub.step_id}",
                submitted_answer=sub.submitted_answer,
                is_correct=sub.is_correct,
                points_earned=sub.points_earned,
                max_points=float(step.points if step else 10),
                hint_used=sub.hint_used,
                feedback=sub.feedback,
                explanation=explanation,
                submitted_at=sub.submitted_at,
            )
        )

    return LabAttemptDetail(
        id=attempt.id,
        lab_id=attempt.lab_id,
        lab_title=attempt.lab.title if attempt.lab else "Unknown Lab",
        lab_slug=attempt.lab.slug if attempt.lab else "unknown",
        lab_difficulty=attempt.lab.difficulty.value if attempt.lab and hasattr(attempt.lab.difficulty, "value") else "BEGINNER",
        attempt_number=attempt.attempt_number,
        status=attempt.status,
        score=attempt.score,
        total_points=attempt.total_points,
        percentage=attempt.percentage,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_taken_seconds=attempt.time_taken_seconds,
        submissions=subs_payload,
    )


def get_lab_telemetry(
    db: Session,
    user_id: int,
) -> LabTelemetryResponse:
    """
    Calculate aggregate lab progress metrics for student dashboard.
    """
    all_labs = db.query(Lab).filter(Lab.is_published.is_(True), Lab.status == LabStatus.PUBLISHED).all()
    total_labs = len(all_labs)

    # Completed distinct labs
    completed_lab_ids = {
        row[0]
        for row in db.query(LabAttempt.lab_id)
        .filter(LabAttempt.user_id == user_id, LabAttempt.status == AttemptStatus.COMPLETED)
        .distinct()
        .all()
    }

    # In-progress distinct labs
    in_progress_lab_ids = {
        row[0]
        for row in db.query(LabAttempt.lab_id)
        .filter(LabAttempt.user_id == user_id, LabAttempt.status == AttemptStatus.IN_PROGRESS)
        .distinct()
        .all()
        if row[0] not in completed_lab_ids
    }

    # Average score
    avg_score_row = (
        db.query(func.avg(LabAttempt.percentage))
        .filter(LabAttempt.user_id == user_id, LabAttempt.status == AttemptStatus.COMPLETED)
        .scalar()
    )
    avg_score = round(float(avg_score_row), 1) if avg_score_row is not None else 0.0

    beginner_total = sum(1 for l in all_labs if l.difficulty == DifficultyLevel.BEGINNER)
    beginner_completed = sum(1 for l in all_labs if l.difficulty == DifficultyLevel.BEGINNER and l.id in completed_lab_ids)

    intermediate_total = sum(1 for l in all_labs if l.difficulty == DifficultyLevel.INTERMEDIATE)
    intermediate_completed = sum(1 for l in all_labs if l.difficulty == DifficultyLevel.INTERMEDIATE and l.id in completed_lab_ids)

    advanced_total = sum(1 for l in all_labs if l.difficulty == DifficultyLevel.ADVANCED)
    advanced_completed = sum(1 for l in all_labs if l.difficulty == DifficultyLevel.ADVANCED and l.id in completed_lab_ids)

    return LabTelemetryResponse(
        total_labs=total_labs,
        completed_labs=len(completed_lab_ids),
        in_progress_labs=len(in_progress_lab_ids),
        average_score=avg_score,
        beginner_completed=beginner_completed,
        beginner_total=beginner_total,
        intermediate_completed=intermediate_completed,
        intermediate_total=intermediate_total,
        advanced_completed=advanced_completed,
        advanced_total=advanced_total,
    )
