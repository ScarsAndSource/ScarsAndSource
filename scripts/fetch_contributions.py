"""
fetch_contributions.py — pulls the public contribution calendar HTML fragment
(no PAT / GraphQL token needed) and writes data/contributions.json.

    python scripts/fetch_contributions.py

Source: https://github.com/users/<username>/contributions
This is the same fragment GitHub's own profile page renders client-side.
"""
import json
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "ScarsAndSource"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).parent.parent / "data" / "contributions.json"


def fetch_days() -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as a <td> with data-date / data-level, or an
    # <li>/<rect> depending on markup version — this covers both shapes.
    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")
    for cell in cells:
        d = cell.get("data-date")
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
        if d is None or level is None:
            continue
        days.append({
            "date": d,
            "level": int(level),
            "count": int(count_attr) if count_attr is not None else None,
        })
    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] or 0 for d in days if d["count"] is not None)
    # fall back to counting non-zero levels if data-count wasn't present
    if total == 0:
        total = sum(1 for d in days if d["level"] > 0)

    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: (d["count"] or d["level"]), default=None)

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day["date"] if best_day else None,
        "generated_at": date.today().isoformat(),
    }


def main():
    days = fetch_days()
    if not days:
        print("warning: no contribution cells parsed — GitHub markup may have "
              "changed, check the CSS selectors in fetch_days()")
    stats = compute_stats(days)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"days": days, "stats": stats}, indent=2), encoding="utf-8")
    print(f"done -> {OUT} ({len(days)} days, {stats['total_last_year']} contributions)")


if __name__ == "__main__":
    main()
