"""
make_ascii_svg.py — converts scripts/prepped/source-prepped.png into avi-ascii.svg
(a self-typing, monochrome ASCII portrait).

    python scripts/make_ascii_svg.py

Design choices (deliberate, matching a dark/monochrome/premium aesthetic):
  - ONE fill color (light gray on transparent). No per-character rainbow.
  - High contrast ramp so background washes to blank, only the subject prints.
  - Each row wipes left-to-right via a clipPath animation, staggered top->bottom.
  - Prints once and freezes (fill="freeze") — no looping.
"""
from pathlib import Path

from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
GRID_W = 100
GRID_H = 53
CHAR_W = 6.2   # px per character cell (monospace advance)
CHAR_H = 11
FONT_FAMILY = "JetBrains Mono, ui-monospace, Menlo, monospace"
FILL_COLOR = "#c9d1d9"
ROW_STAGGER = 0.045   # seconds between each row starting its wipe
WIPE_DURATION = 0.32  # seconds for a single row's left-to-right wipe

SRC = Path(__file__).parent / "prepped" / "source-prepped.png"
OUT = Path(__file__).parent.parent / "avi-ascii.svg"


def image_to_ascii_grid(img: Image.Image) -> list[str]:
    img = img.convert("L").resize((GRID_W, GRID_H))
    pixels = list(img.getdata())
    ramp_len = len(RAMP) - 1
    rows = []
    for y in range(GRID_H):
        row_chars = []
        for x in range(GRID_W):
            brightness = pixels[y * GRID_W + x]  # 0=black .. 255=white
            idx = round((1 - brightness / 255) * ramp_len)
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    return rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    width = GRID_W * CHAR_W
    height = GRID_H * CHAR_H

    defs = []
    row_groups = []

    for i, row in enumerate(rows):
        clip_id = f"wipe{i}"
        start = i * ROW_STAGGER
        end = start + WIPE_DURATION
        # clip rect animates its width from 0 -> full row width
        defs.append(f"""
    <clipPath id="{clip_id}">
      <rect x="0" y="{i * CHAR_H}" width="0" height="{CHAR_H + 2}">
        <animate attributeName="width" from="0" to="{width}"
                 begin="{start:.3f}s" dur="{WIPE_DURATION:.3f}s"
                 fill="freeze" calcMode="linear"/>
      </rect>
    </clipPath>""")

        safe_row = escape_xml(row)
        row_groups.append(f"""
    <g clip-path="url(#{clip_id})">
      <text x="0" y="{(i + 1) * CHAR_H - 2}" font-family="{FONT_FAMILY}"
            font-size="{CHAR_H - 1}" xml:space="preserve"
            fill="{FILL_COLOR}">{safe_row}</text>
    </g>""")

    svg = f"""<svg viewBox="0 0 {width:.1f} {height:.1f}" xmlns="http://www.w3.org/2000/svg"
     width="{width:.0f}" height="{height:.0f}">
  <defs>{''.join(defs)}
  </defs>
  <rect width="100%" height="100%" fill="transparent"/>
  {''.join(row_groups)}
</svg>"""
    return svg


def main():
    if not SRC.exists():
        print(f"missing {SRC} — run prep_photo.py first")
        return
    img = Image.open(SRC)
    rows = image_to_ascii_grid(img)
    svg = build_svg(rows)
    OUT.write_text(svg, encoding="utf-8")
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
