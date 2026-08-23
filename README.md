# 🎯 TalentPilot — Multi-Agent Candidate Evaluation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Anthropic Claude](https://img.shields.io/badge/Claude-3.7%20%7C%203.5-purple.svg)](https://www.anthropic.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.0-red.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous, production-grade Multi-Agent AI system built in Python that pairs **Candidate Screening** with **Tailored Interview Rubric Generation** to automate recruiter intake workflows and standardize candidate evaluations.

---

## 🌟 Architecture & Multi-Agent Design Highlights

* **Multi-Agent State Passing**: Demonstrates a 2-agent sequential pipeline where **Agent 1 (Screener)** extracts skill gaps and passes Pydantic state directly to **Agent 2 (Rubric Generator)**.
* **Dual-Engine AI Reasoning**: Supports live **Anthropic Claude** (`claude-3-7-sonnet-20250219` / `claude-3-5-sonnet-20241022`) via structured JSON schema parsing with automatic offline heuristic fallback.
* **Pydantic Schema Validation**: Enforces rigid JSON schemas (`CandidateScreeningResult`, `TailoredQuestion`, `RubricCriterion`, `RecruiterEvaluationCard`) to guarantee 100% type-safe downstream pipeline execution.
* **Gap-Targeted Interview Generation**: Agent 2 analyzes specific candidate gaps identified by Agent 1 and generates 5 probe questions with expected strong answer criteria.
* **Standardized 1-5 Scoring Rubric**: Automatically creates a structured grading matrix across Core Engineering, LLM Guardrails, and Operational Fit.
* **Glassmorphism Web Dashboard**: Renders an interactive HTML dashboard featuring match scores, requirement alignment matrices, and recruiter question guides.
* **Multi-Role Sample Datasets**: Includes pre-loaded JD/Resume pairs across **AI Engineering**, **AI Product Management**, and **Healthcare Data Analytics**.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────┐
                                  │ Job Description & Resume  │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │  Agent 1: Candidate       │
                                  │  Screener Agent           │
                                  └─────────────┬─────────────┘
                                                │ Pydantic State Object
                                                ▼
                                  ┌───────────────────────────┐
                                  │  Agent 2: Interview Guide │
                                  │  & Rubric Generator Agent │
                                  └─────────────┬─────────────┘
                                                │
                                ┌───────────────┴───────────────┐
                                ▼                               ▼
                  ┌───────────────────────────┐   ┌───────────────────────────┐
                  │ Candidate Evaluation Card │   │ Glassmorphism Web         │
                  │ (candidate_card.md)       │   │ Dashboard (dashboard.html)│
                  └───────────────────────────┘   └───────────────────────────┘
```

---

## 💡 Key Design Decisions for Interview Reviewers

1. **Why a 2-Agent Architecture?**  
   Single-prompt LLMs struggle when asked to simultaneously screen a resume, compute match metrics, generate targeted gap probes, and write a 1-5 grading rubric. Splitting the workflow into two specialized agents improves output precision and reduces context bloat.

2. **Grounded Gap Probing**:  
   Instead of asking generic behavioral questions (*"Tell me about a challenge"*), Agent 2 specifically targets missing requirements identified by Agent 1—providing recruiters with high-leverage technical questions.

3. **Zero-Config Offline Fallback**:  
   Allows developers, CI/CD runners, and interview reviewers to test the complete multi-agent workflow immediately without needing API keys.

---

## 🚀 Quick Start & Installation

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/amandahervol-alt/TalentPilot-AI-Recruitment-Agent.git
cd TalentPilot-AI-Recruitment-Agent
pip install -r requirements.txt
```

### 2. (Optional) Configure Live AI API Key
Copy `.env.example` to `.env` to enable live Claude reasoning:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-7-sonnet-20250219
```
*(If no API key is provided, the application runs seamlessly in zero-config offline mode).*

### 3. Run Multi-Agent Pipeline Across Sample Roles
```bash
# AI Software Engineer (Default)
python app.py --sample engineer

# AI Product Manager
python app.py --sample pm

# Healthcare Data Analyst
python app.py --sample analyst
```
*This automatically processes the Job Description and Resume, generates reports in `output/`, and launches the interactive Web Dashboard in your browser!*

### 4. Run Automated Pytest Suite
```bash
python -m pytest tests/
```

---

## 📂 Repository Structure

```
TalentPilot-AI-Recruitment-Agent/
├── data/
│   └── samples/                  # Sample JD & Resume pairings (Engineer, PM, Analyst)
├── src/
│   ├── schemas.py                # Pydantic schema validation models
│   ├── screener_agent.py         # Agent 1: Candidate Screener
│   ├── rubric_agent.py           # Agent 2: Interview Guide & Rubric Generator
│   ├── pipeline.py               # Multi-Agent Orchestrator
│   └── report_generator.py       # Markdown & Glassmorphism HTML Dashboard Generator
├── tests/
│   └── test_pipeline.py          # Pytest multi-agent test suite
├── output/                       # Generated Markdown & HTML Dashboard outputs
├── app.py                        # CLI & Local HTTP Web Server
├── AGENTS.md                     # Antigravity AI Orchestration Architecture
├── LICENSE                       # MIT License
├── .env.example                  # Environment configuration template
├── requirements.txt              # Project dependencies
└── README.md                     # Technical architecture & portfolio overview
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
