import pytest

from src.rubric_agent import InterviewRubricAgent
from src.screener_agent import CandidateScreenerAgent
from tests.conftest import load_pair


def _screening(role="engineer"):
    return CandidateScreenerAgent(api_key="").screen_candidate(*load_pair(role))


@pytest.mark.parametrize("role", ["engineer", "pm", "analyst"])
def test_five_numbered_questions_led_by_gap_probe(role):
    screening = _screening(role)
    qs = InterviewRubricAgent(api_key="").generate_interview_guide(screening)
    assert [q.question_number for q in qs] == [1, 2, 3, 4, 5]
    first_gap = screening.identified_gaps[0]
    assert qs[0].category == f"Gap Probe — {first_gap[:40]}"
    assert qs[0].targeted_gap_or_skill == first_gap
    assert first_gap in qs[0].question_text


def test_gap_probe_category_truncates_long_gap():
    s = _screening().model_copy(update={"identified_gaps": ["G" * 100]})
    q1 = InterviewRubricAgent(api_key="").generate_interview_guide(s)[0]
    assert q1.category == "Gap Probe — " + "G" * 40


def test_no_gaps_uses_default_topic():
    s = _screening().model_copy(update={"identified_gaps": []})
    q1 = InterviewRubricAgent(api_key="").generate_interview_guide(s)[0]
    assert q1.targeted_gap_or_skill == "Domain Specific Workflows"


def test_rubric_has_three_criteria():
    rubric = InterviewRubricAgent(api_key="").generate_grading_rubric(_screening())
    assert [r.weight for r in rubric] == ["High", "High", "Medium"]
    assert all(r.level_1_poor and r.level_3_proficient and r.level_5_expert for r in rubric)
