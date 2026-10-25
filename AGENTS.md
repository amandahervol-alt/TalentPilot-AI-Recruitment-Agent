# TalentPilot — Multi-Agent AI Recruitment System
AGENTS.md — Antigravity Orchestration Architecture

TalentPilot implements a sequential 2-agent recruitment architecture designed to ingest job descriptions and resumes, screen candidates, identify skill gaps, and generate gap-targeted interview rubrics.

## Architecture

### Agent 1: Candidate Screener (`src/screener_agent.py`)
- **Input**: Job Description text + Candidate Resume text.
- **Role**: Extracts candidate metadata, performs requirement-to-evidence alignment, calculates overall match scores, and identifies specific skill gaps.
- **Output**: `CandidateScreeningResult` (Pydantic model).

### Agent 2: Interview Guide & Rubric Generator (`src/rubric_agent.py`)
- **Input**: `CandidateScreeningResult` state object from Agent 1.
- **Role**: Analyzes the candidate's exact gaps and strengths to formulate 5 high-leverage technical and operational probe questions with expected strong answers, plus a standardized 1-5 evaluation rubric.
- **Output**: `List[TailoredQuestion]` and `List[RubricCriterion]`.

### Orchestrator Pipeline & Reporting (`src/pipeline.py` & `src/report_generator.py`)
- Coordinates sequential agent execution.
- Generates a formatted Recruiter Markdown Dossier (`output/candidate_card.md`) and an interactive glassmorphic web dashboard (`output/dashboard.html`).

## Dual-Engine Operation
- **Live AI Mode**: Anthropic Claude (`claude-sonnet-5-5` by default, configurable with `ANTHROPIC_MODEL`) via structured JSON schema parsing.
- **Zero-Config Offline Mode**: Deterministic heuristic rule engine for instant local execution and automated testing without API keys.
