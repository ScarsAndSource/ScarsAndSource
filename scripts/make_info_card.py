"""
make_info_card.py — hand-authors info-card.svg, a neofetch-style panel.

    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame for Quick Look / debugging

Edit LINES below — this is the slot for the story your commit graph can't tell.
Keep it monochrome-adjacent: one accent color, rest is grayscale, matching
the ASCII portrait's restraint instead of a busy multi-color panel.
"""
import os
from pathlib import Path

OUT = Path(__file__).parent.parent / "info-card.svg"

ACCENT = "#39d353"      # single accent, echoes the heatmap's brightest green
LABEL_COLOR = "#6e7681"
VALUE_COLOR = "#c9d1d9"
BG = "transparent"
FONT_FAMILY = "JetBrains Mono, ui-monospace, Menlo, monospace"

TITLE = "avi@github"

# (label, value) rows — edit freely
LINES = [
    ("os", "Manipal University Jaipur, CS Eng '28"),
    ("shell", "VB Industries — AI automation, freelance"),
    ("stack", "TypeScript · Python · FastAPI · Supabase"),
    ("now", "Shipping hackathon projects + open source"),
    ("contrib", "Active on GSSoC"),
    ("motto", "i win."),
]

LINE_HEIGHT = 26
PAD_X = 20
PAD_TOP = 46
CARD_W = 490
CARD_H = PAD_TOP + LINE_HEIGHT * (len(LINES) + 1) + 18

STAGGER = 0.12
DUR = 0.35


def build_svg(static: bool) -> str:
    rows = []
    for i, (label, value) in enumerate(LINES):
        y = PAD_TOP + i * LINE_HEIGHT
        delay = 0.15 + i * STAGGER
        if static:
            opacity_attr = 'opacity="1"'
            transform = ""
        else:
            opacity_attr = 'opacity="0"'
            transform = f"""
        <animate attributeName="opacity" from="0" to="1"
                 begin="{delay:.2f}s" dur="{DUR}s" fill="freeze"/>
        <animateTransform attributeName="transform" type="translate"
                 from="-8 0" to="0 0" begin="{delay:.2f}s" dur="{DUR}s"
                 fill="freeze" calcMode="ease-out"/>"""
        rows.append(f"""
    <g {opacity_attr}>{transform}
      <text x="{PAD_X}" y="{y}" font-family="{FONT_FAMILY}" font-size="14"
            fill="{ACCENT}">{label}</text>
      <text x="{PAD_X + 90}" y="{y}" font-family="{FONT_FAMILY}" font-size="14"
            fill="{VALUE_COLOR}">{value}</text>
    </g>""")

    header_opacity = '1' if static else '0'
    header_anim = "" if static else f"""
      <animate attributeName="opacity" from="0" to="1" begin="0s" dur="0.3s" fill="freeze"/>"""

    svg = f"""<svg viewBox="0 0 {CARD_W} {CARD_H}" xmlns="http://www.w3.org/2000/svg"
     width="{CARD_W}" height="{CARD_H}">
  <rect width="100%" height="100%" fill="{BG}"/>
  <g opacity="{header_opacity}">{header_anim}
    <circle cx="16" cy="18" r="5" fill="#ff5f56"/>
    <circle cx="34" cy="18" r="5" fill="#ffbd2e"/>
    <circle cx="52" cy="18" r="5" fill="#27c93f"/>
    <text x="{CARD_W - PAD_X}" y="23" font-family="{FONT_FAMILY}" font-size="13"
          fill="{LABEL_COLOR}" text-anchor="end">{TITLE}</text>
  </g>
  <line x1="0" y1="34" x2="{CARD_W}" y2="34" stroke="#30363d" stroke-width="1"/>
  {''.join(rows)}
</svg>"""
    return svg


def main():
    static = os.environ.get("STATIC") == "1"
    svg = build_svg(static)
    OUT.write_text(svg, encoding="utf-8")
    print(f"done ({'static' if static else 'animated'}) -> {OUT}")


if __name__ == "__main__":
    main()
