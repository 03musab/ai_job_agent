#!/usr/bin/env python3
"""
Security Audit Report Generator
Parses Bandit (code SAST) and pip-audit (dependency CVEs) JSON results
and generates a structured, professional Markdown report (SECURITY_REPORT.md).
"""

import json
import os
import sys
from datetime import datetime, timezone

BANDIT_FILE = "bandit_results.json"
PIP_AUDIT_FILE = "pip_audit_results.json"
OUTPUT_REPORT = "SECURITY_REPORT.md"

def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Warning] Failed to load {path}: {e}", file=sys.stderr)
        return None

def build_markdown_report():
    bandit_data = load_json(BANDIT_FILE)
    pip_data = load_json(PIP_AUDIT_FILE)

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_sha = os.environ.get("GITHUB_SHA", "Local Workspace")
    ref_name = os.environ.get("GITHUB_REF_NAME", "main")

    bandit_results = bandit_data.get("results", []) if bandit_data else []

    high_code = [r for r in bandit_results if r.get("issue_severity") == "HIGH"]
    med_code = [r for r in bandit_results if r.get("issue_severity") == "MEDIUM"]
    low_code = [r for r in bandit_results if r.get("issue_severity") == "LOW"]

    # Parse and deduplicate pip-audit vulnerabilities
    raw_vulns = []
    if pip_data and isinstance(pip_data, dict):
        dependencies = pip_data.get("dependencies", [])
        for dep in dependencies:
            name = dep.get("name")
            version = dep.get("version")
            vulns = dep.get("vulns", [])
            for v in vulns:
                raw_vulns.append({
                    "package": name,
                    "version": version,
                    "id": v.get("id", "Unknown"),
                    "fix_versions": ", ".join(v.get("fix_versions", [])) or "None specified",
                    "description": v.get("description", "No description provided.")
                })
    elif pip_data and isinstance(pip_data, list):
        for dep in pip_data:
            name = dep.get("name")
            version = dep.get("version")
            vulns = dep.get("vulns", [])
            for v in vulns:
                raw_vulns.append({
                    "package": name,
                    "version": version,
                    "id": v.get("id", "Unknown"),
                    "fix_versions": ", ".join(v.get("fix_versions", [])) or "None specified",
                    "description": v.get("description", "No description provided.")
                })

    # Deduplicate CVEs by (package, advisory_id)
    seen_cves = set()
    cve_findings = []
    for item in raw_vulns:
        key = (item["package"], item["id"])
        if key not in seen_cves:
            seen_cves.add(key)
            cve_findings.append(item)

    total_issues = len(bandit_results) + len(cve_findings)

    # Determine status badge
    if len(high_code) > 0 or len(cve_findings) > 0:
        status_badge = "🔴 **Action Required**"
    elif len(med_code) > 0:
        status_badge = "🟡 **Review Recommended**"
    else:
        status_badge = "🟢 **Passing / Clean**"

    lines = []
    lines.append("# 🛡️ Automated Security Audit Report")
    lines.append("")
    lines.append(f"> **Status:** {status_badge}  ")
    lines.append(f"> **Generated:** `{now_utc}`  ")
    lines.append(f"> **Branch/Ref:** `{ref_name}` (`{commit_sha[:8] if len(commit_sha) >= 8 else commit_sha}`)  ")
    lines.append("")

    lines.append("## 📊 Executive Summary")
    lines.append("")
    lines.append("| Category | Findings | Severity Note |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **🚨 High Severity (Code)** | `{len(high_code)}` | Critical flaws, injection, or hardcoded secrets |")
    lines.append(f"| **⚠️ Medium Severity (Code)** | `{len(med_code)}` | Weak crypto, insecure configs, or unvalidated parameters |")
    lines.append(f"| **ℹ️ Low Severity (Code)** | `{len(low_code)}` | Information leaks or minor code hygiene warnings |")
    lines.append(f"| **📦 Known CVEs (Dependencies)** | `{len(cve_findings)}` | Vulnerabilities identified in third-party packages |")
    lines.append(f"| **Total Security Items** | `{total_issues}` | Combined code & dependency signals |")
    lines.append("")

    # Section 1: Code Security Vulnerabilities (Bandit)
    lines.append("## 🔍 Code Security Vulnerabilities (SAST)")
    lines.append("")
    if not bandit_results:
        lines.append("✅ **No code security anti-patterns identified by Bandit.**")
    else:
        all_sorted = high_code + med_code + low_code
        lines.append(f"Identified `{len(all_sorted)}` code security items across Python source files:")
        lines.append("")

        for idx, issue in enumerate(all_sorted, 1):
            severity = issue.get("issue_severity", "LOW")
            sev_icon = "🚨 HIGH" if severity == "HIGH" else ("⚠️ MEDIUM" if severity == "MEDIUM" else "ℹ️ LOW")
            test_id = issue.get("test_id", "")
            test_name = issue.get("test_name", "")
            filename = issue.get("filename", "").replace("\\", "/")
            line_no = issue.get("line_number", "")
            issue_text = issue.get("issue_text", "")
            more_info = issue.get("more_info", "")
            code = issue.get("code", "").strip()

            lines.append(f"### {idx}. [{sev_icon}] {issue_text}")
            lines.append(f"- **File:** [`{filename}:{line_no}`]({filename}#L{line_no})")
            lines.append(f"- **Rule ID:** `{test_id}` ({test_name})")
            if more_info:
                lines.append(f"- **Advisory:** [Bandit Documentation]({more_info})")
            lines.append("")
            if code:
                lines.append("```python")
                lines.append(code)
                lines.append("```")
                lines.append("")

    # Section 2: Dependency Vulnerability Scan (CVEs)
    lines.append("## 📦 Dependency Vulnerability Scan (CVEs)")
    lines.append("")
    if not cve_findings:
        lines.append("✅ **No vulnerable third-party dependencies detected.** All scanned packages comply with published security advisories.")
    else:
        lines.append(f"Found `{len(cve_findings)}` unique CVE advisories across dependencies:")
        lines.append("")
        lines.append("| Package | Installed Version | Advisory / CVE | Suggested Remediation Version |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for cve in cve_findings:
            cve_id = cve['id']
            link = f"https://osv.dev/vulnerability/{cve_id}" if "CVE" in cve_id or "PYSEC" in cve_id or "GHSA" in cve_id else f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            lines.append(f"| **`{cve['package']}`** | `{cve['version']}` | [`{cve_id}`]({link}) | `{cve['fix_versions']}` |")
        lines.append("")

    # Section 3: Remediation Checklist
    lines.append("## 🛠️ Security Remediation Guidance")
    lines.append("")
    lines.append("- [ ] **Rotate / Environment Variables**: Ensure all database URLs, API tokens, and JWT secrets are injected via `.env` or GitHub Secrets, never hardcoded in source.")
    lines.append("- [ ] **Parameterized Queries**: Verify that SQL queries in `app.py` use SQLAlchemy ORM or bound parameters (`db.session.execute(text(...), {'param': val})`).")
    lines.append("- [ ] **Dependency Patching**: Run `pip install --upgrade <package>` to bump flagged libraries to their recommended patch versions.")
    lines.append("- [ ] **CSRF & Session Hardening**: Ensure `WTF_CSRF_ENABLED=True` and secure cookie flags (`SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`) are active.")
    lines.append("")
    lines.append("---")
    lines.append("*This report is automatically generated and updated on each push and scheduled audit by the AI JobSnap Security Agent workflow.*")

    report_content = "\n".join(lines) + "\n"

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[Success] Generated {OUTPUT_REPORT} with {total_issues} findings.")
    return total_issues

if __name__ == "__main__":
    build_markdown_report()
