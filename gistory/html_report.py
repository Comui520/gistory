"""HTML report generation module.

Uses Jinja2 templating to render a beautiful standalone HTML
report from collected git statistics and AI insights.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


def generate(
    stats: dict[str, Any],
    ai_report: dict[str, Any] | None,
    output_path: str,
    lang: str = "en",
) -> None:
    """Generate a standalone HTML report and write it to disk.

    Args:
        stats: Git statistics dictionary.
        ai_report: AI-generated insights dictionary, or None.
        output_path: File path to write the HTML report.
        lang: Language code ("en" or "zh").
    """
    template_dir = Path(__file__).resolve().parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )
    template = env.get_template("wrapped.html")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build other-language URL
    out = Path(output_path)
    if lang == "zh":
        other_lang_url = out.stem.rstrip("_zh") + ".html" if out.stem.endswith("_zh") else "wrapped.html"
    else:
        stem = out.stem
        ext = out.suffix
        other_lang_url = f"{stem}_zh{ext}"

    # Prepare day names
    dow = stats.get("day_of_week_distribution", [0] * 7)
    day_names_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_names_zh = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

    # Find peak day and hour
    peak_day_idx = dow.index(max(dow)) if any(dow) else 0
    peak_day_en = day_names_en[peak_day_idx]
    peak_day_zh = day_names_zh[peak_day_idx]
    hour_dist = stats.get("hour_distribution", [0] * 24)
    peak_hour = hour_dist.index(max(hour_dist)) if any(hour_dist) else 0

    # Build heatmap matrix
    heatmap = stats.get("commit_heatmap", [])
    date_counts: dict[str, int] = {}
    if heatmap:
        date_counts = {entry["date"]: entry["count"] for entry in heatmap}
    max_count = max(date_counts.values()) if date_counts else 1

    heatmap_weeks: list[list[dict[str, Any]]] = []
    if heatmap:
        from datetime import timedelta
        dates_sorted = sorted(date_counts.keys())
        start = datetime.strptime(dates_sorted[0], "%Y-%m-%d")
        end = datetime.strptime(dates_sorted[-1], "%Y-%m-%d")
        start_monday = start - timedelta(days=start.weekday())

        current = start_monday
        while current <= end:
            week: list[dict[str, Any]] = []
            for _ in range(7):
                date_key = current.strftime("%Y-%m-%d")
                count = date_counts.get(date_key, 0)
                ratio = count / max(max_count, 1) if count > 0 else 0
                level = 0
                if ratio > 0:
                    if ratio <= 0.25:
                        level = 1
                    elif ratio <= 0.5:
                        level = 2
                    elif ratio <= 0.75:
                        level = 3
                    else:
                        level = 4
                week.append({
                    "date": date_key,
                    "count": count,
                    "level": level,
                })
                current += timedelta(days=1)
            heatmap_weeks.append(week)

    # Top words
    top_words = list(stats.get("commit_message_words", {}).items())[:15]

    # Top files
    top_files = stats.get("files_changed", [])[:10]
    max_changes = top_files[0]["changes"] if top_files else 1

    # Date formatting
    first_date = stats.get("first_commit_date", "")
    last_date = stats.get("last_commit_date", "")
    if first_date:
        try:
            dt = datetime.fromisoformat(first_date)
            first_date = dt.strftime("%B %d, %Y")
        except Exception:
            pass
    if last_date:
        try:
            dt = datetime.fromisoformat(last_date)
            last_date = dt.strftime("%B %d, %Y")
        except Exception:
            pass

    ctx = {
        "lang": lang,
        "generated_at": generated_at,
        "other_lang_url": other_lang_url,
        "stats": stats,
        "ai_report": ai_report,
        "top_words": top_words,
        "top_files": top_files,
        "max_changes": max_changes,
        "peak_day_en": peak_day_en,
        "peak_day_zh": peak_day_zh,
        "peak_hour": peak_hour,
        "heatmap_weeks": heatmap_weeks,
        "max_heatmap_count": max_count,
        "first_date": first_date,
        "last_date": last_date,
        "total_commits": stats.get("total_commits", 0),
        "insertions": stats.get("insertions", 0),
        "deletions": stats.get("deletions", 0),
        "active_days": stats.get("active_days", 0),
    }

    html = template.render(**ctx)
    output = Path(output_path)
    output.write_text(html, encoding="utf-8")
