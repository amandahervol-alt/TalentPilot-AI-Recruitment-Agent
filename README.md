# 🎯 TalentPilot — Multi-Agent Candidate Evaluation System

An autonomous, production-grade Multi-Agent AI system built in Python that pairs **Candidate Screening** with **Tailored Interview Rubric Generation** to automate recruiter intake workflows and standardize candidate evaluations.

---

## 🌟 Architecture & Multi-Agent Design Highlights

* **Multi-Agent State Passing**: Demonstrates a 2-agent sequential pipeline where **Agent 1 (Screener)** extracts skill gaps and passes Pydantic data directly to **Agent 2 (Rubric Generator)**.
* **Pydantic Schema Validation**: Enforces rigid JSON schemas (`CandidateScreeningResult`, `TailoredQuestion`, `RubricCriterion`, `RecruiterEvaluationCard`) to guarantee 100% type-safe downstream pipeline execution.
* **Gap-Targeted Interview Generation**: Agent 2 analyzes specific candidate gaps identified by Agent 1 and generates 5 probe questions with expected strong answer criteria.
* **Standardized 1-5 Scoring Rubric**: Automatically creates a structured grading matrix across Core Engineering, LLM Guardrails, and Operational Fit.
* **Glassmorphism Web Dashboard**: Renders an interactive HTML dashboard featuring match scores, requirement alignment matrices, and recruiter question guides.
* **Zero-Config Offline Mode**: Includes sample job descriptions and resumes out-of-the-box for instant local execution and CI/CD validation without requiring API keys.

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

3. **Production Testability**:  
   Includes a full `pytest` suite testing multi-agent state passing, schema validation, and report rendering.

---

## 🚀 Quick Start & Installation

### 1. Install Dependencies
```bash
py -3 -m pip install -r requirements.txt
```

### 2. Run the Multi-Agent Pipeline & Launch Dashboard
```bash
py -3 app.py
```
*This automatically processes the sample Job Description and Resume, generates the reports in `output/`, and opens the interactive Web Dashboard in your browser at `http://localhost:8000/dashboard.html`!*

### 3. Run Automated Unit Tests
```bash
py -3 -m pytest tests/
```

---

## 📂 Repository Structure

```
talentpilot_agent/
├── data/
│   └── samples/                  # Pre-loaded sample JD and Resume text files
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
├── requirements.txt              # Project dependencies
└── README.md                     # Technical architecture & portfolio overview
```

---

## 👩‍💻 About the Developer

Built by **Amanda Hervol**, an AI Software Engineer & Workflow Architect with a unique background combining Python multi-agent development with recruiting and career coaching expertise.

- 🔗 [LinkedIn](https://www.linkedin.com/in/amandaa-hervol/)
- 📧 [amandahervol@gmail.com](mailto:amandahervol@gmail.com)
