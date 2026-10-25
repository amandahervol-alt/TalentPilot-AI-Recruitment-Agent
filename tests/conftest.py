import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SAMPLES = ROOT / "data" / "samples"
PAIRS = {
    "engineer": ("sample_jd.txt", "sample_resume.txt"),
    "pm": ("sample_jd_pm.txt", "sample_resume_pm.txt"),
    "analyst": ("sample_jd_analyst.txt", "sample_resume_analyst.txt"),
}


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    """No LLM keys, so the deterministic engines run unless a test opts in."""
    monkeypatch.chdir(ROOT)
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_MODEL"):
        monkeypatch.delenv(key, raising=False)


def load_pair(role: str):
    jd, resume = PAIRS[role]
    return (SAMPLES / jd).read_text(encoding="utf-8"), (SAMPLES / resume).read_text(encoding="utf-8")
