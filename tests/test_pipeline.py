import pytest
from pathlib import Path
from src.pipeline import TalentPilotPipeline
from src.report_generator import ReportGenerator


@pytest.mark.parametrize("jd_path,resume_path,expected_candidate", [
    ("data/samples/sample_jd.txt", "data/samples/sample_resume.txt", "Alex Morgan"),
    ("data/samples/sample_jd_pm.txt", "data/samples/sample_resume_pm.txt", "Jordan Taylor"),
    ("data/samples/sample_jd_analyst.txt", "data/samples/sample_resume_analyst.txt", "Samantha Chen")
])
def test_talentpilot_multi_role_pipeline(jd_path, resume_path, expected_candidate):
    jd_file = Path(jd_path)
    resume_file = Path(resume_path)

    assert jd_file.exists(), f"Missing {jd_path}"
    assert resume_file.exists(), f"Missing {resume_path}"

    jd_text = jd_file.read_text(encoding="utf-8")
    resume_text = resume_file.read_text(encoding="utf-8")

    pipeline = TalentPilotPipeline()
    card = pipeline.run(jd_text, resume_text)

    # Check Agent 1 screening output
    s = card.screening_result
    assert s.candidate_name == expected_candidate
    assert s.overall_match_score >= 50
    assert len(s.skill_matrix) >= 3

    # Check Agent 2 rubric & question output
    assert len(card.tailored_questions) == 5
    assert len(card.evaluation_rubric) >= 3

    # Test Report Generator
    generator = ReportGenerator(card)
    md = generator.generate_markdown()
    html = generator.generate_html()

    assert "TalentPilot Multi-Agent Candidate Evaluation" in md
    assert expected_candidate in html
    assert "<!DOCTYPE html>" in html
