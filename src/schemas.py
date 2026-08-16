from typing import List, Optional
from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    skill_name: str
    status: str = Field(..., description="MATCHED, GAP, or PARTIAL")
    rationale: str = Field(..., description="Evidence from resume or missing requirement")


class CandidateScreeningResult(BaseModel):
    candidate_name: str
    candidate_email: str
    job_title: str
    overall_match_score: int = Field(..., description="Score from 1 to 100 based on requirement alignment")
    fit_verdict: str = Field(..., description="Strong Match, Moderate Match, or Low Match")
    key_strengths: List[str]
    identified_gaps: List[str]
    skill_matrix: List[SkillMatch]


class TailoredQuestion(BaseModel):
    question_number: int
    category: str = Field(..., description="Gap Probe, Technical Deep-Dive, Architecture, Stakeholder Ops")
    question_text: str = Field(..., description="The specific question for the interviewer to ask")
    targeted_gap_or_skill: str = Field(..., description="What resume gap or skill this question tests")
    ideal_candidate_answer: str = Field(..., description="What a strong candidate response should include")


class RubricCriterion(BaseModel):
    criterion_name: str
    category: str
    weight: str = Field(default="High", description="High, Medium, Low")
    level_1_poor: str = Field(..., description="Description of a 1/5 rating")
    level_3_proficient: str = Field(..., description="Description of a 3/5 rating")
    level_5_expert: str = Field(..., description="Description of a 5/5 rating")


class RecruiterEvaluationCard(BaseModel):
    system_title: str = Field(default="TalentPilot Multi-Agent Candidate Evaluation")
    generated_at: str
    screening_result: CandidateScreeningResult
    tailored_questions: List[TailoredQuestion]
    evaluation_rubric: List[RubricCriterion]
