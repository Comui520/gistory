"""Terminal rendering module.

Uses Rich to display a beautiful, colorful terminal report
of the developer's Gistory statistics.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.style import Style
from rich.box import ROUNDED, HEAVY

console = Console()


def show(stats: dict[str, Any], ai_report: dict[str, Any] | None) -> None:
    """Render the full Gistory terminal report.

    Args:
        stats: Git statistics dictionary.
        ai_report: AI-generated insights dictionary, or None.
    """
    console.print()
    _show_header()
    _show_basic_stats(stats)
    _show_heatmap(stats)
    _show_top_files(stats)
    _show_commit_words(stats)
    _show_ai_insights(ai_report)
    console.print()


def _show_header() -> None:
    """Display the report title."""
    title = Text("✦ Gistory ✦", style="bold cyan")
    header_panel = Panel(
        Align.center(title),
        border_style="bright_cyan",
        box=HEAVY,
        padding=(1, 4),
    )
    console.print(header_panel)
    console.print()


def _show_basic_stats(stats: dict[str, Any]) -> None:
    """Display basic statistics in a table."""
    total = stats.get("total_commits", 0)
    insertions = stats.get("insertions", 0)
    deletions = stats.get("deletions", 0)
    active_days = stats.get("active_days", 0)

    hour_dist = stats.get("hour_distribution", [0] * 24)
    peak_hour = hour_dist.index(max(hour_dist)) if any(hour_dist) else 0

    dow = stats.get("day_of_week_distribution", [0] * 7)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    peak_day = day_names[dow.index(max(dow))] if any(dow) else "N/A"

    table = Table(
        title="📊  Basic Stats",
        box=ROUNDED,
        border_style="bright_blue",
        title_style="bold bright_blue",
    )
    table.add_column("Metric", style="bold", no_wrap=True)
    table.add_column("Value", style="green", justify="right")

    table.add_row("Total Commits", f"{total:,}")
    table.add_row("Lines Added", f"+{insertions:,}")
    table.add_row("Lines Deleted", f"-{deletions:,}")
    table.add_row("Net Lines", f"{insertions - deletions:+,}")
    table.add_row("Active Days", str(active_days))
    table.add_row("Most Active Day", peak_day)
    table.add_row("Peak Coding Hour", f"{peak_hour:02d}:00")

    console.print(Align.center(table))
    console.print()


def _show_heatmap(stats: dict[str, Any]) -> None:
    """Display a commit heatmap with colored squares."""
    heatmap = stats.get("commit_heatmap", [])
    if not heatmap:
        return

    # Build a map of date -> count
    date_counts: dict[str, int] = {
        entry["date"]: entry["count"] for entry in heatmap
    }

    from datetime import datetime, timedelta

    dates = sorted(date_counts.keys())
    if not dates:
        return

    start = datetime.strptime(dates[0], "%Y-%m-%d")
    end = datetime.strptime(dates[-1], "%Y-%m-%d")

    # Adjust start to previous Monday
    start_monday = start - timedelta(days=start.weekday())

    console.print()
    heading = Text("🔥  Commit Heatmap", style="bold bright_yellow")
    console.print(Align.center(heading))
    console.print()

    # Intensity levels and colors
    intensity_colors = [
        Style(color="bright_black"),     # 0: no commits
        Style(color="green"),             # 1: light
        Style(color="bright_green"),      # 2: medium
        Style(color="yellow"),            # 3: heavy
        Style(color="bright_red"),        # 4: very heavy
    ]

    max_count = max(date_counts.values()) if date_counts else 1

    def intensity(count: int) -> int:
        if count == 0:
            return 0
        ratio = count / max(max_count, 1)
        if ratio <= 0.25:
            return 1
        elif ratio <= 0.5:
            return 2
        elif ratio <= 0.75:
            return 3
        else:
            return 4

    # Day headers
    day_labels = ["  ", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    header_line = " ".join(day_labels)
    console.print(f"    {header_line}", style="dim")

    current = start_monday
    week_str = ""
    week_count = 0

    while current <= end:
        day_of_week = current.weekday()
        date_key = current.strftime("%Y-%m-%d")
        count = date_counts.get(date_key, 0)
        lvl = intensity(count)
        style = intensity_colors[lvl]
        block = "██" if count > 0 else "░░"

        if day_of_week == 0:
            if week_str:
                console.print(week_str)
            week_str = f"[dim]{current.strftime('%b')}[/dim]".rjust(5) + " "

        week_str += f"[{style}]{block}[/{style}] "
        current += timedelta(days=1)
        week_count += 1

    if week_str.strip():
        console.print(week_str)

    # Legend
    console.print()
    q25 = max(1, int(max_count * 0.25))
    q50 = max(q25 + 1, int(max_count * 0.5))
    q75 = max(q50 + 1, int(max_count * 0.75))
    legend_parts = [
        f"[bright_black]░░[/bright_black] 0",
        f"[green]██[/green] 1-{q25}",
        f"[bright_green]██[/bright_green] {q25 + 1}-{q50}",
        f"[yellow]██[/yellow] {q50 + 1}-{q75}",
        f"[bright_red]██[/bright_red] {q75 + 1}+",
    ]
    console.print("     " + "  ".join(legend_parts))
    console.print()


def _show_top_files(stats: dict[str, Any]) -> None:
    """Display top changed files as a bar chart."""
    files = stats.get("files_changed", [])
    if not files:
        return

    console.print()
    heading = Text("📁  Top Changed Files", style="bold bright_magenta")
    console.print(Align.center(heading))
    console.print()

    max_changes = files[0]["changes"] if files else 1
    bar_width = 30

    for entry in files[:10]:
        fname = entry["file"]
        changes = entry["changes"]
        ratio = changes / max(max_changes, 1)
        filled = int(ratio * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        # Truncate long filenames
        if len(fname) > 40:
            fname = "..." + fname[-37:]

        console.print(
            f"  [bold]{fname:<41}[/bold] "
            f"[bright_cyan]{bar}[/bright_cyan] "
            f"[green]{changes}[/green]"
        )

    console.print()


def _show_commit_words(stats: dict[str, Any]) -> None:
    """Display common commit message words as badges."""
    words = stats.get("commit_message_words", {})
    if not words:
        return

    console.print()
    heading = Text("💬  Top Commit Message Words", style="bold bright_yellow")
    console.print(Align.center(heading))
    console.print()

    top_words = list(words.items())[:15]
    badges = []
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "bright_red",
              "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan"]
    for i, (word, count) in enumerate(top_words):
        color = colors[i % len(colors)]
        badge = f"[bold {color}]{word}[/bold {color}] [dim]({count})[/dim]"
        badges.append(badge)

    console.print("  " + "  ".join(badges))
    console.print()


def _show_ai_insights(ai_report: dict[str, Any] | None) -> None:
    """Display AI-generated insights."""
    console.print()

    if ai_report is None:
        no_ai = Panel(
            "[dim italic]Could not generate AI insights. Set OPENAI_API_KEY for personalized insights.[/dim italic]",
            border_style="dim red",
            box=ROUNDED,
        )
        console.print(Align.center(no_ai))
        return

    tags = ai_report.get("persona_tags", [])
    highlight = ai_report.get("highlight", "")
    comment = ai_report.get("comment", "")

    if tags:
        badge_colors = ["bright_red", "bright_green", "bright_yellow",
                        "bright_blue", "bright_magenta", "bright_cyan"]
        tag_badges = []
        for i, tag in enumerate(tags):
            color = badge_colors[i % len(badge_colors)]
            tag_badges.append(f"[bold white on {color}] {tag} [/bold white on {color}]")
        console.print(Align.center(Text("🏷️  Persona Tags", style="bold")))
        console.print()
        console.print(Align.center(Text("  ".join(tag_badges))))
        console.print()

    if highlight:
        highlight_panel = Panel(
            f"[italic]{highlight}[/italic]",
            title="💡 Highlight",
            border_style="bright_cyan",
            box=ROUNDED,
            title_align="left",
        )
        console.print(highlight_panel)

    if comment:
        comment_panel = Panel(
            f"[bold]{comment}[/bold]",
            title="🎤 Final Word",
            border_style="bright_magenta",
            box=ROUNDED,
            title_align="left",
        )
        console.print(comment_panel)
