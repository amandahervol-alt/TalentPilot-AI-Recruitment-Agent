import pytest

import app
from tests.conftest import SAMPLES


def test_run_pipeline_writes_card_and_dashboard(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    app.run_pipeline(str(SAMPLES / "sample_jd_pm.txt"), str(SAMPLES / "sample_resume_pm.txt"), serve=False)

    assert "Jordan Taylor" in (tmp_path / "output/candidate_card.md").read_text(encoding="utf-8")
    assert "Jordan Taylor" in (tmp_path / "output/dashboard.html").read_text(encoding="utf-8")
    out = capsys.readouterr().out
    assert "[+] Candidate: Jordan Taylor (Senior AI Product Manager)" in out
    assert "[+] Match Score: 80/100 (Strong Match)" in out


@pytest.mark.parametrize("missing", ["jd", "resume"])
def test_missing_input_exits_with_error(tmp_path, monkeypatch, missing):
    monkeypatch.chdir(tmp_path)
    jd = tmp_path / "nope.txt" if missing == "jd" else SAMPLES / "sample_jd.txt"
    resume = tmp_path / "nope.txt" if missing == "resume" else SAMPLES / "sample_resume.txt"
    with pytest.raises(SystemExit) as exc:
        app.run_pipeline(str(jd), str(resume), serve=False)
    assert exc.value.code == 1


def _capture(monkeypatch, argv):
    calls = {}
    monkeypatch.setattr(app, "run_pipeline", lambda jd, resume, serve: calls.update(jd=jd, resume=resume, serve=serve))
    monkeypatch.setattr("sys.argv", ["app.py", *argv])
    app.main()
    return calls


@pytest.mark.parametrize("sample", ["engineer", "pm", "analyst"])
def test_cli_samples(monkeypatch, sample):
    calls = _capture(monkeypatch, ["--sample", sample, "--no-serve"])
    assert (calls["jd"], calls["resume"]) == app.SAMPLE_PAIRS[sample]
    assert calls["serve"] is False


def test_cli_defaults_to_engineer_and_serves(monkeypatch):
    calls = _capture(monkeypatch, [])
    assert calls["jd"] == "data/samples/sample_jd.txt"
    assert calls["serve"] is True


def test_cli_custom_files_need_both_paths(monkeypatch):
    assert _capture(monkeypatch, ["--jd", "a.txt", "--resume", "b.txt"])[ "jd"] == "a.txt"
    assert _capture(monkeypatch, ["--jd", "a.txt"])["jd"] == "data/samples/sample_jd.txt"
