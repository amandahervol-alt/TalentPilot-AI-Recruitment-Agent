import pytest

from src.pipeline import TalentPilotPipeline
from src.report_generator import ReportGenerator
from tests.conftest import load_pair


@pytest.fixture(scope="module")
def cards():
    return {r: TalentPilotPipeline().run(*load_pair(r)) for r in ("engineer", "pm", "analyst")}


@pytest.mark.parametrize("role", ["engineer", "pm", "analyst"])
def test_markdown_card(cards, role):
    card = cards[role]
    s = card.screening_result
    md = ReportGenerator(card).generate_markdown()
    assert md.startswith("# 📋 TalentPilot Multi-Agent Candidate Evaluation")
    assert f"* **Name**: {s.candidate_name}" in md
    assert f"`{s.overall_match_score}/100` ({s.fit_verdict})" in md
    for q in card.tailored_questions:
        assert f"### Q{q.question_number} [{q.category}]" in md
    for r in card.evaluation_rubric:
        assert f"### {r.criterion_name}" in md
    assert f"- {s.identified_gaps[0]}" in md


@pytest.mark.parametrize("role", ["engineer", "pm", "analyst"])
def test_html_dashboard(cards, role):
    card = cards[role]
    s = card.screening_result
    html = ReportGenerator(card).generate_html()
    assert html.startswith("<!DOCTYPE html>")
    assert f">{s.candidate_name}</h2>" in html
    assert f'<div class="score-num">{s.overall_match_score}</div>' in html
    assert s.candidate_email in html
    for q in card.tailored_questions:
        assert q.question_text in html
    assert "{{" not in html and "{%" not in html


@pytest.mark.xfail(strict=True, reason="Known bug: HTML dashboard does not escape resume-derived text")
def test_html_escapes_resume_content(cards):
    s = cards["engineer"].screening_result.model_copy(update={"candidate_name": "<script>x()</script>"})
    card = cards["engineer"].model_copy(update={"screening_result": s})
    assert "<script>x()</script>" not in ReportGenerator(card).generate_html()
