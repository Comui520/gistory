"""Gistory CLI entry point.

Generates a developer's "Wrapped" report from a local git repository,
displays a rich terminal report, calls an LLM for fun insights,
and exports a beautiful standalone HTML file.
"""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(
    name="gistory",
    help="Generate a beautiful \"Wrapped\" report from your git history.",
    add_completion=False,
)


@app.command()
def main(
    since: str = typer.Option(
        "1 year ago",
        "--since",
        help="Git log date range (e.g. '1 year ago', '6 months ago').",
    ),
    repo: Path = typer.Option(
        Path("."),
        "--repo",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the git repository.",
    ),
    output: Path = typer.Option(
        Path("wrapped.html"),
        "--output",
        help="Output path for the HTML report.",
    ),
    lang: str = typer.Option(
        "en",
        "--lang",
        help="Language for AI report (en or zh).",
    ),
    style: str = typer.Option(
        "fun",
        "--style",
        help="Tone of the AI report (fun, neutral, or roast).",
    ),
) -> None:
    """Generate your Gistory report!"""
    # Validate lang and style
    if lang not in ("en", "zh"):
        typer.echo(f"❌ Invalid language '{lang}'. Use 'en' or 'zh'.", err=True)
        raise typer.Exit(code=1)

    if style not in ("fun", "neutral", "roast"):
        typer.echo(f"❌ Invalid style '{style}'. Use 'fun', 'neutral', or 'roast'.", err=True)
        raise typer.Exit(code=1)

    # Validate repo is a git repository
    try:
        import git
        try:
            _ = git.Repo(repo).head.commit
        except Exception:
            typer.echo(
                f"❌ '{repo}' is not a valid git repository. "
                "Please run this command inside a git repo or use --repo to specify one.",
                err=True,
            )
            raise typer.Exit(code=1)
    except ImportError:
        typer.echo("❌ GitPython is not installed. Run: pip install GitPython", err=True)
        raise typer.Exit(code=1)

    from .git_stats import collect_stats
    from .llm_report import generate
    from .terminal import show
    from .html_report import generate as generate_html

    typer.echo("🔍 Analyzing your git history...")

    try:
        stats = collect_stats(str(repo), since)
    except Exception as e:
        typer.echo(f"❌ Failed to collect git stats: {e}", err=True)
        raise typer.Exit(code=1)

    if stats["total_commits"] == 0:
        typer.echo(
            "⚠️  No commits found in the specified date range. "
            "Try a longer range with --since '2 years ago'.",
        )
        raise typer.Exit(code=0)

    typer.echo(f"   Found {stats['total_commits']:,} commits across {stats['active_days']} days.")

    # Generate AI report
    typer.echo("🤖 Generating AI insights...")
    ai_report = None
    try:
        ai_report = generate(stats, lang, style)
    except Exception:
        typer.echo("   ⚠️  AI insight generation failed. Continuing without AI insights.")

    # Show terminal report
    show(stats, ai_report)

    # Generate HTML reports (primary lang + alternate lang)
    typer.echo("📄 Generating HTML reports...")
    try:
        primary_output = str(output.resolve())
        generate_html(stats, ai_report, primary_output, lang)

        # Generate alternate language version
        out_path = Path(primary_output)
        if lang == "zh":
            alt_lang = "en"
            alt_stem = out_path.stem
            if alt_stem.endswith("_zh"):
                alt_stem = alt_stem[:-3]
            alt_output = str(out_path.with_stem(alt_stem))
        else:
            alt_lang = "zh"
            alt_output = str(out_path.with_stem(out_path.stem + "_zh"))
        generate_html(stats, ai_report, alt_output, alt_lang)

        typer.echo(f"\n✅ Reports saved:")
        typer.echo(f"   [bold]{primary_output}[/bold] ({lang.upper()})")
        typer.echo(f"   [bold]{alt_output}[/bold] ({alt_lang.upper()})")
        typer.echo("📤 Share it with your friends!")
    except Exception as e:
        typer.echo(f"❌ Failed to generate HTML report: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
