import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.enums import (
    AttemptStatus,
    DifficultyLevel,
    MockTestStatus,
    MockTestType,
)
from app.models.mock_test import (
    MockTest,
    MockTestAttempt,
    MockTestQuestion,
    StudentAnswer,
    TestResult,
)
from app.models.question import Question, QuestionOption
from app.schemas.mock_test import (
    AttemptHistoryItem,
    AttemptStatusResponse,
    DifficultyPerformanceResponse,
    QuestionReviewItem,
    ReviewOptionItem,
    SaveAnswerResponse,
    StartAttemptResponse,
    StudentAnswerBrief,
    StudentOptionBrief,
    StudentQuestionPayload,
    TestResultResponse,
    TestReviewResponse,
    TopicPerformanceResponse,
)
from app.services.scoring_service import scoring_service


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure a datetime object is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class TestAttemptService:
    """Service managing examination attempts, timer synchronization, submissions, and reviews."""

    @staticmethod
    def start_or_resume_attempt(
        user_id: int,
        test_id_or_slug: str | int,
        retake: bool = False,
        db: Session = None,
    ) -> StartAttemptResponse:
        """
        Start a new test sitting or resume an active, unexpired sitting.
        Generates server-authoritative expiration timestamps.
        """
        base_query = (
            db.query(MockTest)
            .options(
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.options),
                selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
            )
        )

        if isinstance(test_id_or_slug, int) or str(test_id_or_slug).isdigit():
            mt = base_query.filter(MockTest.id == int(test_id_or_slug)).first()
        else:
            mt = base_query.filter(MockTest.slug == str(test_id_or_slug)).first()

        if not mt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mock test '{test_id_or_slug}' not found.",
            )

        if mt.status != MockTestStatus.PUBLISHED or len(mt.test_questions) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mock test '{mt.title}' is currently not ready for examination (Status: {mt.status.value}). Insufficient questions in the bank pool.",
            )

        now = datetime.now(timezone.utc)
        attempt: MockTestAttempt | None = None

        if not retake:
            # Check for existing IN_PROGRESS attempt
            existing = (
                db.query(MockTestAttempt)
                .filter(
                    MockTestAttempt.mock_test_id == mt.id,
                    MockTestAttempt.user_id == user_id,
                    MockTestAttempt.status == AttemptStatus.IN_PROGRESS,
                )
                .order_by(MockTestAttempt.id.desc())
                .first()
            )

            if existing:
                expires_at = _ensure_utc(existing.expires_at)
                if now >= expires_at:
                    # Expired — auto finalize
                    TestAttemptService._finalize_expired_attempt(existing, db)
                else:
                    attempt = existing

        # If no active attempt, create a new one
        if not attempt:
            expires_at = now + timedelta(minutes=mt.duration_minutes)
            attempt = MockTestAttempt(
                mock_test_id=mt.id,
                user_id=user_id,
                started_at=now,
                expires_at=expires_at,
                status=AttemptStatus.IN_PROGRESS,
                score=0.0,
                percentage=0.0,
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)

        # Prepare shielded questions payload
        questions_payload: list[StudentQuestionPayload] = []
        ordered_links = sorted(mt.test_questions, key=lambda l: l.order_index)

        for idx, link in enumerate(ordered_links):
            q = link.question
            if not q:
                continue

            # Shielded options (NO is_correct, NO explanation)
            options_payload = [
                StudentOptionBrief(
                    id=opt.id,
                    option_text=opt.option_text,
                    order_index=opt.order_index,
                )
                for opt in sorted(q.options, key=lambda o: o.order_index)
            ]

            questions_payload.append(
                StudentQuestionPayload(
                    id=q.id,
                    question_number=idx + 1,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    points=link.points or q.points,
                    topic_title=q.topic.title if q.topic else "General",
                    difficulty=q.difficulty,
                    options=options_payload,
                )
            )

        # Fetch existing student answers for this attempt
        saved_answers: list[StudentAnswerBrief] = []
        answers_query = (
            db.query(StudentAnswer)
            .filter(StudentAnswer.attempt_id == attempt.id)
            .all()
        )
        for ans in answers_query:
            selected_ids = []
            if ans.answer_data:
                try:
                    data = json.loads(ans.answer_data)
                    if isinstance(data, list):
                        selected_ids = [int(x) for x in data]
                except (json.JSONDecodeError, ValueError):
                    pass

            saved_answers.append(
                StudentAnswerBrief(
                    question_id=ans.question_id,
                    selected_option_ids=selected_ids,
                    is_marked_for_review=ans.is_marked_for_review,
                    answered_at=_ensure_utc(ans.answered_at).isoformat(),
                )
            )

        expires_utc = _ensure_utc(attempt.expires_at)
        remaining_seconds = max(0, int((expires_utc - now).total_seconds()))

        return StartAttemptResponse(
            attempt_id=attempt.id,
            test_id=mt.id,
            test_title=mt.title,
            test_slug=mt.slug,
            duration_minutes=mt.duration_minutes,
            passing_percentage=mt.passing_percentage,
            started_at=_ensure_utc(attempt.started_at).isoformat(),
            expires_at=expires_utc.isoformat(),
            remaining_seconds=remaining_seconds,
            status=attempt.status,
            questions=questions_payload,
            saved_answers=saved_answers,
        )

    @staticmethod
    def save_answer(
        attempt_id: int,
        user_id: int,
        question_id: int,
        selected_option_ids: list[int],
        is_marked_for_review: bool | None,
        db: Session,
    ) -> SaveAnswerResponse:
        """
        Record or update an individual question response.
        Enforces server-authoritative timer and security boundaries.
        """
        attempt = db.query(MockTestAttempt).filter(MockTestAttempt.id == attempt_id).first()
        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot save answer. Attempt status is already {attempt.status}.",
            )

        # Check server expiration
        now = datetime.now(timezone.utc)
        expires_at = _ensure_utc(attempt.expires_at)
        if now >= expires_at:
            TestAttemptService._finalize_expired_attempt(attempt, db)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Examination time has expired. The test has been automatically submitted.",
            )

        # Validate that question belongs to this test
        link = (
            db.query(MockTestQuestion)
            .filter(
                MockTestQuestion.mock_test_id == attempt.mock_test_id,
                MockTestQuestion.question_id == question_id,
            )
            .first()
        )
        if not link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {question_id} does not belong to mock test {attempt.mock_test_id}.",
            )

        # Validate that options belong to the question
        if selected_option_ids:
            valid_options = (
                db.query(QuestionOption)
                .filter(
                    QuestionOption.question_id == question_id,
                    QuestionOption.id.in_(selected_option_ids),
                )
                .all()
            )
            if len(valid_options) != len(selected_option_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more selected option IDs do not belong to this question.",
                )

        # Idempotent upsert
        student_ans = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.attempt_id == attempt_id,
                StudentAnswer.question_id == question_id,
            )
            .first()
        )

        json_answer = json.dumps(selected_option_ids)
        if student_ans:
            student_ans.answer_data = json_answer
            student_ans.answered_at = now
            if is_marked_for_review is not None:
                student_ans.is_marked_for_review = is_marked_for_review
        else:
            student_ans = StudentAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                answer_data=json_answer,
                is_correct=False,
                points_earned=0,
                is_marked_for_review=bool(is_marked_for_review),
                answered_at=now,
            )
            db.add(student_ans)

        db.commit()

        return SaveAnswerResponse(
            success=True,
            question_id=question_id,
            selected_option_ids=selected_option_ids,
            is_marked_for_review=student_ans.is_marked_for_review,
            message="Answer recorded successfully.",
        )

    @staticmethod
    def clear_answer(
        attempt_id: int,
        user_id: int,
        question_id: int,
        db: Session,
    ) -> SaveAnswerResponse:
        """Clear the answer for a given question while preserving review flags."""
        attempt = db.query(MockTestAttempt).filter(MockTestAttempt.id == attempt_id).first()
        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot clear answer. Attempt status is {attempt.status}.",
            )

        now = datetime.now(timezone.utc)
        if now >= _ensure_utc(attempt.expires_at):
            TestAttemptService._finalize_expired_attempt(attempt, db)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Examination time has expired.",
            )

        student_ans = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.attempt_id == attempt_id,
                StudentAnswer.question_id == question_id,
            )
            .first()
        )
        is_marked = False
        if student_ans:
            student_ans.answer_data = "[]"
            student_ans.answered_at = now
            is_marked = student_ans.is_marked_for_review
            db.commit()

        return SaveAnswerResponse(
            success=True,
            question_id=question_id,
            selected_option_ids=[],
            is_marked_for_review=is_marked,
            message="Answer choice cleared.",
        )

    @staticmethod
    def mark_question(
        attempt_id: int,
        user_id: int,
        question_id: int,
        is_marked: bool | None = None,
        is_marked_for_review: bool | None = None,
        db: Session = None,
    ) -> SaveAnswerResponse:
        """Toggle question mark for review flag."""
        flag_val = is_marked if is_marked is not None else (is_marked_for_review if is_marked_for_review is not None else True)
        attempt = db.query(MockTestAttempt).filter(MockTestAttempt.id == attempt_id).first()
        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot mark question. Attempt status is {attempt.status}.",
            )

        now = datetime.now(timezone.utc)
        if now >= _ensure_utc(attempt.expires_at):
            TestAttemptService._finalize_expired_attempt(attempt, db)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Examination time has expired.",
            )

        student_ans = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.attempt_id == attempt_id,
                StudentAnswer.question_id == question_id,
            )
            .first()
        )
        if student_ans:
            student_ans.is_marked_for_review = flag_val
        else:
            student_ans = StudentAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                answer_data="[]",
                is_correct=False,
                points_earned=0,
                is_marked_for_review=flag_val,
                answered_at=now,
            )
            db.add(student_ans)

        db.commit()

        selected_ids: list[int] = []
        if student_ans and student_ans.answer_data:
            try:
                selected_ids = [int(x) for x in json.loads(student_ans.answer_data)]
            except (json.JSONDecodeError, ValueError):
                pass

        return SaveAnswerResponse(
            success=True,
            question_id=question_id,
            selected_option_ids=selected_ids,
            is_marked_for_review=flag_val,
            message="Question review marker updated.",
        )

    @staticmethod
    def submit_attempt(
        attempt_id: int,
        user_id: int,
        db: Session,
    ) -> TestResultResponse:
        """
        Finalize and score an examination attempt.
        Calculates pass/fail, updates test results, and unlocks review data.
        """
        attempt = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.options),
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTestAttempt.student_answers),
                selectinload(MockTestAttempt.result),
            )
            .filter(MockTestAttempt.id == attempt_id)
            .first()
        )

        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        # If already submitted or expired, return the result
        if attempt.status in (AttemptStatus.SUBMITTED, AttemptStatus.EXPIRED):
            return TestAttemptService.get_attempt_result(attempt_id, user_id, db)

        now = datetime.now(timezone.utc)
        expires_at = _ensure_utc(attempt.expires_at)
        started_at = _ensure_utc(attempt.started_at)

        is_expired = now >= expires_at
        final_status = AttemptStatus.EXPIRED if is_expired else AttemptStatus.SUBMITTED

        # Score attempt
        mt = attempt.mock_test
        scoring_res = scoring_service.score_attempt(
            attempt=attempt,
            test_questions=mt.test_questions,
            student_answers=attempt.student_answers,
            passing_percentage=mt.passing_percentage,
        )

        # Elapsed time
        time_used = max(0, int((now - started_at).total_seconds()))
        max_duration_seconds = mt.duration_minutes * 60
        if is_expired:
            time_used = min(time_used, max_duration_seconds)

        attempt.status = final_status
        attempt.submitted_at = now
        attempt.score = scoring_res.score
        attempt.percentage = scoring_res.percentage

        # Upsert TestResult
        test_result = attempt.result
        if not test_result:
            test_result = TestResult(
                attempt_id=attempt.id,
                correct_answers=scoring_res.correct_answers,
                incorrect_answers=scoring_res.incorrect_answers,
                unanswered=scoring_res.unanswered_questions,
                total_questions=scoring_res.total_questions,
                score=scoring_res.score,
                total_points=scoring_res.total_points,
                earned_points=scoring_res.earned_points,
                percentage=scoring_res.percentage,
                passing_percentage=scoring_res.passing_percentage,
                passed=scoring_res.passed,
                time_taken_seconds=time_used,
            )
            db.add(test_result)
        else:
            test_result.correct_answers = scoring_res.correct_answers
            test_result.incorrect_answers = scoring_res.incorrect_answers
            test_result.unanswered = scoring_res.unanswered_questions
            test_result.total_questions = scoring_res.total_questions
            test_result.score = scoring_res.score
            test_result.total_points = scoring_res.total_points
            test_result.earned_points = scoring_res.earned_points
            test_result.percentage = scoring_res.percentage
            test_result.passing_percentage = scoring_res.passing_percentage
            test_result.passed = scoring_res.passed
            test_result.time_taken_seconds = time_used

        db.commit()
        db.refresh(test_result)

        return TestResultResponse(
            attempt_id=attempt.id,
            test_id=mt.id,
            test_title=mt.title,
            test_slug=mt.slug,
            status=attempt.status,
            score=scoring_res.score,
            percentage=scoring_res.percentage,
            total_points=scoring_res.total_points,
            earned_points=scoring_res.earned_points,
            passing_percentage=scoring_res.passing_percentage,
            passed=scoring_res.passed,
            total_questions=scoring_res.total_questions,
            attempted_questions=scoring_res.attempted_questions,
            unanswered_questions=scoring_res.unanswered_questions,
            correct_answers=scoring_res.correct_answers,
            incorrect_answers=scoring_res.incorrect_answers,
            time_taken_seconds=time_used,
            started_at=started_at.isoformat(),
            submitted_at=now.isoformat(),
            topic_breakdown=[
                TopicPerformanceResponse(**t) for t in scoring_res.topic_breakdown
            ],
            difficulty_breakdown=[
                DifficultyPerformanceResponse(**d) for d in scoring_res.difficulty_breakdown
            ],
        )

    @staticmethod
    def get_attempt_status(
        attempt_id: int,
        user_id: int,
        db: Session,
    ) -> AttemptStatusResponse:
        """Query authoritative server-side timer and progress status."""
        attempt = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test).selectinload(MockTest.test_questions),
                selectinload(MockTestAttempt.student_answers),
            )
            .filter(MockTestAttempt.id == attempt_id)
            .first()
        )

        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        now = datetime.now(timezone.utc)
        expires_at = _ensure_utc(attempt.expires_at)
        started_at = _ensure_utc(attempt.started_at)
        is_expired = now >= expires_at

        # If expired during sitting, auto-finalize
        if is_expired and attempt.status == AttemptStatus.IN_PROGRESS:
            TestAttemptService._finalize_expired_attempt(attempt, db)
            db.refresh(attempt)

        remaining_seconds = max(0, int((expires_at - now).total_seconds())) if not is_expired else 0

        # Count answered & marked
        answered_count = 0
        marked_count = 0
        for ans in attempt.student_answers:
            if ans.is_marked_for_review:
                marked_count += 1
            if ans.answer_data and ans.answer_data not in ("[]", ""):
                try:
                    data = json.loads(ans.answer_data)
                    if data:
                        answered_count += 1
                except (json.JSONDecodeError, ValueError):
                    pass

        total_q = len(attempt.mock_test.test_questions) if attempt.mock_test else 0

        return AttemptStatusResponse(
            attempt_id=attempt.id,
            status=attempt.status,
            started_at=started_at.isoformat(),
            expires_at=expires_at.isoformat(),
            remaining_seconds=remaining_seconds,
            is_expired=is_expired,
            answered_count=answered_count,
            marked_count=marked_count,
            total_questions=total_q,
        )

    @staticmethod
    def get_attempt_result(
        attempt_id: int,
        user_id: int,
        db: Session,
    ) -> TestResultResponse:
        """Fetch exam performance scorecard and breakdowns."""
        attempt = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.options),
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTestAttempt.student_answers),
                selectinload(MockTestAttempt.result),
            )
            .filter(MockTestAttempt.id == attempt_id)
            .first()
        )

        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        if attempt.status == AttemptStatus.IN_PROGRESS:
            now = datetime.now(timezone.utc)
            if now >= _ensure_utc(attempt.expires_at):
                return TestAttemptService.submit_attempt(attempt_id, user_id, db)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test is still in progress. Submit the test to view results.",
            )

        mt = attempt.mock_test
        scoring_res = scoring_service.score_attempt(
            attempt=attempt,
            test_questions=mt.test_questions,
            student_answers=attempt.student_answers,
            passing_percentage=mt.passing_percentage,
        )

        res = attempt.result
        time_taken = res.time_taken_seconds if res else 0

        return TestResultResponse(
            attempt_id=attempt.id,
            test_id=mt.id,
            test_title=mt.title,
            test_slug=mt.slug,
            status=attempt.status,
            score=attempt.score,
            percentage=attempt.percentage,
            total_points=scoring_res.total_points,
            earned_points=scoring_res.earned_points,
            passing_percentage=mt.passing_percentage,
            passed=res.passed if res else scoring_res.passed,
            total_questions=scoring_res.total_questions,
            attempted_questions=scoring_res.attempted_questions,
            unanswered_questions=scoring_res.unanswered_questions,
            correct_answers=scoring_res.correct_answers,
            incorrect_answers=scoring_res.incorrect_answers,
            time_taken_seconds=time_taken,
            started_at=_ensure_utc(attempt.started_at).isoformat(),
            submitted_at=_ensure_utc(attempt.submitted_at).isoformat() if attempt.submitted_at else None,
            topic_breakdown=[
                TopicPerformanceResponse(**t) for t in scoring_res.topic_breakdown
            ],
            difficulty_breakdown=[
                DifficultyPerformanceResponse(**d) for d in scoring_res.difficulty_breakdown
            ],
        )

    @staticmethod
    def get_attempt_review(
        attempt_id: int,
        user_id: int,
        db: Session,
    ) -> TestReviewResponse:
        """
        Provide in-depth post-exam question review.
        Reveals correct options and pedagogical explanations only after submission.
        """
        attempt = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.options),
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.topic),
                selectinload(MockTestAttempt.student_answers),
                selectinload(MockTestAttempt.result),
            )
            .filter(MockTestAttempt.id == attempt_id)
            .first()
        )

        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found.",
            )

        if attempt.status == AttemptStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Answer review is only permitted after exam submission.",
            )

        result_summary = TestAttemptService.get_attempt_result(attempt_id, user_id, db)

        answer_map = {ans.question_id: ans for ans in attempt.student_answers}
        ordered_links = sorted(attempt.mock_test.test_questions, key=lambda l: l.order_index)

        review_questions: list[QuestionReviewItem] = []
        for idx, link in enumerate(ordered_links):
            q = link.question
            if not q:
                continue

            ans = answer_map.get(q.id)
            selected_ids: list[int] = []
            if ans and ans.answer_data:
                try:
                    data = json.loads(ans.answer_data)
                    if isinstance(data, list):
                        selected_ids = [int(x) for x in data]
                except (json.JSONDecodeError, ValueError):
                    pass

            options_payload = [
                ReviewOptionItem(
                    id=opt.id,
                    option_text=opt.option_text,
                    is_correct=opt.is_correct,
                )
                for opt in sorted(q.options, key=lambda o: o.order_index)
            ]

            review_questions.append(
                QuestionReviewItem(
                    question_id=q.id,
                    question_number=idx + 1,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    points=link.points or q.points,
                    topic_title=q.topic.title if q.topic else "General",
                    difficulty=q.difficulty,
                    options=options_payload,
                    selected_option_ids=selected_ids,
                    is_correct=ans.is_correct if ans else False,
                    points_earned=ans.points_earned if ans else 0,
                    is_marked_for_review=ans.is_marked_for_review if ans else False,
                    explanation=q.explanation,
                )
            )

        return TestReviewResponse(
            attempt_id=attempt.id,
            test_id=attempt.mock_test.id,
            test_title=attempt.mock_test.title,
            test_slug=attempt.mock_test.slug,
            status=attempt.status,
            result=result_summary,
            questions=review_questions,
        )

    @staticmethod
    def list_user_attempts(
        user_id: int,
        db: Session,
    ) -> list[AttemptHistoryItem]:
        """Fetch all historical examination attempts for a student."""
        attempts = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test),
                selectinload(MockTestAttempt.result),
            )
            .filter(MockTestAttempt.user_id == user_id)
            .order_by(MockTestAttempt.id.desc())
            .all()
        )

        history: list[AttemptHistoryItem] = []
        for att in attempts:
            mt = att.mock_test
            res = att.result
            time_taken = res.time_taken_seconds if res else 0
            passed = res.passed if res else (att.percentage >= (mt.passing_percentage if mt else 70.0))
            total_points = res.total_points if res else 0.0

            history.append(
                AttemptHistoryItem(
                    attempt_id=att.id,
                    test_id=mt.id if mt else 0,
                    test_title=mt.title if mt else "Exam",
                    test_slug=mt.slug if mt else "",
                    difficulty=mt.difficulty if mt else DifficultyLevel.BEGINNER,
                    test_type=mt.test_type if mt else MockTestType.MIXED,
                    status=att.status,
                    score=att.score,
                    total_points=total_points,
                    percentage=att.percentage,
                    passed=passed,
                    started_at=_ensure_utc(att.started_at).isoformat(),
                    submitted_at=_ensure_utc(att.submitted_at).isoformat() if att.submitted_at else None,
                    time_taken_seconds=time_taken,
                )
            )

        return history

    @staticmethod
    def create_practice_session(
        user_id: int,
        attempt_id: int | None = None,
        prior_attempt_id: int | None = None,
        mode: str | None = None,
        filter_mode: str | None = None,
        db: Session = None,
    ) -> StartAttemptResponse:
        """
        Create a targeted practice sitting focusing on incorrect or unanswered questions.
        Respects zero-knowledge student answer shielding.
        """
        target_att_id = attempt_id if attempt_id is not None else prior_attempt_id
        if target_att_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attempt ID is required for practice session generation.",
            )

        active_mode = mode or filter_mode or "incorrect_or_unanswered"

        attempt = (
            db.query(MockTestAttempt)
            .options(
                selectinload(MockTestAttempt.mock_test)
                .selectinload(MockTest.test_questions)
                .selectinload(MockTestQuestion.question)
                .selectinload(Question.options),
                selectinload(MockTestAttempt.student_answers),
            )
            .filter(MockTestAttempt.id == target_att_id)
            .first()
        )

        if not attempt or attempt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {target_att_id} not found.",
            )

        # Map answers
        answer_map = {ans.question_id: ans for ans in attempt.student_answers}

        targeted_questions: list[Question] = []
        for link in attempt.mock_test.test_questions:
            q = link.question
            if not q:
                continue

            ans = answer_map.get(q.id)
            has_selection = False
            if ans and ans.answer_data:
                try:
                    data = json.loads(ans.answer_data)
                    if data:
                        has_selection = True
                except (json.JSONDecodeError, ValueError):
                    pass

            if active_mode == "incorrect":
                if has_selection and not ans.is_correct:
                    targeted_questions.append(q)
            elif active_mode == "unanswered":
                if not has_selection:
                    targeted_questions.append(q)
            else:  # "incorrect_or_unanswered"
                if not has_selection or (has_selection and not ans.is_correct):
                    targeted_questions.append(q)

        if not targeted_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No {active_mode} questions available for practice.",
            )

        # Create a dynamic practice MockTest
        now = datetime.now(timezone.utc)
        practice_slug = f"practice-{active_mode}-{attempt.id}-{int(now.timestamp())}"
        practice_test = MockTest(
            title=f"Practice: {active_mode.replace('_', ' ').title()} ({attempt.mock_test.title})",
            slug=practice_slug,
            description=f"Targeted review of {len(targeted_questions)} questions from previous attempt.",
            difficulty=attempt.mock_test.difficulty,
            test_type=MockTestType.PRACTICE,
            duration_minutes=max(10, len(targeted_questions) * 2),
            total_questions=len(targeted_questions),
            passing_percentage=attempt.mock_test.passing_percentage,
            status=MockTestStatus.PUBLISHED,
        )
        db.add(practice_test)
        db.flush()

        for idx, q in enumerate(targeted_questions):
            link = MockTestQuestion(
                mock_test_id=practice_test.id,
                question_id=q.id,
                order_index=idx,
                points=q.points,
            )
            db.add(link)

        db.commit()

        # Start the practice session
        return TestAttemptService.start_or_resume_attempt(
            user_id=user_id,
            test_id_or_slug=practice_test.id,
            retake=True,
            db=db,
        )

    @staticmethod
    def _finalize_expired_attempt(attempt: MockTestAttempt, db: Session) -> None:
        """Internal helper to automatically score and finalize an expired test."""
        # Load relationships if not loaded
        db.refresh(
            attempt,
            attribute_names=["mock_test", "student_answers", "result"],
        )
        mt = attempt.mock_test
        now = datetime.now(timezone.utc)

        scoring_res = scoring_service.score_attempt(
            attempt=attempt,
            test_questions=mt.test_questions if mt else [],
            student_answers=attempt.student_answers,
            passing_percentage=mt.passing_percentage if mt else 70.0,
        )

        attempt.status = AttemptStatus.EXPIRED
        attempt.submitted_at = now
        attempt.score = scoring_res.score
        attempt.percentage = scoring_res.percentage

        max_sec = (mt.duration_minutes * 60) if mt else 1800

        res = attempt.result
        if not res:
            res = TestResult(
                attempt_id=attempt.id,
                correct_answers=scoring_res.correct_answers,
                incorrect_answers=scoring_res.incorrect_answers,
                unanswered=scoring_res.unanswered_questions,
                total_questions=scoring_res.total_questions,
                score=scoring_res.score,
                total_points=scoring_res.total_points,
                earned_points=scoring_res.earned_points,
                percentage=scoring_res.percentage,
                passing_percentage=scoring_res.passing_percentage,
                passed=scoring_res.passed,
                time_taken_seconds=max_sec,
            )
            db.add(res)
        else:
            res.correct_answers = scoring_res.correct_answers
            res.incorrect_answers = scoring_res.incorrect_answers
            res.unanswered = scoring_res.unanswered_questions
            res.total_questions = scoring_res.total_questions
            res.score = scoring_res.score
            res.total_points = scoring_res.total_points
            res.earned_points = scoring_res.earned_points
            res.percentage = scoring_res.percentage
            res.passing_percentage = scoring_res.passing_percentage
            res.passed = scoring_res.passed
            res.time_taken_seconds = max_sec

        db.commit()


test_attempt_service = TestAttemptService()
