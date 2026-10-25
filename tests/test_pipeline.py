import pytest

from src.pipeline import TalentPilotPipeline
from tests.conftest import load_pair


@pytest.mark.parametrize("role, name", [("engineer", "Alex Morgan"), ("pm", "Jordan Taylor"), ("analyst", "Samantha Chen")])
def test_pipeline_passes_screening_into_rubric_agent(role, name):
    card = TalentPilotPipeline().run(*load_pair(role))
    s = card.screening_result
    assert s.candidate_name == name
    assert card.system_title == "TalentPilot Multi-Agent Candidate Evaluation Card"
    assert len(card.generated_at) == 19  # YYYY-MM-DD HH:MM:SS
    assert card.tailored_questions[0].targeted_gap_or_skill == s.identified_gaps[0]
    assert len(card.tailored_questions) == 5
    assert len(card.evaluation_rubric) == 3
