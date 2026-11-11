"""Daily job: measures the languages across all of the owner's repositories with the GitHub CLI,
rebuilds the languages chart (light and dark) and pushes it if anything changed. No AI involved."""
import json
import math
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from svgkit import ASSETS, EASE, THEMES, W, cycle_css, esc, svg, write

OWNER = "ikertxuletas"
REPO = Path(__file__).resolve().parent.parent
LOG = REPO.parent / "update_langs.log"
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
USES = {
    "Python": "pipelines, scrapers, checks and the daily reports",
    "JavaScript": "dashboards and interactive reports",
    "HTML": "the report pages anyone can open",
    "TypeScript": "typed tooling for bigger web projects",
    "CSS": "making reports readable at a glance",
    "PowerShell": "Windows automation and scheduled tasks",
}


def run(*cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                          check=True, creationflags=NO_WINDOW).stdout


def measure():
    repos = json.loads(run("gh", "repo", "list", OWNER, "-L", "200", "--json", "name"))
    total = Counter()
    for r in repos:
        total.update(json.loads(run("gh", "api", f"repos/{OWNER}/{r['name']}/languages")))
    s = sum(total.values())
    top = [(k, round(100 * v / s, 1)) for k, v in total.most_common(5)]
    rest = round(100 - sum(p for _, p in top), 1)
    if rest >= 0.5:
        top.append(("Other", rest))
    assert abs(sum(p for _, p in top) - 100) < 1, top
    return len(repos), top


def chart(t, n_repos, langs):
    h, cx, cy, r = 300, 140, 170, 100
    circ = 2 * math.pi * r
    colors = [t["accent"], t["accent2"], t["faint"], t["muted"], t["dim"], t["line"]]
    slot = 3.0
    kf, total = cycle_css("cyc", len(langs), slot)
    p = 100 / len(langs)
    css = (kf + f".cyc{{opacity:0;animation:cyc {total}s linear infinite}}"
           f"@keyframes thick{{0%{{stroke-width:20;opacity:.55}}2%{{stroke-width:32;opacity:1}}{p - 2:.1f}%{{stroke-width:32;opacity:1}}{p:.1f}%{{stroke-width:20;opacity:.55}}100%{{stroke-width:20;opacity:.55}}}}"
           f".seg{{opacity:.55;animation:thick {total}s {EASE} infinite}}"
           f"@keyframes row{{0%{{opacity:0}}2%{{opacity:1}}{p - 2:.1f}%{{opacity:1}}{p:.1f}%{{opacity:0}}100%{{opacity:0}}}}"
           f".row{{opacity:0;animation:row {total}s ease-in-out infinite}}"
           f"@keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}"
           f".orb{{transform-origin:{cx}px {cy}px;animation:spin 18s linear infinite}}")
    b = (f'<text x="0" y="28" font-size="24" font-weight="700" letter-spacing="-0.8" fill="{t["ink"]}">What my code is made of</text>'
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["surface"]}" stroke-width="20"/>'
         f'<g transform="rotate(-90 {cx} {cy})">')
    start = 0.0
    for i, (name, pct) in enumerate(langs):
        ln = circ * pct / 100
        gap = min(4, ln * 0.3)
        b += (f'<circle class="seg" style="animation-delay:{i * slot}s" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colors[i]}" '
              f'stroke-width="20" stroke-dasharray="{ln - gap:.2f} {circ - ln + gap:.2f}" stroke-dashoffset="{-start:.2f}"/>')
        start += ln
    b += f'</g><g class="orb"><circle cx="{cx}" cy="{cy - r - 20}" r="3" fill="{t["accent"]}"/></g>'
    lx = 320
    for i, (name, pct) in enumerate(langs):
        y = 74 + i * 38
        d = f"animation-delay:{i * slot}s"
        b += (f'<text class="cyc" style="{d}" x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="44" font-weight="700" letter-spacing="-2" fill="{colors[i] if i < 2 else t["ink"]}">{pct:g}%</text>'
              f'<text class="cyc" style="{d}" x="{cx}" y="{cy + 34}" text-anchor="middle" font-size="14" fill="{t["muted"]}">{esc(name)}</text>'
              f'<rect class="row" style="{d}" x="{lx - 14}" y="{y - 24}" width="{W - lx + 14}" height="34" rx="10" fill="{t["surface"]}"/>'
              f'<circle cx="{lx + 4}" cy="{y - 7}" r="5" fill="{colors[i]}"/>'
              f'<text x="{lx + 20}" y="{y - 2}" font-size="16" font-weight="600" fill="{t["ink"]}">{esc(name)}</text>'
              f'<text x="{lx + 140}" y="{y - 2}" font-size="14" fill="{t["muted"]}">{pct:g}%  {esc(USES.get(name, ""))}</text>')
    b += f'<text x="{lx}" y="{h - 8}" font-size="13" fill="{t["muted"]}">Measured across my {n_repos} repositories, public and private. Updated daily.</text>'
    label = "Languages across my code: " + ", ".join(f"{n} {p:g}%" for n, p in langs)
    return svg(h, b, css, label)


def main():
    n_repos, langs = measure()
    data = ASSETS / "langs.json"
    new = json.dumps({"repos": n_repos, "langs": langs}, indent=1)
    if "--force" not in sys.argv and data.exists() and data.read_text(encoding="utf-8") == new:
        return "unchanged"
    for theme, t in THEMES.items():
        write("langs", theme, chart(t, n_repos, langs))
    data.write_text(new, encoding="utf-8")
    if "--no-push" in sys.argv:
        return "built"
    run("git", "pull", "--rebase", "-q")
    run("git", "add", "assets/langs-dark.svg", "assets/langs-light.svg", "assets/langs.json")
    run("git", "commit", "-q", "-m", "Update languages chart")
    run("git", "push", "-q")
    return "pushed"


if __name__ == "__main__":
    try:
        result = main()
    except Exception as e:
        result = f"error: {e}"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M} {result}\n")
