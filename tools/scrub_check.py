#!/usr/bin/env python3
"""Scan a folder about to be published (e.g. a GitHub repo) for material that must not go public.

Usage:
  python scrub_check.py <folder> [--deny names.txt]

Flags: confidentiality markings, internal SharePoint/OneDrive tenants, email addresses,
phone numbers, likely secrets (API keys, tokens, private keys), .env / .msg / office files,
Windows user paths, and any word listed in the deny file (one per line, case-insensitive).
Lines containing the marker 'scrub:ok' are skipped (use for reviewed, intentional mentions).
Exit 0 = clean, 1 = findings. Findings print as file:line: rule: excerpt.
"""
import argparse
import os
import re
import sys

RULES = [
    ("marking", re.compile(r"\b(restricted use|internal[- ]restricted|confidential|for official use only|do not distribute|not for circulation)\b", re.I)),  # scrub:ok (rule definition, so the script passes its own check when copied into a repo for CI)
    ("tenant-url", re.compile(r"https?://(?!contoso\.)[a-z0-9-]+\.sharepoint\.com|https?://[a-z0-9-]+-my\.sharepoint\.com", re.I)),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!users\.noreply\.github\.com|example\.(com|org))[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"(?<!\d)(\+\d{1,3}[ .-]?)?(\(?\d{2,4}\)?[ .-]?){2,4}\d{2,4}(?!\d)(?=.*\b(tel|phone|mobile)\b)", re.I)),
    ("secret", re.compile(r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,})", re.I)),
    ("user-path", re.compile(r"[A-Z]:\\Users\\[^\\\s<>]+\\", re.I)),
    ("tenant-id", re.compile(r"\b(tenant[_ -]?id)\b.{0,20}[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)),
]
BAD_FILES = re.compile(r"(^\.env$|\.env\.|\.msg$|\.pst$|\.docx$|\.xlsx$|\.pptx$|\.pdf$)", re.I)
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
TEXT_EXT = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml", ".ps1", ".sh", ".js", ".ts", ".html", ".csv", ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--deny", help="file with words/names to block, one per line")
    a = ap.parse_args()

    deny = []
    if a.deny:
        with open(a.deny, encoding="utf-8") as f:
            deny = [w.strip() for w in f if w.strip() and not w.startswith("#")]
    deny_re = re.compile(r"\b(" + "|".join(map(re.escape, deny)) + r")\b", re.I) if deny else None

    findings = []
    for root, dirs, files in os.walk(a.folder):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, a.folder)
            if BAD_FILES.search(fn):
                findings.append(f"{rel}: file-type: review or remove before publishing")
                continue
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            is_push = fn.upper() == "PUSH.MD"
            with open(path, encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, 1):
                    if "scrub:ok" in line:
                        continue  # explicit, reviewed exception
                    for name, rx in RULES:
                        if name == "user-path" and is_push:
                            continue  # PUSH.md legitimately carries the local path; it is not committed
                        if rx.search(line):
                            findings.append(f"{rel}:{i}: {name}: {line.strip()[:120]}")
                    if deny_re and deny_re.search(line):
                        findings.append(f"{rel}:{i}: deny-list: {line.strip()[:120]}")

    for x in findings:
        print(x)
    print("RESULT:", "FINDINGS" if findings else "CLEAN", f"({len(findings)})")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
