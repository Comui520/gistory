# ✦ GitWrapped

Generate a beautiful "Wrapped" report from your git history — rich terminal UI and standalone HTML.

[中文文档](README-zh.md)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-purple.svg)](https://pypi.org)

## Features

- **Rich Terminal Report** — Beautiful colored output with heatmaps, bar charts, and stats
- **AI-Powered Insights** — Persona tags, highlights, and witty commentary via OpenAI
- **Standalone HTML Export** — Responsive, dark/light mode, mobile-first, social-ready
- **Multilingual** — English and Chinese AI report support
- **Multiple Tones** — Fun, neutral, or roast-style commentary
- **Zero Config Fallback** — Works without an API key (just skips AI insights)

## Installation

```bash
# Clone and install
git clone https://github.com/gitwrapped/gitwrapped.git
cd gitwrapped
pip install -e .
```

Or from PyPI (coming soon):

```bash
pip install gitwrapped
```

## Configuration

Set your OpenAI API key (optional — only needed for AI insights):

```bash
# Create .env from example
cp .env.example .env

# Edit .env and add your key
OPENAI_API_KEY=sk-your-actual-key
```

Or export environment variables directly:

```bash
export OPENAI_API_KEY="sk-..."
```

## Usage

```bash
# Basic usage (uses current directory, last 1 year)
gitwrapped

# Custom date range
gitwrapped --since "6 months ago"

# Specify a repo
gitwrapped --repo /path/to/repo

# Output to custom path
gitwrapped --output my-wrapped.html

# Change language and style
gitwrapped --lang zh --style roast

# Full example
gitwrapped --since "1 year ago" --repo . --output wrapped.html --lang en --style fun
```

## Example Output

```
✦ Your GitWrapped Report ✦

┌─────────────────────────────────────┐
│  📊  Basic Stats                    │
│  Total Commits  │        1,247      │
│  Lines Added    │      +45,392      │
│  Lines Deleted  │      -18,201      │
│  Active Days    │          217      │
│  Most Active Day│    Wednesday      │
│  Peak Hour      │        14:00      │
└─────────────────────────────────────┘

🔥  Commit Heatmap
     Mo Tu We Th Fr Sa Su
Jan  ██ ██ ░░ ██ ██ ░░ ░░
...

🏷️  Persona Tags
[ Night Coder ] [ Bug Squasher ] [ Refactor King ]

💡 Highlight
"The week you shipped v2.0 — 147 commits, 3,000 lines, and only one regretful force-push."
```

## Requirements

- Python 3.10+
- Git installed on your system
- OpenAI API key (optional, for AI insights)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT © 2025 GitWrapped Contributors
