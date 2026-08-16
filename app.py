import os
import sys
import argparse
import webbrowser
import http.server
import socketserver
from pathlib import Path

from src.pipeline import TalentPilotPipeline
from src.report_generator import ReportGenerator


def run_pipeline(jd_file: str, resume_file: str, serve: bool = True):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print(f"\n[+] Launching TalentPilot Multi-Agent Recruitment Pipeline...")
    jd_path = Path(jd_file)
    resume_path = Path(resume_file)

    if not jd_path.exists() or not resume_path.exists():
        print(f"[!] Input files missing: {jd_file} or {resume_file}")
        sys.exit(1)

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    with open(resume_path, "r", encoding="utf-8") as f:
        resume_text = f.read()

    print(f"[*] Agent 1: Screening candidate resume against job description...")
    pipeline = TalentPilotPipeline()
    eval_card = pipeline.run(jd_text, resume_text)

    print(f"[*] Agent 2: Generating tailored interview questions & 1-5 evaluation rubric...")

    generator = ReportGenerator(eval_card)
    markdown_out = generator.generate_markdown()
    html_out = generator.generate_html()

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    md_file = output_dir / "candidate_card.md"
    html_file = output_dir / "dashboard.html"

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown_out)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_out)

    s = eval_card.screening_result
    print(f"\n[OK] Pipeline Execution Complete!")
    print(f"[+] Candidate: {s.candidate_name} ({s.job_title})")
    print(f"[+] Match Score: {s.overall_match_score}/100 ({s.fit_verdict})")
    print(f"[+] Markdown Report generated: {md_file.resolve()}")
    print(f"[+] HTML Dashboard generated: {html_file.resolve()}")

    if serve:
        print("\n🌐 Launching local HTTP dashboard server at http://localhost:8000 ...")
        os.chdir(output_dir)
        handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True
        try:
            with socketserver.TCPServer(("", 8000), handler) as httpd:
                webbrowser.open("http://localhost:8000/dashboard.html")
                print("Press Ctrl+C to stop the dashboard server.")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def main():
    parser = argparse.ArgumentParser(description="TalentPilot Multi-Agent Recruitment System")
    parser.add_argument("--jd", type=str, default="data/samples/sample_jd.txt", help="Path to JD file")
    parser.add_argument("--resume", type=str, default="data/samples/sample_resume.txt", help="Path to Resume file")
    parser.add_argument("--no-serve", action="store_true", help="Do not launch HTTP server")

    args = parser.parse_args()
    run_pipeline(args.jd, args.resume, serve=not args.no_serve)


if __name__ == "__main__":
    main()
