from typing import List
from src.schemas import CandidateScreeningResult, TailoredQuestion, RubricCriterion


class InterviewRubricAgent:
    """Agent 2: Consumes Agent 1's CandidateScreeningResult and generates custom interview questions & 1-5 grading rubrics."""

    def generate_interview_guide(self, screening: CandidateScreeningResult) -> List[TailoredQuestion]:
        """Generate questions tailored to candidate strengths and gaps."""
        questions = [
            TailoredQuestion(
                question_number=1,
                category="Gap Probe — Clinical & Healthcare Data",
                question_text=f"Our role involves integrating with clinical healthcare data (EHR/FHIR). Since your background is heavy in general enterprise automation, how would you approach learning healthcare data security (HIPAA) and API standards?",
                targeted_gap_or_skill="Healthcare EHR / Clinical Workflows",
                ideal_candidate_answer="Candidate explains how they rapidly ramp up on new domain standards, citing past experience handling enterprise OAuth/Secret Manager security."
            ),
            TailoredQuestion(
                question_number=2,
                category="Technical Deep-Dive — Pydantic & LLM Guardrails",
                question_text=f"You mentioned enforcing Pydantic schemas across all LLM endpoints. Can you walk through a time an LLM returned malformed JSON or hallucinated a field, and how your Pydantic validation handled it?",
                targeted_gap_or_skill="Pydantic & JSON Schemas",
                ideal_candidate_answer="Describes fallback retry logic, schema validation error catches, and strict output constraint prompts."
            ),
            TailoredQuestion(
                question_number=3,
                category="Architecture — Async Document Intelligence",
                question_text=f"In your previous role, you built an async pipeline processing 5,000+ pages/week. How did you handle rate limits, concurrency, and P99 latency when calling Anthropic/OpenAI APIs?",
                targeted_gap_or_skill="RAG & Document Intelligence",
                ideal_candidate_answer="Mentions async worker pools (asyncio/Celery), exponential backoff retry algorithms, and token context chunking."
            ),
            TailoredQuestion(
                question_number=4,
                category="Stakeholder Operations",
                question_text="How do you work directly with non-technical operations teams to translate fuzzy business requests into technical API specifications?",
                targeted_gap_or_skill="Non-Technical Stakeholder Collaboration",
                ideal_candidate_answer="Describes spending time observing manual workflows first, mapping step-by-step logic, and building functional prototypes."
            ),
            TailoredQuestion(
                question_number=5,
                category="Cloud & Deployment",
                question_text="Tell us about your experience deploying serverless Python containers on GCP Cloud Run or Docker. How do you handle container scaling and secret management?",
                targeted_gap_or_skill="GCP Cloud Run & Docker",
                ideal_candidate_answer="Mentions stateless container design, GCP Secret Manager integration, and zero-idle cost scaling."
            )
        ]
        return questions

    def generate_grading_rubric(self, screening: CandidateScreeningResult) -> List[RubricCriterion]:
        """Generate a 1-5 evaluation rubric for candidate scoring."""
        rubric = [
            RubricCriterion(
                criterion_name="Python & Microservices Architecture",
                category="Core Engineering",
                weight="High",
                level_1_poor="Basic script writing only; struggles with async Python, FastAPI routes, or Pydantic schemas.",
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
                criterion_name="Domain Adaptability & Compliance",
                category="Operational Fit",
                weight="Medium",
                level_1_poor="Unfamiliar with enterprise security, OAuth, key vault management, or HIPAA privacy requirements.",
                level_3_proficient="Understands OAuth 2.0, secret managers, and secure handling of sensitive enterprise data.",
                level_5_expert="Proactive focus on compliance, role-based access control (RBAC), and audit-ready data pipelines."
            )
        ]
        return rubric
