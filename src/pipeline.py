import datetime
from src.schemas import RecruiterEvaluationCard
from src.screener_agent import CandidateScreenerAgent
from src.rubric_agent import InterviewRubricAgent


class TalentPilotPipeline:
    """Multi-agent orchestrator managing state passing between Screener (Agent 1) and Rubric Generator (Agent 2)."""

    def __init__(self):
        self.screener_agent = CandidateScreenerAgent()
        self.rubric_agent = InterviewRubricAgent()

    def run(self, jd_text: str, resume_text: str) -> RecruiterEvaluationCard:
        """Run two-agent pipeline sequentially."""
        # Step 1: Candidate Screening (Agent 1)
        screening_res = self.screener_agent.screen_candidate(jd_text, resume_text)

        # Step 2: Tailored Questions & Rubric Generation (Agent 2)
        questions = self.rubric_agent.generate_interview_guide(screening_res)
        rubric = self.rubric_agent.generate_grading_rubric(screening_res)

        # Step 3: Combine into Recruiter Evaluation Card
        evaluation_card = RecruiterEvaluationCard(
            system_title="TalentPilot Multi-Agent Candidate Evaluation Card",
            generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            screening_result=screening_res,
            tailored_questions=questions,
            evaluation_rubric=rubric
        )

        return evaluation_card
