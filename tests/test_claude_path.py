"""Live-Claude branches of both agents, with the Anthropic client mocked."""
import json
import sys
import types
from types import SimpleNamespace
from unittest import mock

import pytest

from src.pipeline import TalentPilotPipeline
from src.rubric_agent import InterviewRubricAgent
from src.screener_agent import CandidateScreenerAgent
from tests.conftest import load_pair

SCREENING = {
    "candidate_name": "Casey Claude", "candidate_email": "casey@example.com", "job_title": "ML Engineer",
    "overall_match_score": 91, "fit_verdict": "Strong Match",
    "key_strengths": ["s"], "identified_gaps": ["g"],
    "skill_matrix": [{"skill_name": "Python", "status": "MATCHED", "rationale": "r"}],
}
GUIDE = {
    "tailored_questions": [
        {"question_number": i, "category": "Architecture", "question_text": f"q{i}",
         "targeted_gap_or_skill": "x", "ideal_candidate_answer": "y"} for i in range(1, 6)
    ],
    "evaluation_rubric": [
        {"criterion_name": f"c{i}", "category": "Core Technical", "weight": "High",
         "level_1_poor": "a", "level_3_proficient": "b", "level_5_expert": "c"} for i in range(3)
    ],
}


@pytest.fixture
def client(monkeypatch):
    c = mock.Mock()
    module = types.ModuleType("anthropic")
    module.Anthropic = mock.Mock(return_value=c)
    monkeypatch.setitem(sys.modules, "anthropic", module)
    return c


def _text(t):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=t)])


def test_screener_parses_fenced_json(client):
    client.messages.create.return_value = _text("```json\n" + json.dumps(SCREENING) + "\n```")
    s = CandidateScreenerAgent(api_key="sk-test").screen_candidate(*load_pair("engineer"))
    assert s.candidate_name == "Casey Claude"
    assert s.overall_match_score == 91


def test_screener_falls_back_on_error(client, capsys):
    client.messages.create.side_effect = RuntimeError("boom")
    s = CandidateScreenerAgent(api_key="sk-test").screen_candidate(*load_pair("engineer"))
    assert (s.candidate_name, s.overall_match_score) == ("Alex Morgan", 83)
    assert "Using offline heuristic engine" in capsys.readouterr().out


def test_screener_falls_back_on_invalid_json(client):
    client.messages.create.return_value = _text("not json")
    s = CandidateScreenerAgent(api_key="sk-test").screen_candidate(*load_pair("pm"))
    assert s.candidate_name == "Jordan Taylor"


def test_rubric_agent_uses_claude_output(client):
    client.messages.create.return_value = _text(json.dumps(GUIDE))
    agent = InterviewRubricAgent(api_key="sk-test")
    screening = CandidateScreenerAgent(api_key="").screen_candidate(*load_pair("engineer"))
    assert [q.question_text for q in agent.generate_interview_guide(screening)] == ["q1", "q2", "q3", "q4", "q5"]
    assert [r.criterion_name for r in agent.generate_grading_rubric(screening)] == ["c0", "c1", "c2"]


def test_rubric_agent_falls_back_on_error(client):
    client.messages.create.side_effect = RuntimeError("boom")
    agent = InterviewRubricAgent(api_key="sk-test")
    screening = CandidateScreenerAgent(api_key="").screen_candidate(*load_pair("engineer"))
    assert agent.generate_interview_guide(screening)[0].category.startswith("Gap Probe")
    assert len(agent.generate_grading_rubric(screening)) == 3


def test_rubric_agent_falls_back_when_claude_returns_empty_lists(client):
    client.messages.create.return_value = _text('{"tailored_questions": [], "evaluation_rubric": []}')
    agent = InterviewRubricAgent(api_key="sk-test")
    screening = CandidateScreenerAgent(api_key="").screen_candidate(*load_pair("engineer"))
    assert len(agent.generate_interview_guide(screening)) == 5
    assert len(agent.generate_grading_rubric(screening)) == 3


@pytest.mark.parametrize("key", ["", "your_anthropic_api_key_here"])
def test_placeholder_or_empty_key_never_calls_claude(client, monkeypatch, key):
    monkeypatch.setenv("ANTHROPIC_API_KEY", key)
    TalentPilotPipeline().run(*load_pair("analyst"))
    client.messages.create.assert_not_called()


@pytest.mark.xfail(strict=True, reason="Known bug: rubric agent calls Claude twice for one guide")
def test_pipeline_makes_one_claude_call_per_agent(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    client.messages.create.side_effect = [_text(json.dumps(SCREENING)), _text(json.dumps(GUIDE)), _text(json.dumps(GUIDE))]
    TalentPilotPipeline().run(*load_pair("engineer"))
    assert client.messages.create.call_count == 2
