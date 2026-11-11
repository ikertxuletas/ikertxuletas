"""Builds the static README SVGs (hero, stats, projects, build steps, contact) in light and dark.
The languages chart is built by update_langs.py because its data changes."""
from svgkit import EASE, THEMES, W, cycle_css, esc, svg, write

ENDINGS = [
    "reports that arrive on their own.", "answers before your first coffee.", "numbers you can trust.",
    "dashboards that update themselves.", "charts that explain themselves.", "a morning email, not a weekend job.",
    "checks that never skip a step.", "one clean page a day.", "hours back in your week.", "decisions, not spreadsheets.",
]
PROJECTS = [
    ("job-radar", "A personal headhunter that reads the job market every morning."),
    ("Atlas", "Explains why markets moved, then checks whether it was right."),
    ("Quant research", "Tests investment ideas against reality before any money does."),
    ("Trade-fair prospecting", "Builds client lists from trade-fair directories, automatically."),
    ("LeeMe", "Turns any PDF into an audiobook in natural Spanish."),
]
STEPS = ["Collect", "Organise", "Verify", "Enrich with AI", "Deliver"]


def wave_path(y, w, a, b, c):
    q = w / 6
    return f"M0 {y + a:.1f} C {q:.0f} {y - b:.1f}, {2 * q:.0f} {y + c:.1f}, {3 * q:.0f} {y:.1f} S {5 * q:.0f} {y - a:.1f}, {w} {y + b:.1f}"


def wave_lines(t, y, w):
    """Three lines that draw in, then keep moving in slow, offset waves (SMIL, works inside <img>)."""
    out = ""
    for colour, width, opacity, dur, amps, delay in [
            (t["accent"], 1.5, 1, 9, [(6, 8, 7), (-5, -7, -6), (8, -4, 9), (6, 8, 7)], ".5s,3.2s"),
            (t["muted"], 1, 1, 12, [(-4, 5, -6), (6, -6, 5), (-3, 8, -4), (-4, 5, -6)], ".9s,4s"),
            (t["accent"], 1, .35, 15, [(3, -9, 4), (-7, 6, -8), (5, 3, 6), (3, -9, 4)], "1.3s,5s")]:
        ds = [wave_path(y + 4, w, *(v * 1.5 for v in a)) for a in amps]
        out += (f'<path class="vein" style="animation-delay:{delay}" d="{ds[0]}" fill="none" stroke="{colour}" stroke-width="{width}" opacity="{opacity}">'
                f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" calcMode="spline" '
                f'keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1" values="{";".join(ds)}"/></path>')
    return out


def hero(t):
    h = 300
    kf, total = cycle_css("rot", len(ENDINGS), 3.5)
    css = (kf + f".rot{{opacity:0;animation:rot {total}s linear infinite}}"
           f"@keyframes ping{{0%{{transform:scale(1);opacity:.6}}100%{{transform:scale(2.6);opacity:0}}}}"
           f".ping{{transform-origin:6px 22px;animation:ping 2s ease-out infinite}}"
           f"@keyframes draw{{from{{stroke-dashoffset:900}}to{{stroke-dashoffset:0}}}}"
           f"@keyframes shimmer{{0%,100%{{stroke-opacity:.35}}50%{{stroke-opacity:.85}}}}"
           f".vein{{stroke-dasharray:900;animation:draw 2.6s {EASE} .5s both,shimmer 6s ease-in-out 3.2s infinite}}")
    b = (f'<circle class="ping" cx="6" cy="22" r="4" fill="{t["accent"]}"/><circle cx="6" cy="22" r="4" fill="{t["accent"]}"/>'
         f'<text class="r" x="20" y="27" font-size="15" fill="{t["muted"]}">Iker González, Munich. Open to remote roles.</text>'
         f'<text class="r" style="animation-delay:.15s" x="0" y="96" font-size="42" font-weight="700" letter-spacing="-1.9" fill="{t["ink"]}">I turn repetitive data work into</text>')
    for i, e in enumerate(ENDINGS):
        b += (f'<text class="rot" style="animation-delay:{i * 3.5}s" x="0" y="150" font-size="42" font-weight="700" '
              f'letter-spacing="-1.9" fill="{t["accent"]}">{esc(e)}</text>')
    b += wave_lines(t, 186, W)
    for i, line in enumerate(["Finance background, automation mindset. I build tools that collect, check and",
                              "explain numbers, so teams spend their time deciding, not copying."]):
        b += f'<text class="r" style="animation-delay:{.7 + i * .08}s" x="0" y="{236 + i * 28}" font-size="18" fill="{t["muted"]}">{line}</text>'
    return svg(h, b, css, "I turn repetitive data work into reports that arrive on their own. Finance background, automation mindset.")


def stats(t):
    h = 100
    items = [("3", "languages spoken"), ("5", "tools of my own in use"), ("Daily", "reports, no button pressed"), ("100%", "of figures checked")]
    css = "@keyframes breathe{0%,100%{opacity:.82}50%{opacity:1}}.br{animation:breathe 4s ease-in-out infinite}"
    b = ""
    for i, (big, lab) in enumerate(items):
        x = i * W / 4
        col = t["accent"] if big == "Daily" else t["ink"]
        b += (f'<g class="r" style="animation-delay:{.1 + i * .1}s"><text {"class=\"br\" " if big == "Daily" else ""}x="{x}" y="52" font-size="50" '
              f'font-weight="700" letter-spacing="-2.4" fill="{col}">{big}</text>'
              f'<text x="{x}" y="84" font-size="15" font-weight="500" fill="{t["muted"]}">{lab}</text></g>')
    return svg(h, b, css, "3 languages spoken. 5 tools of my own in use. Daily reports with no button pressed. 100% of figures checked.")


def projects(t):
    row, top, n = 80, 56, len(PROJECTS)
    h = top + n * row
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
    b = (f'<defs><radialGradient id="sp"><stop offset="0" stop-color="{t["accent"]}" stop-opacity=".16"/>'
         f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient></defs>'
         f'<text x="0" y="28" font-size="24" font-weight="700" letter-spacing="-0.8" fill="{t["ink"]}">What I\'ve built</text>')
    for i, (name, line) in enumerate(PROJECTS):
        y = top + i * row
        d = f"animation-delay:{i * slot}s"
        b += (f'<g class="enc" style="{d}"><clipPath id="c{i}"><rect x="0.5" y="{y + 4.5}" width="{W - 1}" height="{row - 9}" rx="12"/></clipPath>'
              f'<rect x="0.5" y="{y + 4.5}" width="{W - 1}" height="{row - 9}" rx="12" fill="{t["surface"]}"/>'
              f'<g clip-path="url(#c{i})"><ellipse class="spot" style="{d}" cx="140" cy="{y + row / 2}" rx="180" ry="90" fill="url(#sp)"/></g>'
              f'<rect class="edge" style="{d}" x="0.5" y="{y + 4.5}" width="{W - 1}" height="{row - 9}" rx="12" fill="none" stroke="{t["accent"]}" stroke-opacity=".7"/></g>'
              f'<g class="nud" style="{d}"><text x="20" y="{y + 32}" font-size="14" font-weight="500" fill="{t["muted"]}">{esc(name)}</text>'
              f'<text x="20" y="{y + 58}" font-size="19" font-weight="600" letter-spacing="-0.4" fill="{t["ink"]}">{esc(line)}</text></g>')
    return svg(h, b, css, "What I've built: " + "; ".join(f"{n}: {l}" for n, l in PROJECTS))


def build(t):
    h, n, slot = 120, len(STEPS), 2.4
    total = n * slot
    p = 100 / n
    xs = [0, 175, 355, 520, W]
    widths = [len(st) * 9.4 for st in STEPS]
    starts = [xs[i] if i < n - 1 else W - widths[i] for i in range(n)]
    gw = 140
    centres = [starts[i] + widths[i] / 2 - gw / 2 for i in range(n)]
    frames = "".join(f"{i * p:.1f}%,{i * p + p * 0.7:.1f}%{{transform:translateX({c:.0f}px)}}" for i, c in enumerate(centres))
    css = (f"@keyframes glide{{{frames}100%{{transform:translateX({centres[0]:.0f}px)}}}}"
           f".gl{{animation:glide {total}s cubic-bezier(.65,0,.35,1) infinite}}"
           f"@keyframes lit{{0%{{fill:{t['muted']}}}3%,{p - 3:.1f}%{{fill:{t['accent']}}}{p + 2:.1f}%,100%{{fill:{t['muted']}}}}}"
           f".st{{fill:{t['muted']};animation:lit {total}s ease-in-out infinite}}")
    b = (f'<defs><linearGradient id="gg"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient></defs>'
         f'<text x="0" y="28" font-size="24" font-weight="700" letter-spacing="-0.8" fill="{t["ink"]}">How I build</text>')
    for i, st in enumerate(STEPS):
        b += f'<text class="st" style="animation-delay:{i * slot}s" x="{starts[i]:.0f}" y="70" font-size="17" font-weight="600">{st}</text>'
    b += (f'<rect x="0" y="84" width="{W}" height="1" fill="{t["line"]}"/>'
          f'<rect class="gl" x="0" y="83" width="{gw}" height="3" rx="1.5" fill="url(#gg)"/>'
          f'<text x="0" y="112" font-size="15" font-weight="500" fill="{t["muted"]}">Gather the data, put it in order, check it, explain it and send it to whoever needs it, every day.</text>')
    return svg(h, b, css, "How I build: " + ", ".join(STEPS))


def contact(t):
    h = 110
    b = (f'<text class="r" x="0" y="44" font-size="38" font-weight="700" letter-spacing="-1.7" fill="{t["ink"]}">Have numbers that should</text>'
         f'<text class="r" style="animation-delay:.12s" x="0" y="92" font-size="38" font-weight="700" letter-spacing="-1.7" fill="{t["ink"]}">report themselves? <tspan fill="{t["accent"]}">Let\'s talk.</tspan></text>')
    return svg(h, b, label="Have numbers that should report themselves? Let's talk.")


LINKS = {"portfolio": "Portfolio", "linkedin": "LinkedIn", "email": "iker.g.job@gmail.com",
         "es": "Español", "de": "Deutsch", "jobradar": "job-radar on GitHub"}


def pill(t, text):
    w = round(len(text) * 8.6 + 40)
    b = (f'<rect x="0.5" y="0.5" width="{w - 1}" height="39" rx="19.5" fill="none" stroke="{t["line"]}"/>'
         f'<text x="{w / 2}" y="25.5" text-anchor="middle" font-size="15" font-weight="600" fill="{t["accent"]}">{esc(text)}</text>')
    return svg(40, b, label=text).replace(f'width="{W}" height="40" viewBox="0 0 {W} 40"', f'width="{w}" height="40" viewBox="0 0 {w} 40"')


def note(t):
    b = f'<text x="0" y="18" font-size="15" font-weight="500" fill="{t["muted"]}">job-radar is open source. The rest hold personal or client data; happy to show them on a call.</text>'
    return svg(28, b, label="job-radar is open source. The rest hold personal or client data; happy to show them on a call.")


if __name__ == "__main__":
    for theme, t in THEMES.items():
        for name, fn in [("hero", hero), ("stats", stats), ("projects", projects), ("build", build), ("contact", contact), ("note", note)]:
            write(name, theme, fn(t))
        for key, text in LINKS.items():
            write(f"link-{key}", theme, pill(t, text))
    print("ok")
