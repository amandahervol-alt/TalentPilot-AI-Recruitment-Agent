import pytest
from pathlib import Path
from src.pipeline import TalentPilotPipeline
from src.report_generator import ReportGenerator


@pytest.fixture
def sample_inputs():
    jd_path = Path("data/samples/sample_jd.txt")
    resume_path = Path("data/samples/sample_resume.txt")

    if jd_path.exists() and resume_path.exists():
        return jd_path.read_text(encoding="utf-8"), resume_path.read_text(encoding="utf-8")

    return "JOB TITLE: Senior AI Software Engineer", "ALEX MORGAN\nPython FastAPI AI Engineer"


def test_talentpilot_pipeline_execution(sample_inputs):
    jd_text, resume_text = sample_inputs

    pipeline = TalentPilotPipeline()
    card = pipeline.run(jd_text, resume_text)

    # Check Agent 1 screening output
    s = card.screening_result
    assert s.candidate_name == "Alex Morgan"
    assert s.overall_match_score >= 50
    assert len(s.skill_matrix) >= 1

    # Check Agent 2 rubric & question output
    assert len(card.tailored_questions) == 5
    assert len(card.evaluation_rubric) >= 3


def test_report_generator_rendering(sample_inputs):
    jd_text, resume_text = sample_inputs

    pipeline = TalentPilotPipeline()
    card = pipeline.run(jd_text, resume_text)

    generator = ReportGenerator(card)
    md = generator.generate_markdown()
    html = generator.generate_html()

    assert "TalentPilot Multi-Agent Candidate Evaluation" in md
    assert "Alex Morgan" in html
    assert "<!DOCTYPE html>" in html
