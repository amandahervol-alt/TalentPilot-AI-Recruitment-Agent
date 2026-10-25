from html import escape

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
    assert f">{escape(s.candidate_name)}</h2>" in html
    assert f'<div class="score-num">{s.overall_match_score}</div>' in html
    assert s.candidate_email in html
    for q in card.tailored_questions:
        assert escape(q.question_text) in html
    assert "{{" not in html and "{%" not in html


def _card_with(cards, **screening_updates):
    s = cards["engineer"].screening_result.model_copy(update=screening_updates)
    return cards["engineer"].model_copy(update={"screening_result": s})


def test_html_escapes_resume_content(cards):
    card = _card_with(cards, candidate_name="<script>x()</script>", candidate_email='a@b.co" onmouseover="x()')
    html = ReportGenerator(card).generate_html()
    assert "<script>x()</script>" not in html
    assert "&lt;script&gt;x()&lt;/script&gt;" in html
    assert '" onmouseover="' not in html


def test_html_escapes_claude_skill_status(cards):
    from src.schemas import SkillMatch
    card = _card_with(cards, skill_matrix=[SkillMatch(skill_name="Go", status='gap" onclick="x()', rationale="<b>r</b>")])
    html = ReportGenerator(card).generate_html()
    assert 'onclick="x()' not in html
    assert "<b>r</b>" not in html


def test_markdown_keeps_text_unescaped(cards):
    card = _card_with(cards, candidate_name="O'Brien & Sons")
    assert "* **Name**: O'Brien & Sons" in ReportGenerator(card).generate_markdown()
