from jinja2 import Template
from src.schemas import RecruiterEvaluationCard


class ReportGenerator:
    """Generates Markdown candidate cards and glassmorphism HTML web dashboards."""

    def __init__(self, eval_card: RecruiterEvaluationCard):
        self.card = eval_card

    def generate_markdown(self) -> str:
        c = self.card
        s = c.screening_result

        md = f"""# 📋 {c.system_title}
**Generated**: {c.generated_at}

## 👤 Candidate Profile
* **Name**: {s.candidate_name}
* **Email**: {s.candidate_email}
* **Target Role**: {s.job_title}
* **Match Score**: `{s.overall_match_score}/100` ({s.fit_verdict})

### 🌟 Key Strengths
"""
        for str_item in s.key_strengths:
            md += f"- {str_item}\n"

        md += "\n### ⚠️ Identified Gaps / Probing Areas\n"
        for gap_item in s.identified_gaps:
            md += f"- {gap_item}\n"

        md += "\n---\n\n## 🔍 Tailored Recruiter Interview Questions\n\n"
        for q in c.tailored_questions:
            md += f"### Q{q.question_number} [{q.category}]\n"
            md += f"**Question**: *\"{q.question_text}\"*\n"
            md += f"- **Targeted Signal**: `{q.targeted_gap_or_skill}`\n"
            md += f"- **Ideal Response**: {q.ideal_candidate_answer}\n\n"

        md += "---\n\n## 📊 Candidate Evaluation Rubric (1-5 Scale)\n\n"
        for r in c.evaluation_rubric:
            md += f"### {r.criterion_name} ({r.category} — {r.weight} Weight)\n"
            md += f"- **1/5 (Needs Improvement)**: {r.level_1_poor}\n"
            md += f"- **3/5 (Proficient)**: {r.level_3_proficient}\n"
            md += f"- **5/5 (Expert)**: {r.level_5_expert}\n\n"

        return md

    def generate_html(self) -> str:
        c = self.card
        s = c.screening_result

        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TalentPilot — Candidate Evaluation Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0d1117;
            --card-bg: rgba(22, 27, 34, 0.75);
            --border: rgba(255, 255, 255, 0.1);
            --teal: #2dd4bf;
            --purple: #a855f7;
            --amber: #f59e0b;
            --green: #34d399;
            --red: #f87171;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text-main);
            padding: 2rem;
            line-height: 1.6;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(45, 212, 191, 0.1) 0%, transparent 45%),
                radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.1) 0%, transparent 45%);
            min-height: 100vh;
        }

        .container { max-width: 1100px; margin: 0 auto; }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }

        h1 { font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 700; color: #fff; }
        .timestamp { color: var(--text-muted); font-size: 0.85rem; }

        .profile-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.8rem;
            margin-bottom: 2rem;
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
        }

        .match-score-badge {
            text-align: center;
            background: rgba(45, 212, 191, 0.12);
            border: 1px solid rgba(45, 212, 191, 0.3);
            border-radius: 14px;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .score-num { font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 700; color: var(--teal); }
        .verdict-tag { font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; color: var(--green); }

        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem;
            margin: 2rem 0 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .q-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-left: 4px solid var(--teal);
            border-radius: 12px;
            padding: 1.4rem;
            margin-bottom: 1.2rem;
        }

        .q-tag {
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            background: rgba(168, 85, 247, 0.2);
            color: var(--purple);
            display: inline-block;
            margin-bottom: 0.5rem;
        }

        .rubric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
        }

        .rubric-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.4rem;
        }

        .matrix-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }

        .matrix-table th, .matrix-table td {
            padding: 0.8rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 0.9rem;
        }

        .badge-matched { color: var(--green); font-weight: 600; }
        .badge-gap { color: var(--amber); font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🎯 TalentPilot Candidate Evaluation</h1>
                <div class="timestamp">Multi-Agent AI Pipeline • {{ c.generated_at }}</div>
            </div>
        </header>

        <!-- Candidate Profile & Score -->
        <div class="profile-card">
            <div>
                <h2 style="font-family: 'Outfit'; font-size: 1.6rem; margin-bottom: 0.4rem;">{{ s.candidate_name }}</h2>
                <p style="color: var(--text-muted); margin-bottom: 1rem;"><strong>Target Role:</strong> {{ s.job_title }} | <strong>Email:</strong> {{ s.candidate_email }}</p>
                <div>
                    <strong>Key Strengths:</strong>
                    <ul style="margin-left: 1.2rem; margin-top: 0.3rem;">
                        {% for str_item in s.key_strengths %}
                        <li>{{ str_item }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            <div class="match-score-badge">
                <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Match Score</div>
                <div class="score-num">{{ s.overall_match_score }}</div>
                <div class="verdict-tag">{{ s.fit_verdict }}</div>
            </div>
        </div>

        <!-- Skill Matrix -->
        <div class="section-title">📊 Requirements vs Resume Alignment Matrix</div>
        <table class="matrix-table">
            <thead>
                <tr>
                    <th>Requirement / Competency</th>
                    <th>Alignment Status</th>
                    <th>Evidence / Analysis</th>
                </tr>
            </thead>
            <tbody>
                {% for m in s.skill_matrix %}
                <tr>
                    <td><strong>{{ m.skill_name }}</strong></td>
                    <td class="badge-{{ m.status.lower() }}">{{ m.status }}</td>
                    <td>{{ m.rationale }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <!-- Tailored Questions -->
        <div class="section-title">❓ Tailored Recruiter Interview Guide (Agent 2 Output)</div>
        {% for q in c.tailored_questions %}
        <div class="q-card">
            <span class="q-tag">Q{{ q.question_number }} • {{ q.category }}</span>
            <div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 0.5rem; color: #fff;">"{{ q.question_text }}"</div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;"><strong>Targeted Signal:</strong> {{ q.targeted_gap_or_skill }}</p>
            <p style="font-size: 0.9rem; color: var(--teal);"><strong>Expected Strong Answer:</strong> {{ q.ideal_candidate_answer }}</p>
        </div>
        {% endfor %}

        <!-- Evaluation Rubric -->
        <div class="section-title">📋 Standardized Candidate Evaluation Rubric (1-5 Scale)</div>
        <div class="rubric-grid">
            {% for r in c.evaluation_rubric %}
            <div class="rubric-card">
                <h3 style="font-family: 'Outfit'; font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--purple);">{{ r.criterion_name }}</h3>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.8rem;">Category: {{ r.category }} | Weight: {{ r.weight }}</p>
                <div style="font-size: 0.85rem;">
                    <p style="margin-bottom: 0.4rem;"><strong style="color: var(--red);">1/5 (Needs Improvement):</strong> {{ r.level_1_poor }}</p>
                    <p style="margin-bottom: 0.4rem;"><strong style="color: var(--amber);">3/5 (Proficient):</strong> {{ r.level_3_proficient }}</p>
                    <p><strong style="color: var(--green);">5/5 (Expert):</strong> {{ r.level_5_expert }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""
        # Resume and JD text is untrusted: escape everything rendered into the page.
        template = Template(html_template, autoescape=True)
        return template.render(c=c, s=s)
