#!/usr/bin/env python3
"""
Northstar Launch Monitor
Eli | March 23, 2026 | Day 4

Checks launch health signals every session:
- GitHub stars, forks, open issues
- CI status
- Landing page availability
- License requests in issues
- ClawHub listing status

Usage:
    python3 scripts/launch_monitor.py
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

# ---- Config ----------------------------------------------------------------

GITHUB_REPO = "Daveglaser0823/northstar-skill"
LANDING_PAGE = "https://daveglaser0823.github.io/northstar-skill/"
CLAWHUB_LISTING = "https://clawhub.ai/Daveglaser0823/northstar"

# ---- Helpers ---------------------------------------------------------------

def http_get(url: str, headers: dict = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return 0, b""

def github_api(path: str) -> dict:
    url = f"https://api.github.com/{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "NorthstarMonitor/1.0",
    }
    code, data = http_get(url, headers)
    if code == 200:
        return json.loads(data)
    return {}

# ---- Checks ----------------------------------------------------------------

def check_github_repo():
    data = github_api(f"repos/{GITHUB_REPO}")
    if not data:
        return {"ok": False, "error": "GitHub API unavailable"}
    return {
        "ok": True,
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "watchers": data.get("subscribers_count", 0),
    }

def check_open_issues():
    data = github_api(f"repos/{GITHUB_REPO}/issues?state=open&per_page=20")
    if not isinstance(data, list):
        return {"ok": False, "license_requests": [], "bug_reports": [], "other": []}

    license_requests = []
    bug_reports = []
    other = []

    for issue in data:
        title = issue.get("title", "")
        labels = [lbl.get("name", "") for lbl in issue.get("labels", [])]
        item = {
            "number": issue.get("number"),
            "title": title,
            "created_at": issue.get("created_at", "")[:10],
            "labels": labels,
        }
        if "license-request" in labels or "License Request" in title:
            license_requests.append(item)
        elif "bug" in labels:
            bug_reports.append(item)
        else:
            other.append(item)

    return {
        "ok": True,
        "license_requests": license_requests,
        "bug_reports": bug_reports,
        "other": other,
    }

def check_ci():
    data = github_api(f"repos/{GITHUB_REPO}/actions/runs?per_page=3")
    runs = data.get("workflow_runs", []) if isinstance(data, dict) else []
    if not runs:
        return {"ok": False, "latest": None}
    latest = runs[0]
    return {
        "ok": latest.get("conclusion") == "success",
        "latest": {
            "name": latest.get("name"),
            "status": latest.get("status"),
            "conclusion": latest.get("conclusion"),
            "created_at": latest.get("created_at", "")[:16],
        }
    }

def check_url(url: str, label: str) -> dict:
    code, _ = http_get(url)
    return {"ok": code == 200, "status": code, "url": url, "label": label}

# ---- Report ----------------------------------------------------------------

def print_report(repo, issues, ci, landing, clawhub):
    now = datetime.now().strftime("%Y-%m-%d %H:%M ET")
    print()
    print(f"{'━'*54}")
    print(f"  Northstar Launch Monitor | {now}")
    print(f"{'━'*54}")

    # GitHub stats
    if repo["ok"]:
        stars = repo["stars"]
        forks = repo["forks"]
        open_i = repo["open_issues"]
        print("\n📊 GitHub Repo")
        print(f"   Stars:       {stars}  {'⭐ Great!' if stars > 15 else '📍 Pre-launch' if stars == 0 else ''}")
        print(f"   Forks:       {forks}")
        print(f"   Open Issues: {open_i}")
    else:
        print("\n❌ GitHub API unavailable")

    # Open issues detail
    if issues["ok"]:
        lr = issues["license_requests"]
        bugs = issues["bug_reports"]
        other = issues["other"]

        if lr:
            print(f"\n🎯 LICENSE REQUESTS ({len(lr)}) -- CUSTOMER ZERO PROTOCOL")
            for req in lr:
                print(f"   #{req['number']}: {req['title']} ({req['created_at']})")
        if bugs:
            print(f"\n🐛 Bug Reports ({len(bugs)})")
            for bug in bugs:
                print(f"   #{bug['number']}: {bug['title']}")
        if not lr and not bugs:
            print("\n   No open license requests or bug reports.")
        if other:
            print(f"\n   Other issues: {len(other)}")

    # CI status
    print("\n🔄 CI Status")
    if ci["ok"] and ci["latest"]:
        run = ci["latest"]
        symbol = "✅" if run.get("conclusion") == "success" else "❌"
        print(f"   {symbol} {run['name']}: {run['conclusion']} ({run['created_at']})")
    elif ci["latest"]:
        run = ci["latest"]
        print(f"   ⏳ {run['name']}: {run['status']}")
    else:
        print("   ❓ No CI runs found")

    # Infrastructure
    print("\n🌐 Infrastructure")
    for check in [landing, clawhub]:
        symbol = "✅" if check["ok"] else "❌"
        print(f"   {symbol} {check['label']}: HTTP {check['status']}")

    # Assessment
    print("\n📋 Assessment")
    if repo["ok"]:
        stars = repo["stars"]
        lr_count = len(issues.get("license_requests", []))
        if lr_count > 0:
            print(f"   🚨 ACTION REQUIRED: {lr_count} license request(s) pending!")
            print("      See CUSTOMER-ZERO-RESPONSE.md immediately.")
        elif stars == 0:
            print("   📍 Pre-launch. Stars: 0. No requests yet.")
        elif stars < 5:
            print(f"   📌 Early signal. Stars: {stars}. Watch through Day 7.")
        elif stars < 15:
            print(f"   📈 Good signal. Stars: {stars}. Stay the course.")
        else:
            print(f"   🔥 Strong signal. Stars: {stars}. Activate Tier 2 distribution.")
    
    print(f"\n{'━'*54}")
    print()

# ---- Main ------------------------------------------------------------------

def main():
    repo = check_github_repo()
    issues = check_open_issues()
    ci = check_ci()
    landing = check_url(LANDING_PAGE, "Landing Page")
    clawhub = check_url(CLAWHUB_LISTING, "ClawHub Listing")

    print_report(repo, issues, ci, landing, clawhub)

    # Exit with code 1 if there are license requests (alerts Eli immediately)
    if issues.get("license_requests"):
        sys.exit(1)

if __name__ == "__main__":
    main()
