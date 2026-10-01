"""Test suite for Step 19 CTF Challenges & Advanced Training Engine.

Verifies catalog browsing, zero-knowledge flag isolation, progressive hints,
anti-enumeration rate limiting, solution walkthrough reveals, tracks, and metrics.
"""

import time

import pytest
from app.db.session import SessionLocal
from app.models.challenge import ChallengeAttempt, ChallengeSubmission
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def clean_challenge_attempts():
    """Ensure tests run with isolated challenge attempt state."""
    db = SessionLocal()
    db.query(ChallengeSubmission).delete()
    db.query(ChallengeAttempt).delete()
    db.commit()
    db.close()
    yield
    db = SessionLocal()
    db.query(ChallengeSubmission).delete()
    db.query(ChallengeAttempt).delete()
    db.commit()
    db.close()



def test_list_challenges_catalog(client: TestClient):
    """Catalog returns active challenges with summary metadata."""
    response = client.get("/api/v1/challenges")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 40

    item = data[0]
    assert "challenge_id" in item
    assert "title" in item
    assert "difficulty" in item
    assert "category" in item
    assert "points" in item
    # Ensure flag hashes are never in catalog
    assert "flag_hash" not in item
    assert "flag_salt" not in item


def test_list_challenges_filtering(client: TestClient):
    """Challenges filter correctly by difficulty and category."""
    # Filter by difficulty
    resp_beginner = client.get("/api/v1/challenges?difficulty=BEGINNER")
    assert resp_beginner.status_code == 200
    beginner_list = resp_beginner.json()
    assert len(beginner_list) >= 10
    assert all(c["difficulty"] == "BEGINNER" for c in beginner_list)

    # Filter by category
    resp_cat = client.get("/api/v1/challenges?category=NETWORKING")
    assert resp_cat.status_code == 200
    cat_list = resp_cat.json()
    assert len(cat_list) >= 1
    assert all(c["category"] == "NETWORKING" for c in cat_list)

    # Search filter
    resp_search = client.get("/api/v1/challenges?search=DNS")
    assert resp_search.status_code == 200
    search_list = resp_search.json()
    assert len(search_list) >= 1
    assert any("DNS" in c["title"].upper() or "DNS" in c["description"].upper() for c in search_list)


def test_zero_knowledge_flag_isolation(client: TestClient):
    """Challenge detail never leaks flag hashes or solutions to unsolved attempts."""
    response = client.get("/api/v1/challenges/CHAL-BEG-001")
    assert response.status_code == 200
    ch = response.json()

    assert ch["challenge_id"] == "CHAL-BEG-001"
    assert ch["simulation_only"] is True
    # Zero-knowledge check: raw secret hashes must never appear in response
    assert "flag_hash" not in ch
    assert "flag_salt" not in ch
    for st in ch.get("stages", []):
        assert "flag_hash" not in st
        assert "flag_salt" not in st

    # Unsolved challenges must hide explanation and locked hints
    if not ch.get("is_solved") and not ch.get("revealed_solution"):
        assert ch.get("solution_explanation") is None
        for h in ch.get("hints", []):
            if not h.get("is_unlocked"):
                assert h.get("hint_text") is None


def test_challenge_tracks_listing_and_detail(client: TestClient):
    """Tracks return curated sequential challenges for skill pathways."""
    # List tracks
    resp_tracks = client.get("/api/v1/challenges/tracks")
    assert resp_tracks.status_code == 200
    tracks = resp_tracks.json()
    assert len(tracks) >= 5

    track_ids = [t["track_id"] for t in tracks]
    assert "TRACK-NET-DEFENDER" in track_ids
    assert "TRACK-SOC-ANALYST" in track_ids

    # Track detail
    resp_detail = client.get("/api/v1/challenges/tracks/TRACK-NET-DEFENDER")
    assert resp_detail.status_code == 200
    t_detail = resp_detail.json()
    assert t_detail["track_id"] == "TRACK-NET-DEFENDER"
    assert len(t_detail["items"]) >= 5
    assert t_detail["items"][0]["order_index"] == 1
    assert "challenge" in t_detail["items"][0]


def test_challenge_metrics_and_recommendations(client: TestClient):
    """Metrics aggregate KPI distribution and adaptive recommendations suggest next steps."""
    # Metrics
    resp_metrics = client.get("/api/v1/challenges/metrics")
    assert resp_metrics.status_code == 200
    metrics = resp_metrics.json()
    assert metrics["total_challenges"] >= 40
    assert "BEGINNER" in metrics["difficulty_distribution"]
    assert "user_solved" in metrics

    # Recommendations
    resp_recs = client.get("/api/v1/challenges/recommendations?limit=3")
    assert resp_recs.status_code == 200
    recs = resp_recs.json()
    assert len(recs) <= 3
    assert len(recs) >= 1
    assert "challenge_id" in recs[0]
    assert "reason" in recs[0]


def test_attempt_lifecycle_and_notes(client: TestClient):
    """Starting an attempt initializes progress state and allows notes autosave."""
    # Start attempt
    resp_start = client.post("/api/v1/challenges/CHAL-BEG-001/start")
    assert resp_start.status_code == 200
    att = resp_start.json()
    assert att["status"] == "IN_PROGRESS"
    assert att["score"] == 0.0
    assert att["hints_unlocked"] == 0
    attempt_id = att["attempt_id"]

    # Save notes
    notes_payload = {
        "attempt_id": attempt_id,
        "notes": "Evidence note: Analyzed SYN packets to port 22 on host 10.0.0.5."
    }
    resp_notes = client.post("/api/v1/challenges/CHAL-BEG-001/notes", json=notes_payload)
    assert resp_notes.status_code == 200
    updated_att = resp_notes.json()
    assert "Analyzed SYN packets" in updated_att["notes"]


def test_hint_unlock_with_penalty(client: TestClient):
    """Unlocking progressive hints reveals hint content and increments score penalty."""
    resp_start = client.post("/api/v1/challenges/CHAL-BEG-007/start")
    assert resp_start.status_code == 200
    att = resp_start.json()
    attempt_id = att["attempt_id"]

    # Unlock Hint #1
    resp_hint = client.post("/api/v1/challenges/CHAL-BEG-007/hint", json={"attempt_id": attempt_id})
    assert resp_hint.status_code == 200
    hint_data = resp_hint.json()
    assert hint_data["hint_number"] == 1
    assert hint_data["hint_text"] is not None
    assert hint_data["penalty_applied"] > 0
    assert hint_data["total_penalty"] > 0


def test_flag_submission_incorrect_and_rate_limit(client: TestClient):
    """Submitting incorrect flag fails gracefully and rapid repeat requests trigger rate limit."""
    resp_start = client.post("/api/v1/challenges/CHAL-BEG-003/start")
    assert resp_start.status_code == 200
    attempt_id = resp_start.json()["attempt_id"]

    # Submit incorrect flag
    sub_payload = {"attempt_id": attempt_id, "flag": "FLAG{WRONG_GUESS}"}
    resp_sub = client.post("/api/v1/challenges/CHAL-BEG-003/submit", json=sub_payload)
    assert resp_sub.status_code == 200
    result = resp_sub.json()
    assert result["is_correct"] is False
    assert result["solved"] is False
    assert result["attempts_used"] >= 1

    # Immediate second submission should hit rate limit
    resp_rapid = client.post("/api/v1/challenges/CHAL-BEG-003/submit", json=sub_payload)
    assert resp_rapid.status_code == 400
    assert "rate limit" in resp_rapid.json()["detail"].lower()


def test_flag_submission_correct_single_stage(client: TestClient):
    """Submitting valid flag marks challenge solved and reveals walkthrough."""
    resp_start = client.post("/api/v1/challenges/CHAL-BEG-001/start")
    assert resp_start.status_code == 200
    attempt_id = resp_start.json()["attempt_id"]

    # Sleep 2.1s to ensure rate limit window is satisfied
    time.sleep(2.1)

    # CHAL-BEG-001 flag is FLAG{10.10.10.25}
    valid_flag = "FLAG{10.10.10.25}"
    resp_submit = client.post(
        "/api/v1/challenges/CHAL-BEG-001/submit",
        json={"attempt_id": attempt_id, "flag": valid_flag},
    )
    assert resp_submit.status_code == 200
    res = resp_submit.json()
    assert res["is_correct"] is True
    assert res["solved"] is True
    assert res["points_awarded"] > 0

    # Verify detail now shows solved status and walkthrough
    resp_detail = client.get("/api/v1/challenges/CHAL-BEG-001")
    assert resp_detail.status_code == 200
    det = resp_detail.json()
    assert det["is_solved"] is True
    assert det["solution_explanation"] is not None


def test_reveal_solution_give_up(client: TestClient):
    """Revealing solution grants educational walkthrough but awards zero points."""
    resp_start = client.post("/api/v1/challenges/CHAL-BEG-006/start")
    assert resp_start.status_code == 200
    attempt_id = resp_start.json()["attempt_id"]

    resp_reveal = client.post(
        "/api/v1/challenges/CHAL-BEG-006/reveal",
        json={"attempt_id": attempt_id},
    )
    assert resp_reveal.status_code == 200
    rev = resp_reveal.json()
    assert rev["revealed"] is True
    assert rev["score"] == 0.0
    assert rev["solution_explanation"] is not None
    assert rev["common_mistakes"] is not None

    # Submitting after reveal should not award points
    time.sleep(2.1)
    resp_sub = client.post(
        "/api/v1/challenges/CHAL-BEG-006/submit",
        json={"attempt_id": attempt_id, "flag": "FLAG{ANYTHING}"},
    )
    assert resp_sub.status_code == 200
    assert resp_sub.json()["current_score"] == 0.0
