"""Shared helpers for the profile README SVGs: themes, embedded font and the SVG wrapper."""
import base64
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE.parent / "assets"
FONT = base64.b64encode((HERE / "geist.woff2").read_bytes()).decode()
EASE = "cubic-bezier(.23,1,.32,1)"
W = 860

THEMES = {
    "dark": {"ink": "#f0f6fc", "muted": "#9198a1", "line": "#3d444d", "surface": "#1c232e",
             "accent": "#C9B48A", "accent2": "#8C7748", "faint": "#6e7681", "dim": "#3d444d"},
    "light": {"ink": "#1f2328", "muted": "#59636e", "line": "#d1d9e0", "surface": "#f2eee7",
              "accent": "#7A6034", "accent2": "#A99D88", "faint": "#8c959f", "dim": "#d1d9e0"},
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def svg(h, body, css="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'role="img" aria-label="{esc(label)}"><style>'
            f'@font-face{{font-family:G;src:url(data:font/woff2;base64,{FONT}) format("woff2");font-weight:400 700}}'
            f'text{{font-family:G,"Segoe UI",Helvetica,Arial,sans-serif}}'
            f'@keyframes rise{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}'
            f'.r{{animation:rise .8s {EASE} both}}'
            f'{css}'
            f'@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}'
            f'</style>{body}</svg>')


def cycle_css(name, n, slot):
    """Keyframes for n items shown one after another, each for `slot` seconds of an n*slot cycle."""
    total = n * slot
    p = 100 / n
    fade = min(p * 0.15, 1.6)
    return (f"@keyframes {name}{{0%{{opacity:0;transform:translateY(10px)}}{fade:.2f}%{{opacity:1;transform:none}}"
            f"{p - fade:.2f}%{{opacity:1;transform:none}}{p:.2f}%{{opacity:0;transform:translateY(-10px)}}"
            f"100%{{opacity:0;transform:translateY(-10px)}}}}"), total


def write(name, theme, content):
    (ASSETS / f"{name}-{theme}.svg").write_text(content, encoding="utf-8")
