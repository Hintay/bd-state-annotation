"""Pydantic models defining the structured output contract for each prompt."""
from typing import Literal
from pydantic import BaseModel

MoodState = Literal["MANIC", "HYPOMANIC", "DEPRESSIVE", "STABLE"]

class SinglePostLabel(BaseModel):
    id: str
    state: MoodState
    opposite_pole_symptoms: list[str]
    specifiers: list[Literal["with_mixed_features"]]
    confidence: Literal["High", "Medium", "Low"]   # single-post prompt uses a string scale
    reasoning: str

class ChangePoint(BaseModel):
    date: str
    event: str
    pre_state: str
    post_state: str

class TrendLabel(BaseModel):
    id: str
    dominant_state: Literal["MANIC", "HYPOMANIC", "DEPRESSIVE", "STABLE", "NO_DATA"]
    opposite_pole_symptoms: list[str]
    specifiers: list[str]
    trend_direction: Literal["NO_TREND", "FLUCTUATING", "TOWARDS_DEPRESSION", "TOWARDS_MANIA"]
    trend_summary: str
    change_points: list[ChangePoint]
    confidence: float                              # trend prompt uses a 0-1 float

class DiagnosisEvidence(BaseModel):
    type: Literal["explicit_diagnosis", "treatment_evidence", "medication_mention",
                  "diagnosis_detail", "hospitalization", "other"]
    post_id: str
    quote: str
    interpretation: str

class PatientVerdict(BaseModel):
    author_name: str
    verification_status: Literal["verified", "probable", "unverified"]
    confidence: float
    diagnosis_type: Literal["BD_I", "BD_II", "BD_NOS", "cyclothymia", "unspecified", "none"]
    diagnosis_evidence: list[DiagnosisEvidence]
    evidence_post_count: int
    exclusion_flags: list[str]
    reasoning: str
