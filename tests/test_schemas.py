import pytest
from pydantic import ValidationError
from src.schemas import SinglePostLabel, TrendLabel, ChangePoint, PatientVerdict

def test_single_post_label_accepts_valid():
    obj = SinglePostLabel(
        id="p1", state="HYPOMANIC", opposite_pole_symptoms=[],
        specifiers=[], confidence="High", reasoning="ok")
    assert obj.state == "HYPOMANIC"
    assert obj.confidence == "High"

def test_single_post_label_rejects_bad_state():
    with pytest.raises(ValidationError):
        SinglePostLabel(id="p1", state="EUPHORIC", opposite_pole_symptoms=[],
                        specifiers=[], confidence="High", reasoning="x")

def test_state_label_accepts_uncertain():
    single = SinglePostLabel(id="p1", state="UNCERTAIN", opposite_pole_symptoms=[],
                             specifiers=[], confidence="Low", reasoning="no clinical signal")
    assert single.state == "UNCERTAIN"
    trend = TrendLabel(id="u1", dominant_state="UNCERTAIN", opposite_pole_symptoms=[],
                       specifiers=[], trend_direction="NO_TREND", trend_summary="unanalyzable",
                       change_points=[], confidence=0.2)
    assert trend.dominant_state == "UNCERTAIN"

def test_trend_label_confidence_is_float():
    obj = TrendLabel(
        id="u1", dominant_state="MANIC", opposite_pole_symptoms=[], specifiers=[],
        trend_direction="TOWARDS_MANIA", trend_summary="s",
        change_points=[ChangePoint(date="2024-03-08", event="e", pre_state="STABLE", post_state="HYPOMANIC")],
        confidence=0.95)
    assert obj.confidence == 0.95
    assert obj.change_points[0].post_state == "HYPOMANIC"

def test_patient_verdict_accepts_valid():
    obj = PatientVerdict(
        author_name="user_01", verification_status="verified", confidence=0.9,
        diagnosis_type="BD_II", diagnosis_evidence=[], evidence_post_count=3,
        exclusion_flags=[], reasoning="r")
    assert obj.verification_status == "verified"
