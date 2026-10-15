import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from audit_results import ROOT, read_run, require, verify_expected_failure


def run_logged(command, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    with log_path.open("w", encoding="utf-8") as log:
        print("\n> " + subprocess.list2cmdline(command), flush=True)
        with subprocess.Popen(command, cwd=ROOT, env=environment, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                              errors="replace") as process:
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
            return process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--artifact-dir", type=Path, default=Path("test-results"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    args = parser.parse_args()
    report_dir = (ROOT / args.report_dir).resolve()
    artifact_dir = (ROOT / args.artifact_dir).resolve()
    evidence_dir = (ROOT / args.evidence_dir).resolve()
    for path in (report_dir, artifact_dir, evidence_dir):
        require(path.is_relative_to(ROOT), "输出目录必须位于项目内")
        path.mkdir(parents=True, exist_ok=True)

    previous = evidence_dir / "validation.json"
    if previous.exists():
        history = evidence_dir / "history"
        history.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        previous.replace(history / f"validation-{stamp}.json")
    plans = [
        ("results", [], "regression", 0),
        ("independent", ["tests/test_checkout.py::test_complete_purchase"], "independent", 0),
        ("failure-demo", ["failure_lab/test_diagnostics.py", "--failure-demo"], "failure-demo", 1),
        ("recovered", ["failure_lab/test_diagnostics.py"], "recovered", 0),
    ]
    failures = []
    for name, selection, artifact_name, expected_exit in plans:
        html_name = "report" if name == "results" else name
        xml = report_dir / f"{name}.xml"

        xml.unlink(missing_ok=True)
        command = [sys.executable, "-m", "pytest", *selection,
                   f"--output={artifact_dir / artifact_name}",
                   f"--html={report_dir / (html_name + '.html')}",
                   f"--junitxml={xml}", "--tb=short"]
        code = run_logged(command, report_dir / f"{name}-run.txt")
        try:
            require(code == expected_exit, f"{name} 退出码为 {code}，预期为 {expected_exit}")
            run = read_run(name, report_dir)
            if name == "failure-demo":
                verify_expected_failure(run)
            else:
                require(run["tests"] > 0 and run["passed"] == run["tests"], f"{name} 未全部通过")
        except (ValueError, OSError) as error:
            failures.append(str(error))
    if not failures:
        command = [sys.executable, str(ROOT / "scripts/audit_results.py"),
                   "--report-dir", str(report_dir), "--artifact-dir", str(artifact_dir),
                   "--evidence-dir", str(evidence_dir)]
        if run_logged(command, report_dir / "audit-run.txt") != 0:
            failures.append("报告或失败证据核验未通过")
    status = {"success": not failures, "errors": failures,
              "report": (report_dir / "report.html").relative_to(ROOT).as_posix()}
    (report_dir / "acceptance.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write("## UI project validation\n\n")
            for name, *_ in plans:
                try:
                    result = read_run(name, report_dir)
                    label = "expected assertion failure" if name == "failure-demo" else "test run"
                    output.write(f"- {name} ({label}): {result['passed']} passed, "
                                 f"{result['failures']} failed, {result['errors']} errors, "
                                 f"{result['skipped']} skipped\n")
                except (OSError, ValueError):
                    output.write(f"- {name}: results unavailable\n")
            output.write("\nAcceptance: " + ("PASS" if not failures else "FAIL") + "\n")
    print("\nAcceptance: " + ("PASS" if not failures else "FAIL"), flush=True)
    for error in failures:
        print(error, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
