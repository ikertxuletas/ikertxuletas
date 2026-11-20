"""Activity card for the profile README: which allowlisted projects moved lately, measured with the GitHub CLI.
The allowlist lives outside this public repo, so private repository names never land here."""
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from svgkit import EASE, THEMES, W, esc, svg

ALLOW_PATH = Path(__file__).resolve().parents[2] / "activity_projects.json"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
WEEKS = 12
ROWS = 4


def gh(*args):
    return subprocess.run(("gh", *args), capture_output=True, text=True, encoding="utf-8",
                          check=True, creationflags=NO_WINDOW).stdout


def load_allow(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def weekly_buckets(dates, today, weeks=WEEKS):
    out = [0] * weeks
    for d in dates:
        age = (today - d).days
        if 0 <= age < weeks * 7:
            out[weeks - 1 - age // 7] += 1
    return out


def fmt_day(d):
    return f"{d.day} {MONTHS[d.month - 1]}"


def pick_rows(repos, allow):
    return sorted((r for r in repos if r["name"] in allow), key=lambda r: r["pushedAt"], reverse=True)[:ROWS]


def commit_dates(owner, repo, since):
    try:
        out = gh("api", "--paginate", f"repos/{owner}/{repo}/commits?since={since:%Y-%m-%dT%H:%M:%SZ}&per_page=100",
                 "--jq", ".[].commit.committer.date")
    except subprocess.CalledProcessError as e:
        if "409" in e.stderr or "empty" in e.stderr.lower():
            return []
        raise
    return [datetime.fromisoformat(s).date() for s in out.split()]


def measure(owner, allow):
    repos = json.loads(gh("repo", "list", owner, "-L", "200", "--json", "name,pushedAt"))
    now = datetime.now(timezone.utc)
    today = now.date()
    since = now - timedelta(days=WEEKS * 7)
    # The profile repo is skipped in the totals: its commits are this job's own daily updates.
    dates = {r["name"]: commit_dates(owner, r["name"], since) for r in repos if r["name"] != owner}
    rows = [{"name": allow[r["name"]][0], "line": allow[r["name"]][1],
             "last": fmt_day(datetime.fromisoformat(r["pushedAt"]).date()),
             "weeks": weekly_buckets(dates.get(r["name"], []), today)} for r in pick_rows(repos, allow)]
    commits_30d = sum(1 for ds in dates.values() for d in ds if (today - d).days < 30)
    return {"commits_30d": commits_30d, "repos": len(repos), "rows": rows}, [r["name"] for r in repos]


def check_private(texts, hidden):
    low = [t.lower() for t in texts]
    leaked = [h for h in hidden if any(h.lower() in t for t in low)]
    assert not leaked, f"hidden repositories in output: {leaked}"


def spark(t, weeks, gmax, x0, base, w=110, h=18):
    step = w / (len(weeks) - 1)
    # Square-root scale: one busy week would otherwise flatten every other row.
    pts = " ".join(f"{x0 + i * step:.1f},{base - h * (v / gmax) ** .5:.1f}" for i, v in enumerate(weeks))
    return (f'<polyline points="{pts}" fill="none" stroke="{t["accent"]}" stroke-width="1.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def card(t, data):
    """Same row geometry and highlight cycle as projects() in build_svgs.py, plus a date and a 12-week commit line."""
    rows, row, top, foot = data["rows"], 80, 56, 34
    n = max(len(rows), 1)
    h = top + len(rows) * row + foot
    slot = 3.0
    total = n * slot
    p = 100 / n
    per = 2 * (W + row - 8)
    css = (f"@keyframes enc{{0%{{opacity:0}}3%{{opacity:1}}{p - 2:.1f}%{{opacity:1}}{p + 1:.1f}%{{opacity:0}}100%{{opacity:0}}}}"
           f"@keyframes edge{{0%{{stroke-dashoffset:{per}}}6%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}"
           f"@keyframes nudge{{0%{{transform:none}}3%{{transform:translateX(8px)}}{p - 2:.1f}%{{transform:translateX(8px)}}{p + 1:.1f}%{{transform:none}}100%{{transform:none}}}}"
           f"@keyframes spot{{0%{{transform:translateX(0)}}{p:.1f}%{{transform:translateX(560px)}}100%{{transform:translateX(560px)}}}}"
           f".enc{{opacity:0;animation:enc {total}s ease-in-out infinite}}"
           f".edge{{stroke-dasharray:{per};animation:edge {total}s {EASE} infinite}}"
           f".nud{{animation:nudge {total}s {EASE} infinite}}"
           f".spot{{animation:spot {total}s ease-in-out infinite}}")
    gmax = max([max(r["weeks"]) for r in rows] + [1])
    b = (f'<defs><radialGradient id="sp"><stop offset="0" stop-color="{t["accent"]}" stop-opacity=".16"/>'
         f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>'
         f'<text x="0" y="28" font-size="24" font-weight="700" letter-spacing="-0.8" fill="{t["ink"]}">Working on now</text>')
    for i, r in enumerate(rows):
        y = top + i * row
        d = f"animation-delay:{i * slot}s"
        b += (f'<g class="enc" style="{d}"><clipPath id="c{i}"><rect x="0.5" y="{y + 4.5}" width="{W - 1}" height="{row - 9}" rx="12"/></clipPath>'
              f'<rect x="0.5" y="{y + 4.5}" width="{W - 1}" height="{row - 9}" rx="12" fill="{t["surface"]}"/>'
              f'<g clip-path="url(#c{i})"><ellipse class="spot" style="{d}" cx="140" cy="{y + row / 2}" rx="180" ry="90" fill="url(#sp)"/></g>'
              f'<rect class="edge" style="{d}" x="0.5" y="{y + 4.5}" width="{W - 1}" height="{row - 9}" rx="12" fill="none" stroke="{t["accent"]}" stroke-opacity=".7"/></g>'
              f'<g class="nud" style="{d}"><text x="20" y="{y + 32}" font-size="14" font-weight="500" fill="{t["muted"]}">{esc(r["name"])}</text>'
              f'<text x="20" y="{y + 58}" font-size="19" font-weight="600" letter-spacing="-0.4" fill="{t["ink"]}">{esc(r["line"])}</text></g>'
              + spark(t, r["weeks"], gmax, W - 290, y + 33) +
              f'<text x="{W - 20}" y="{y + 32}" text-anchor="end" font-size="14" fill="{t["muted"]}">last commit {esc(r["last"])}</text>')
    foot_text = (f'{data["commits_30d"]} commits in the last 30 days across {data["repos"]} repositories, '
                 f'public and private. Updated daily.')
    b += f'<text x="0" y="{h - 8}" font-size="14" fill="{t["muted"]}">{foot_text}</text>'
    label = "Working on now: " + "; ".join(f'{r["name"]}: {r["line"]} Last commit {r["last"]}' for r in rows) + ". " + foot_text
    return svg(h, b, css, label)


def selfcheck():
    today = date(2026, 11, 20)
    assert weekly_buckets([today, today - timedelta(days=6), today - timedelta(days=7), today - timedelta(days=83),
                           today - timedelta(days=84)], today) == [1] + [0] * 9 + [1, 2]
    assert weekly_buckets([], today) == [0] * 12
    assert fmt_day(date(2026, 11, 19)) == "19 Nov" and fmt_day(date(2026, 5, 3)) == "3 May"
    assert pick_rows([{"name": "gone", "pushedAt": "2026-11-19T00:00:00Z"}], {"x": ["X", "x"]}) == []
    check_private(["Quant research"], ["hidden-repo"])
    try:
        check_private(["... Hidden-Repo ..."], ["hidden-repo"])
        raise SystemExit("guard failed")
    except AssertionError:
        pass
    s = card(THEMES["dark"], {"commits_30d": 142, "repos": 10,
                              "rows": [{"name": "A", "line": "b", "last": "19 Nov", "weeks": [0] * 12}]})
    assert "142 commits in the last 30 days across 10 repositories, public and private. Updated daily." in s
    assert "last commit 19 Nov" in s
    print("ok")


if __name__ == "__main__" and "--selfcheck" in sys.argv:
    selfcheck()
