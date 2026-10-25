import os
import json
from typing import List, Tuple
from dotenv import load_dotenv
from src.claude_response import DEFAULT_MODEL, REQUEST_OPTIONS, first_text, strip_code_fences
from src.schemas import CandidateScreeningResult, TailoredQuestion, RubricCriterion

load_dotenv()


class InterviewRubricAgent:
    """Agent 2: Consumes Agent 1's CandidateScreeningResult and generates custom interview questions & 1-5 grading rubrics."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
        # One Claude call returns both questions and rubric; remember it per screening.
        self._claude_cache = {}

    def _claude_guide(self, screening: CandidateScreeningResult) -> Tuple[List[TailoredQuestion], List[RubricCriterion]]:
        key = screening.model_dump_json()
        if key not in self._claude_cache:
            try:
                self._claude_cache[key] = self._generate_with_claude(screening)
            except Exception as e:
                print(f"[RubricAgent Warning] Claude live guide generation error ({e}). Using offline heuristic engine.")
                self._claude_cache[key] = ([], [])
        return self._claude_cache[key]

    def generate_interview_guide(self, screening: CandidateScreeningResult) -> List[TailoredQuestion]:
        """Generate questions tailored to candidate strengths and gaps."""
        if self.api_key and self.api_key != "your_anthropic_api_key_here":
            questions, _ = self._claude_guide(screening)
            if questions:
                return questions

        return self._generate_questions_heuristically(screening)

    def generate_grading_rubric(self, screening: CandidateScreeningResult) -> List[RubricCriterion]:
        """Generate a 1-5 evaluation rubric for candidate scoring."""
        if self.api_key and self.api_key != "your_anthropic_api_key_here":
            _, rubric = self._claude_guide(screening)
            if rubric:
                return rubric

        return self._generate_rubric_heuristically(screening)

    def _generate_with_claude(self, screening: CandidateScreeningResult) -> Tuple[List[TailoredQuestion], List[RubricCriterion]]:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)

        prompt = f"""You are an expert Technical Interview Designer.
Based on the following candidate screening results, generate:
1. Exactly 5 tailored interview questions targeting the candidate's specific strengths and identified gaps.
2. A 3-criterion 1-5 grading rubric for the role.

Screening Summary:
Candidate: {screening.candidate_name}
Target Role: {screening.job_title}
Match Score: {screening.overall_match_score}/100 ({screening.fit_verdict})
Key Strengths: {screening.key_strengths}
Identified Gaps: {screening.identified_gaps}

Return JSON with this structure:
{{
  "tailored_questions": [
    {{
      "question_number": 1,
      "category": "Gap Probe | Technical Deep-Dive | Architecture | Stakeholder Ops | Problem Solving",
      "question_text": "Detailed question string",
      "targeted_gap_or_skill": "Targeted skill name",
      "ideal_candidate_answer": "Summary of what a strong response demonstrates"
    }}
  ],
  "evaluation_rubric": [
    {{
      "criterion_name": "Criterion Title",
      "category": "Core Technical | Systems Architecture | Operational Fit",
      "weight": "High" | "Medium",
      "level_1_poor": "Description of poor answer (1/5)",
      "level_3_proficient": "Description of competent answer (3/5)",
      "level_5_expert": "Description of exceptional answer (5/5)"
    }}
  ]
}}

Output ONLY valid JSON."""

        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            **REQUEST_OPTIONS,
        )

        content = strip_code_fences(first_text(response))

        data = json.loads(content)
        questions = [TailoredQuestion.model_validate(q) for q in data.get("tailored_questions", [])]
        rubric = [RubricCriterion.model_validate(r) for r in data.get("evaluation_rubric", [])]
        return questions, rubric

    def _generate_questions_heuristically(self, screening: CandidateScreeningResult) -> List[TailoredQuestion]:
        gaps = screening.identified_gaps
        first_gap = gaps[0] if gaps else "Domain Specific Workflows"

        questions = [
            TailoredQuestion(
                question_number=1,
                category=f"Gap Probe — {first_gap[:40]}",
                question_text=f"Our team heavily emphasizes {first_gap}. Based on your previous projects, how would you rapidly ramp up on this area and ensure high-standard execution?",
                targeted_gap_or_skill=first_gap,
                ideal_candidate_answer="Candidate explains how they rapidly ramp up on new domain standards, citing past experience handling complex technical requirements."
            ),
            TailoredQuestion(
                question_number=2,
                category="Technical Deep-Dive — Schema Validation & Reliability",
                question_text=f"In production systems, how do you handle unexpected malformed inputs or downstream API schema changes without causing cascading failures?",
                targeted_gap_or_skill="Pydantic & Schema Validation",
                ideal_candidate_answer="Describes fallback retry logic, strict schema validation catches, and automated error logging."
            ),
            TailoredQuestion(
                question_number=3,
                category="Architecture — Concurrency & High-Volume Processing",
                question_text=f"Walk us through how you design async worker pipelines or microservices to handle high-throughput workloads with rate limiting and exponential backoff.",
                targeted_gap_or_skill="Async Processing & Concurrency",
                ideal_candidate_answer="Mentions async worker pools (asyncio/Celery), exponential backoff retry algorithms, and token context optimization."
            ),
            TailoredQuestion(
                question_number=4,
                category="Stakeholder Operations & Requirements Gathering",
                question_text="How do you work directly with non-technical operations teams to translate fuzzy business requests into technical system specifications?",
                targeted_gap_or_skill="Non-Technical Stakeholder Collaboration",
                ideal_candidate_answer="Describes observing manual workflows first, mapping step-by-step logic, and building functional prototypes."
            ),
            TailoredQuestion(
                question_number=5,
                category="Deployment & Infrastructure",
                question_text="Tell us about your experience deploying serverless Python containers on cloud infrastructure. How do you handle secrets, scaling, and observability?",
                targeted_gap_or_skill="Cloud Infrastructure & Observability",
                ideal_candidate_answer="Mentions stateless container design, cloud Secret Manager integration, and zero-idle cost scaling."
            )
        ]
        return questions

    def _generate_rubric_heuristically(self, screening: CandidateScreeningResult) -> List[RubricCriterion]:
        return [
            RubricCriterion(
                criterion_name="Core Technical Proficiency & Microservices",
                category="Core Engineering",
                weight="High",
                level_1_poor="Basic script writing only; struggles with async architecture, routing, or Pydantic schemas.",
                level_3_proficient="Competent in building FastAPI endpoints, Pydantic validation models, and RESTful API integrations.",
                level_5_expert="Mastery of async microservices, schema enforcement, rate-limit retries, and high-concurrency pipelines."
            ),
            RubricCriterion(
                criterion_name="LLM Guardrails & Schema Enforcement",
                category="AI Systems",
                weight="High",
                level_1_poor="Relies solely on prompt wording without code-level schema validation or fallback error handling.",
                level_3_proficient="Enforces Pydantic schemas and structured JSON outputs to prevent hallucination.",
                level_5_expert="Implements robust multi-agent state passing, deterministic rules layers, and automated evaluation harnesses."
            ),
            RubricCriterion(
                criterion_name="Domain Adaptability & Stakeholder Communication",
                category="Operational Fit",
                weight="Medium",
                level_1_poor="Unfamiliar with enterprise security, OAuth, key vault management, or HIPAA privacy requirements.",
                level_3_proficient="Understands OAuth 2.0, secret managers, and secure handling of sensitive enterprise data.",
                level_5_expert="Proactive focus on compliance, role-based access control (RBAC), and audit-ready data pipelines."
            )
        ]
