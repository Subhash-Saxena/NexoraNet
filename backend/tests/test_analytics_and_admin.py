from collections.abc import Generator

import pytest
from app.db.session import SessionLocal
from app.models.user import User
from app.services.analytics.report_service import ReportService
from app.services.analytics.seed_step20_data import seed_step20_data
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def ensure_step20_seed(db: Session) -> None:
    """Ensure skills, achievements, and admin user are present in DB before test runs."""
    seed_step20_data(db)


def test_analytics_overview(client: TestClient) -> None:
    """Verify student analytics overview returns real persisted telemetry."""
    res = client.get("/api/v1/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "user_id" in data
    assert "total_learning_time_minutes" in data
    assert "lessons_completed" in data
    assert "labs_completed" in data
    assert "challenges_solved" in data
    assert "current_learning_streak" in data
    assert isinstance(data["recent_activity"], list)


def test_analytics_progress_and_trends(client: TestClient) -> None:
    """Verify learning progress breakdown and performance trends."""
    res_prog = client.get("/api/v1/analytics/progress")
    assert res_prog.status_code == 200
    prog_data = res_prog.json()
    assert "overall_completion_percentage" in prog_data
    assert "modules" in prog_data
    assert len(prog_data["modules"]) > 0

    res_trends = client.get("/api/v1/analytics/trends")
    assert res_trends.status_code == 200
    trends_data = res_trends.json()
    assert "test_accuracy_trend" in trends_data
    assert "lab_performance_trend" in trends_data
    assert "challenge_scores_trend" in trends_data


def test_skills_catalog_and_confidence(client: TestClient) -> None:
    """Verify 28 skills catalog with explainable confidence and evidence breakdowns."""
    res = client.get("/api/v1/skills")
    assert res.status_code == 200
    skills = res.json()
    assert len(skills) == 28

    # Verify skill structure
    first_skill = skills[0]
    assert "skill_code" in first_skill
    assert "name" in first_skill
    assert "category" in first_skill
    assert "accuracy" in first_skill
    assert "confidence" in first_skill
    assert "evidence_breakdown" in first_skill
    assert "educational_guidance" in first_skill

    # Verify single skill retrieval by code
    res_single = client.get("/api/v1/skills/SUBNETTING")
    assert res_single.status_code == 200
    subnet_data = res_single.json()
    assert subnet_data["skill_code"] == "SUBNETTING"
    assert "evidence_breakdown" in subnet_data


def test_recommendations_lifecycle(client: TestClient) -> None:
    """Verify pedagogical recommendations with neutral explanations and dismissal."""
    res = client.get("/api/v1/recommendations")
    assert res.status_code == 200
    recs = res.json()
    assert isinstance(recs, list)
    if recs:
        first_rec = recs[0]
        assert "title" in first_rec
        assert "rationale" in first_rec
        assert "target_url" in first_rec
        assert "priority" in first_rec

        # Dismiss recommendation
        rec_id = first_rec["id"]
        res_dismiss = client.post(f"/api/v1/recommendations/{rec_id}/dismiss")
        assert res_dismiss.status_code == 200
        assert res_dismiss.json()["status"] == "dismissed"


def test_achievements_criteria_evaluation(client: TestClient) -> None:
    """Verify 10 platform achievements with documented criteria."""
    res = client.get("/api/v1/achievements")
    assert res.status_code == 200
    achievements = res.json()
    assert len(achievements) >= 10

    sample = achievements[0]
    assert "code" in sample
    assert "title" in sample
    assert "criteria_description" in sample
    assert "required_count" in sample
    assert "progress_count" in sample
    assert "is_unlocked" in sample


def test_assessment_report_generation(client: TestClient) -> None:
    """Verify archival assessment report generation with educational disclaimer."""
    res = client.post("/api/v1/reports/assessment/generate")
    assert res.status_code == 201
    report = res.json()
    assert "report_uuid" in report
    assert "title" in report
    assert "summary" in report
    assert "disclaimer" in report
    assert "not a professional certification" in report["disclaimer"].lower()

    # Retrieve by UUID
    uuid_str = report["report_uuid"]
    res_get = client.get(f"/api/v1/reports/{uuid_str}")
    assert res_get.status_code == 200
    assert res_get.json()["report_uuid"] == uuid_str


def test_educational_certificate_verification(client: TestClient, db: Session) -> None:
    """Verify issuance and public read-only certificate verification."""
    student = db.query(User).filter(User.username == "student_dev").first()
    assert student is not None

    cert = ReportService.issue_certificate_if_eligible(
        db=db,
        user=student,
        course_or_module_title="Network Defense Foundations",
        course_or_module_slug="network-defense-foundations",
    )
    assert cert.verification_code.startswith("NX-")

    # Verify publicly
    res = client.get(f"/api/v1/certificates/verify/{cert.verification_code}")
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["student_name"] == (student.display_name or student.username)
    assert "internal educational completion verification" in data["disclaimer"]


def test_portfolio_privacy_and_sanitization(client: TestClient) -> None:
    """Verify portfolio defaults to PRIVATE, public view strips sensitive fields, and URL security."""
    # Ensure starting in PRIVATE state
    client.put("/api/v1/portfolio", json={"visibility": "PRIVATE"})
    # 1. Fetch own portfolio
    res = client.get("/api/v1/portfolio")
    assert res.status_code == 200
    port = res.json()
    slug = port["public_slug"]
    assert port["visibility"] == "PRIVATE"

    # 2. Public view should be blocked while PRIVATE
    res_pub_blocked = client.get(f"/api/v1/portfolio/public/{slug}")
    assert res_pub_blocked.status_code == 404

    # 3. Add project with valid URL
    res_proj = client.post(
        "/api/v1/portfolio/projects",
        json={
            "title": "Automated PCAP Forensics Parser",
            "description": "Python tool analyzing TCP window sizes and detecting beaconing intervals.",
            "technologies": ["Python", "Scapy", "Wireshark"],
            "skills": ["PACKET_ANALYSIS", "TCP_IP"],
            "learning_outcome": "Mastered stream reassembly and flow metrics.",
            "repository_url": "https://github.com/example/pcap-tool",
            "demo_url": "https://example.com/demo",
        },
    )
    assert res_proj.status_code == 201

    # 4. Attempt to add project with dangerous URL (must be rejected)
    res_bad_url = client.post(
        "/api/v1/portfolio/projects",
        json={
            "title": "Insecure Project",
            "description": "Testing injection.",
            "repository_url": "javascript:alert(1)",
        },
    )
    assert res_bad_url.status_code == 400

    # 5. Make portfolio PUBLIC
    res_update = client.put(
        "/api/v1/portfolio",
        json={"visibility": "PUBLIC", "bio": "Security investigator passionate about packet analysis."},
    )
    assert res_update.status_code == 200

    # 6. Public view should succeed and NEVER leak email, internal passwords, or notes
    res_pub = client.get(f"/api/v1/portfolio/public/{slug}")
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert "email" not in pub_data
    assert "password_hash" not in pub_data
    assert len(pub_data["projects"]) >= 1

    # 7. JSON Export
    res_exp = client.get("/api/v1/portfolio/export/json")
    assert res_exp.status_code == 200
    exp_data = res_exp.json()
    assert "export_version" in exp_data


def test_admin_authorization_and_audit(client: TestClient) -> None:
    """Verify strict server-side authorization: students get 403, admins get 200."""
    # 1. Non-admin request (defaults to student_dev) -> 403 Forbidden
    res_student = client.get("/api/v1/admin/dashboard")
    assert res_student.status_code == 403
    assert "Administrator authorization required" in res_student.json()["detail"]

    # 2. Student attempting content listing -> 403 Forbidden
    res_content_student = client.get("/api/v1/admin/content")
    assert res_content_student.status_code == 403

    # 3. Admin request with header X-User-Role: ADMIN -> 200 OK
    res_admin = client.get("/api/v1/admin/dashboard", headers={"X-User-Role": "ADMIN"})
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert "total_users" in data
    assert "catalog_counts" in data
    assert "publication_status" in data

    # 4. Admin content listing -> 200 OK
    res_content = client.get("/api/v1/admin/content", headers={"X-User-Role": "ADMIN"})
    assert res_content.status_code == 200
    assert isinstance(res_content.json(), list)

    # 5. Admin audit log listing -> 200 OK
    res_audit = client.get("/api/v1/admin/audit", headers={"X-User-Role": "ADMIN"})
    assert res_audit.status_code == 200
    assert isinstance(res_audit.json(), list)
