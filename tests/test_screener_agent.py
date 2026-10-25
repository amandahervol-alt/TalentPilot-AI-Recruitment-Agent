import pytest

from src.screener_agent import CandidateScreenerAgent
from tests.conftest import load_pair


@pytest.fixture
def screener():
    return CandidateScreenerAgent(api_key="")


@pytest.mark.parametrize("role, name, email, title, score, n_skills, gap", [
    ("engineer", "Alex Morgan", "alex.morgan@example.com", "Senior AI Software Engineer", 83, 6,
     "Healthcare EHR / Clinical Workflows"),
    ("pm", "Jordan Taylor", "jordan.taylor@example.com", "Senior AI Product Manager", 80, 5,
     "Hands-on LLM Prompt Engineering"),
    ("analyst", "Samantha Chen", "samantha.chen@example.com", "Senior Healthcare Data Analyst", 80, 5,
     "Healthcare Claims & EHR Standards"),
])
def test_screens_each_sample_pair(screener, role, name, email, title, score, n_skills, gap):
    s = screener.screen_candidate(*load_pair(role))
    assert (s.candidate_name, s.candidate_email, s.job_title) == (name, email, title)
    assert s.overall_match_score == score
    assert s.fit_verdict == "Strong Match"
    assert len(s.skill_matrix) == n_skills
    assert [m.skill_name for m in s.skill_matrix if m.status == "GAP"] == [gap]
    assert s.identified_gaps == [f"Missing explicit experience in {gap}"]
    assert len(s.key_strengths) == n_skills - 1


ENGINEER_JD = "JOB TITLE: Backend Engineer\nWe need Python."


@pytest.mark.parametrize("resume, score, verdict", [
    ("python pydantic webhook rag docker clinical", 100, "Strong Match"),
    ("python pydantic webhook rag", 66, "Moderate Match"),
    ("python", 16, "Low Match"),
])
def test_score_and_verdict_thresholds(screener, resume, score, verdict):
    s = screener.screen_candidate(ENGINEER_JD, "Pat Lee\n" + resume)
    assert (s.overall_match_score, s.fit_verdict) == (score, verdict)


def test_no_matches_uses_default_strengths(screener):
    s = screener.screen_candidate(ENGINEER_JD, "Pat Lee\nI bake bread.")
    assert s.overall_match_score == 0
    assert all(m.status == "GAP" for m in s.skill_matrix)
    assert s.key_strengths == ["Strong technical fundamentals & domain experience"]


def test_all_matches_uses_default_gaps(screener):
    s = screener.screen_candidate(ENGINEER_JD, "Pat Lee\npython json api rag docker fhir")
    assert s.identified_gaps == ["No critical requirement gaps identified"]


def test_empty_skill_matrix_scores_75(screener, monkeypatch):
    monkeypatch.setattr(screener, "_analyze_skill_matrix", lambda jd, r: [])
    s = screener.screen_candidate(ENGINEER_JD, "Pat Lee")
    assert (s.overall_match_score, s.fit_verdict) == (75, "Moderate Match")


@pytest.mark.parametrize("jd, first_skill", [
    ("JOB TITLE: X\nSenior Product Manager", "AI Product Strategy & Roadmaps"),
    ("JOB TITLE: X\nData Analyst", "SQL & Relational Databases"),
    ("JOB TITLE: X\nEngineer", "Python & FastAPI"),
])
def test_skill_set_is_chosen_from_jd(screener, jd, first_skill):
    assert screener._analyze_skill_matrix(jd, "")[0].skill_name == first_skill


@pytest.mark.parametrize("resume, expected", [
    ("jane doe\nSoftware Engineer", "Jane Doe"),
    ("jane@doe.com\nSoftware Engineer", "Alex Morgan"),
    ("A" * 35 + "\nmore", "Alex Morgan"),
    ("", "Alex Morgan"),
    ("\n\n  pat lee  \n", "Pat Lee"),
])
def test_name_extraction_and_fallback(screener, resume, expected):
    assert screener._extract_name(resume) == expected


def test_email_and_title_fallbacks(screener):
    assert screener._extract_email("no contact info") == "alex.morgan@example.com"
    assert screener._extract_email("reach me: first.last@corp.co.uk") == "first.last@corp.co.uk"
    assert screener._extract_job_title("no title line") == "Senior Technical Role"
    assert screener._extract_job_title("job title:  Staff Engineer  \nmore") == "Staff Engineer"


@pytest.mark.xfail(strict=True, reason="Known bug: keywords match inside words ('rest' in 'interest', 'rag' in 'storage')")
@pytest.mark.parametrize("resume, skill", [
    ("My interests include hiking.", "REST APIs & Webhooks"),
    ("Managed cold storage logistics.", "RAG & Document Intelligence"),
])
def test_keywords_do_not_match_inside_other_words(screener, resume, skill):
    matrix = {m.skill_name: m.status for m in screener._analyze_skill_matrix("Engineer", resume)}
    assert matrix[skill] == "GAP"
