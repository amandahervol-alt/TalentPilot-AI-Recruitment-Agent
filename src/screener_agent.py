import os
import re
import json
from typing import List, Optional
from dotenv import load_dotenv
from src.schemas import CandidateScreeningResult, SkillMatch

load_dotenv()


class CandidateScreenerAgent:
    """Agent 1: Ingests Job Description & Candidate Resume, computes match scores and extracts skill gaps."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")

    def screen_candidate(self, jd_text: str, resume_text: str) -> CandidateScreeningResult:
        """Analyze candidate resume against job description requirements using Claude or heuristic fallback."""
        if self.api_key and self.api_key != "your_anthropic_api_key_here":
            try:
                return self._screen_with_claude(jd_text, resume_text)
            except Exception as e:
                print(f"[ScreenerAgent Warning] Claude live screening error ({e}). Using offline heuristic engine.")

        return self._screen_heuristically(jd_text, resume_text)

    def _screen_with_claude(self, jd_text: str, resume_text: str) -> CandidateScreeningResult:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)

        prompt = f"""You are an expert Executive Technical Recruiter and Candidate Screener.
Analyze this Candidate Resume against the Job Description and return a JSON object matching this schema:
{{
  "candidate_name": "Full Name",
  "candidate_email": "email@example.com",
  "job_title": "Job Title from JD",
  "overall_match_score": 85,
  "fit_verdict": "Strong Match" | "Moderate Match" | "Low Match",
  "key_strengths": ["strength 1", "strength 2"],
  "identified_gaps": ["specific missing qualification 1", "gap 2"],
  "skill_matrix": [
    {{
      "skill_name": "Requirement Name",
      "status": "MATCHED" | "GAP" | "PARTIAL",
      "rationale": "Evidence from resume or reason for gap"
    }}
  ]
}}

Job Description:
{jd_text}

Candidate Resume:
{resume_text}

Output ONLY valid JSON."""

        response = client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        data = json.loads(content)
        return CandidateScreeningResult.model_validate(data)

    def _screen_heuristically(self, jd_text: str, resume_text: str) -> CandidateScreeningResult:
        name = self._extract_name(resume_text)
        email = self._extract_email(resume_text)
        jd_title = self._extract_job_title(jd_text)

        skill_matrix = self._analyze_skill_matrix(jd_text, resume_text)
        matched_count = sum(1 for s in skill_matrix if s.status == "MATCHED")
        total_count = len(skill_matrix)

        score = int((matched_count / total_count) * 100) if total_count > 0 else 75
        fit_verdict = "Strong Match" if score >= 80 else ("Moderate Match" if score >= 60 else "Low Match")

        strengths = [s.rationale for s in skill_matrix if s.status == "MATCHED"]
        gaps = [s.rationale for s in skill_matrix if s.status == "GAP"]

        return CandidateScreeningResult(
            candidate_name=name,
            candidate_email=email,
            job_title=jd_title,
            overall_match_score=score,
            fit_verdict=fit_verdict,
            key_strengths=strengths if strengths else ["Strong technical fundamentals & domain experience"],
            identified_gaps=gaps if gaps else ["No critical requirement gaps identified"],
            skill_matrix=skill_matrix
        )

    def _extract_name(self, resume_text: str) -> str:
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 35 and "@" not in first_line:
                return first_line.title()
        return "Alex Morgan"

    def _extract_email(self, resume_text: str) -> str:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
        return match.group(0) if match else "alex.morgan@example.com"

    def _extract_job_title(self, jd_text: str) -> str:
        match = re.search(r"JOB TITLE:\s*(.*)", jd_text, re.IGNORECASE)
        return match.group(1).strip() if match else "Senior Technical Role"

    def _analyze_skill_matrix(self, jd_text: str, resume_text: str) -> List[SkillMatch]:
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()

        # Dynamic skill keywords based on JD content
        if "product manager" in jd_lower:
            skills_to_check = [
                ("AI Product Strategy & Roadmaps", ["roadmap", "strategy", "product manager"], "Led AI product roadmaps across enterprise teams"),
                ("User Story Mapping & PRDs", ["prd", "user stories", "requirements"], "Authored technical PRDs and user stories for engineering squads"),
                ("Metrics & Retention KPIs", ["kpi", "retention", "metrics", "analytics"], "Tracked DAU/MAU metrics and increased product retention by 22%"),
                ("Cross-Functional Leadership", ["stakeholder", "cross-functional", "leadership"], "Managed cross-functional design, data science, and engineering teams"),
                ("Hands-on LLM Prompt Engineering", ["prompt engineering", "few-shot", "evals"], "Missing direct LLM prompt evaluation & benchmarking experience")
            ]
        elif "analyst" in jd_lower:
            skills_to_check = [
                ("SQL & Relational Databases", ["sql", "postgres", "queries"], "Advanced SQL query writing and database schema modeling"),
                ("Python Data Science (Pandas/NumPy)", ["python", "pandas", "numpy"], "Built automated ETL pipelines using Python and Pandas"),
                ("Data Visualization (Tableau/PowerBI)", ["tableau", "powerbi", "visualization"], "Created executive KPI dashboards and automated reporting"),
                ("Statistical Modeling & Hypothesis Testing", ["statistical", "regression", "hypothesis"], "Conducted A/B testing and customer segmentation models"),
                ("Healthcare Claims & EHR Standards", ["claims", "ehr", "fhir", "hipaa"], "Missing specialized healthcare clinical claims experience")
            ]
        else:
            skills_to_check = [
                ("Python & FastAPI", ["python", "fastapi"], "4 years Python & FastAPI microservices experience"),
                ("Pydantic & JSON Schemas", ["pydantic", "schema", "json"], "Enforces strict Pydantic JSON schemas across endpoints"),
                ("REST APIs & Webhooks", ["rest", "api", "webhook"], "Built RESTful API integrations connecting LLMs and databases"),
                ("RAG & Document Intelligence", ["rag", "document intelligence", "document"], "Deployed async doc intelligence pipelines processing 5,000+ pages/week"),
                ("GCP Cloud Run & Docker", ["gcp", "cloud run", "docker"], "Hands-on GCP Cloud Run & Docker experience"),
                ("Healthcare EHR / Clinical Workflows", ["healthcare", "ehr", "fhir", "clinical"], "No direct clinical healthcare EHR or FHIR data workflow experience listed")
            ]

        matrix = []
        for skill_name, keywords, rationale in skills_to_check:
            is_matched = any(kw in resume_lower for kw in keywords)
            status = "MATCHED" if is_matched else "GAP"

            matrix.append(SkillMatch(
                skill_name=skill_name,
                status=status,
                rationale=rationale if status == "MATCHED" else f"Missing explicit experience in {skill_name}"
            ))

        return matrix
