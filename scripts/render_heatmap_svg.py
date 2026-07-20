"""
render_heatmap_svg.py — reads data/contributions.json and draws contrib-heatmap.svg
(53-week x 7-day grid, GitHub-ish green ramp, diagonal slide-down reveal that
plays once on load then freezes — no looping glow).

    python scripts/render_heatmap_svg.py
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "contributions.json"
OUT = Path(__file__).parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 12
GAP = 3
LEGEND_H = 24
FOOTER_H = 22
LABEL_W = 28   # room for weekday labels

STAGGER = 0.006   # per-cell delay, diagonal via (week + day) index
DUR = 0.4


def load():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    return payload["days"], payload["stats"]


def bucket_by_week(days: list[dict]) -> list[list[dict | None]]:
    """Return weeks[week_index][weekday(0=Sun..6=Sat)] -> day dict or None."""
    by_date = {d["date"]: d for d in days}
    if not days:
        return []
    all_dates = sorted(by_date.keys())
    start = datetime.fromisoformat(all_dates[0])
    end = datetime.fromisoformat(all_dates[-1])

    # align start back to the preceding Sunday
    start_sunday = start
    while start_sunday.weekday() != 6:  # Python Mon=0..Sun=6; GitHub week starts Sun
        start_sunday = start_sunday.fromordinal(start_sunday.toordinal() - 1)

    weeks: list[list[dict | None]] = []
    cur = start_sunday
    week: list[dict | None] = [None] * 7
    idx_in_week = 0
    while cur <= end:
        key = cur.date().isoformat()
        weekday = (cur.weekday() + 1) % 7  # convert to Sun=0..Sat=6
        week[weekday] = by_date.get(key)
        if weekday == 6:
            weeks.append(week)
            week = [None] * 7
        cur = cur.fromordinal(cur.toordinal() + 1)
    if any(c is not None for c in week):
        weeks.append(week)
    return weeks


def build_svg(weeks: list[list[dict | None]], stats: dict) -> str:
    n_weeks = len(weeks)
    grid_w = n_weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    width = LABEL_W + grid_w + 10
    height = LEGEND_H + grid_h + FOOTER_H + 10

    cells = []
    for w, week in enumerate(weeks):
        for d, day in enumerate(week):
            level = day["level"] if day else 0
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = LABEL_W + w * (CELL + GAP)
            y = LEGEND_H + d * (CELL + GAP)
            delay = (w + d) * STAGGER
            cells.append(f"""
    <rect x="{x}" y="{y - 6}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"
          opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s"
               dur="{DUR}s" fill="freeze"/>
      <animate attributeName="y" from="{y - 6}" to="{y}" begin="{delay:.3f}s"
               dur="{DUR}s" fill="freeze" calcMode="ease-out"/>
    </rect>""")

    legend_x0 = LABEL_W
    legend_swatches = []
    for i, color in enumerate(PALETTE):
        lx = width - 10 - (len(PALETTE) - i) * (CELL + 2)
        legend_swatches.append(
            f'<rect x="{lx}" y="{height - FOOTER_H + 2}" width="{CELL - 2}" '
            f'height="{CELL - 2}" rx="2" fill="{color}"/>'
        )

    footer_text = f"{stats.get('total_last_year', 0)} contributions in the last year " \
                   f"· streak {stats.get('current_streak', 0)}d (longest {stats.get('longest_streak', 0)}d)"

    svg = f"""<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="transparent"/>
  {''.join(cells)}
  <text x="{legend_x0}" y="{height - FOOTER_H + 12}" font-family="JetBrains Mono, monospace"
        font-size="11" fill="#8b949e">Less</text>
  {''.join(legend_swatches)}
  <text x="{width - 8}" y="{height - FOOTER_H + 12}" font-family="JetBrains Mono, monospace"
        font-size="11" fill="#8b949e" text-anchor="end">More</text>
  <text x="{LABEL_W}" y="{height - 4}" font-family="JetBrains Mono, monospace"
        font-size="12" fill="#c9d1d9">{footer_text}</text>
</svg>"""
    return svg


def main():
    if not DATA.exists():
        print(f"missing {DATA} — run fetch_contributions.py first")
        return
    days, stats = load()
    weeks = bucket_by_week(days)
    svg = build_svg(weeks, stats)
    OUT.write_text(svg, encoding="utf-8")
    print(f"done -> {OUT} ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
