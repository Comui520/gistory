"""Git statistics collection module.

Uses GitPython with a subprocess fallback to gather commit statistics
from a local git repository within a specified date range.
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STOP_WORDS: set[str] = {
    "the", "and", "for", "that", "this", "with", "from", "have", "are",
    "was", "not", "but", "you", "all", "can", "had", "has", "been",
    "one", "our", "out", "its", "get", "use", "will", "just", "like",
    "some", "than", "then", "also", "into", "more", "when", "make",
    "they", "what", "which", "their", "them", "about", "would", "other",
    "after", "over", "only", "your", "very", "most", "should", "could",
    "does", "each", "every", "where", "there", "here", "being", "such",
    "doing", "done", "even", "still", "much", "well", "way", "how",
    "too", "now", "new", "see", "may", "need", "really", "these",
    "those", "many", "same", "before", "between", "during", "through",
    "because", "while", "without", "another", "within", "using", "used",
    "work", "working", "change", "changes", "changed", "changing",
    "add", "added", "adding", "update", "updated", "updating",
    "fix", "fixed", "fixes", "fixing", "remove", "removed", "removing",
    "implement", "implemented", "implementing", "refactor", "refactored",
    "merge", "merged", "merging", "branch", "commit", "file", "files",
    "code", "test", "tests", "testing", "wip", "todo", "typo",
}


def collect_stats(repo_path: str, since: str) -> dict[str, Any]:
    """Collect git statistics from a repository.

    Args:
        repo_path: Path to the git repository.
        since: Date string for --since parameter (e.g. "1 year ago").

    Returns:
        A dictionary containing all collected statistics.
    """
    repo_path_obj = Path(repo_path).resolve()

    try:
        import git
        repo = git.Repo(repo_path_obj)
        _ = repo.head.commit  # verify it's valid
        return _collect_with_gitpython(repo, since)
    except Exception:
        return _collect_with_subprocess(repo_path_obj, since)


def _collect_with_gitpython(repo: Any, since: str) -> dict[str, Any]:
    """Collect stats using GitPython (preferred method)."""
    commits = list(repo.iter_commits(since=since))
    if not commits:
        return _empty_stats()

    total_commits = len(commits)

    # File changes
    file_counter: Counter[str] = Counter()
    for commit in commits:
        try:
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
            else:
                diffs = commit.diff(None)
            for diff in diffs:
                if diff.a_path:
                    file_counter[diff.a_path] += 1
        except Exception:
            pass

    top_files = [{"file": f, "changes": c} for f, c in file_counter.most_common(10)]

    # Insertions/deletions via subprocess shortstat (most reliable)
    insertions = 0
    deletions = 0
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--shortstat", "--format="],
            capture_output=True, text=True, cwd=str(repo.working_dir), timeout=60,
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                m = re.search(
                    r"(\d+)\s+files?\s+changed(?:,\s+(\d+)\s+insertions?\(\+\))?(?:,\s+(\d+)\s+deletions?\(-\))?",
                    line,
                )
                if m:
                    if m.group(2):
                        insertions += int(m.group(2))
                    if m.group(3):
                        deletions += int(m.group(3))
    except Exception:
        pass

    # Hour distribution
    hour_dist: list[int] = [0] * 24
    day_of_week_dist: list[int] = [0] * 7
    heatmap_data: Counter[str] = Counter()
    word_counter: Counter[str] = Counter()

    first_commit_date = None
    last_commit_date = None

    for commit in commits:
        dt = commit.committed_datetime
        if isinstance(dt, datetime):
            hour_dist[dt.hour] += 1
            day_of_week_dist[dt.weekday()] += 1
            date_key = dt.strftime("%Y-%m-%d")
            heatmap_data[date_key] += 1

            if first_commit_date is None or dt < first_commit_date:
                first_commit_date = dt
            if last_commit_date is None or dt > last_commit_date:
                last_commit_date = dt

        msg = commit.message or ""
        words = re.findall(r"\b[a-zA-Z]{3,}\b", msg.lower())
        for word in words:
            if word not in STOP_WORDS:
                word_counter[word] += 1

    commit_heatmap = [
        {"date": d, "count": c}
        for d, c in sorted(heatmap_data.items())
    ]

    active_days = len(heatmap_data)

    top_words = dict(word_counter.most_common(30))

    return {
        "total_commits": total_commits,
        "files_changed": top_files,
        "insertions": insertions,
        "deletions": deletions,
        "hour_distribution": hour_dist,
        "day_of_week_distribution": day_of_week_dist,
        "commit_heatmap": commit_heatmap,
        "commit_message_words": top_words,
        "first_commit_date": first_commit_date.isoformat() if first_commit_date else "",
        "last_commit_date": last_commit_date.isoformat() if last_commit_date else "",
        "active_days": active_days,
    }


def _collect_with_subprocess(repo_path: Path, since: str) -> dict[str, Any]:
    """Fallback: collect stats using subprocess calling git commands."""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--format=%H"],
            capture_output=True, text=True, cwd=str(repo_path),
            timeout=60,
        )
        if result.returncode != 0:
            return _empty_stats()
        commit_hashes = [h for h in result.stdout.strip().split("\n") if h]
    except Exception:
        return _empty_stats()

    if not commit_hashes:
        return _empty_stats()

    total_commits = len(commit_hashes)

    # Shortstat for insertions/deletions
    insertions = 0
    deletions = 0
    file_counter: Counter[str] = Counter()
    try:
        shortstat = subprocess.run(
            ["git", "log", f"--since={since}", "--shortstat", "--format=%H"],
            capture_output=True, text=True, cwd=str(repo_path),
            timeout=60,
        )
        if shortstat.returncode == 0:
            lines = shortstat.stdout.split("\n")
            for line in lines:
                m = re.search(
                    r"(\d+)\s+files?\s+changed.*?(\d+)\s+insertion.*?(\d+)\s+deletion",
                    line,
                )
                if m:
                    insertions += int(m.group(2))
                    deletions += int(m.group(3))
    except Exception:
        pass

    # File changes via --name-only
    try:
        nameonly = subprocess.run(
            ["git", "log", f"--since={since}", "--name-only", "--format="],
            capture_output=True, text=True, cwd=str(repo_path),
            timeout=60,
        )
        if nameonly.returncode == 0:
            for line in nameonly.stdout.strip().split("\n"):
                line = line.strip()
                if line:
                    file_counter[line] += 1
    except Exception:
        pass

    top_files = [{"file": f, "changes": c} for f, c in file_counter.most_common(10)]

    # Date/time distributions
    hour_dist: list[int] = [0] * 24
    day_of_week_dist: list[int] = [0] * 7
    heatmap_data: Counter[str] = Counter()
    word_counter: Counter[str] = Counter()
    first_dt = None
    last_dt = None

    try:
        log_data = subprocess.run(
            ["git", "log", f"--since={since}", "--format=%H%n%aI%n%s"],
            capture_output=True, text=True, cwd=str(repo_path),
            timeout=60,
        )
        if log_data.returncode == 0:
            parts = log_data.stdout.strip().split("\n")
            i = 0
            while i + 2 < len(parts):
                # hash: parts[i], date: parts[i+1], subject: parts[i+2]
                date_str = parts[i + 1]
                subject = parts[i + 2]
                try:
                    dt = datetime.fromisoformat(date_str)
                except Exception:
                    dt = None
                if dt:
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    hour_dist[dt.hour] += 1
                    day_of_week_dist[dt.weekday()] += 1
                    date_key = dt.strftime("%Y-%m-%d")
                    heatmap_data[date_key] += 1
                    if first_dt is None or dt < first_dt:
                        first_dt = dt
                    if last_dt is None or dt > last_dt:
                        last_dt = dt

                words = re.findall(r"\b[a-zA-Z]{3,}\b", subject.lower())
                for word in words:
                    if word not in STOP_WORDS:
                        word_counter[word] += 1

                i += 3
    except Exception:
        pass

    commit_heatmap = [
        {"date": d, "count": c}
        for d, c in sorted(heatmap_data.items())
    ]
    active_days = len(commit_heatmap)
    top_words = dict(word_counter.most_common(30))

    return {
        "total_commits": total_commits,
        "files_changed": top_files,
        "insertions": insertions,
        "deletions": deletions,
        "hour_distribution": hour_dist,
        "day_of_week_distribution": day_of_week_dist,
        "commit_heatmap": commit_heatmap,
        "commit_message_words": top_words,
        "first_commit_date": first_dt.isoformat() if first_dt else "",
        "last_commit_date": last_dt.isoformat() if last_dt else "",
        "active_days": active_days,
    }


def _empty_stats() -> dict[str, Any]:
    """Return empty stats when no data is available."""
    return {
        "total_commits": 0,
        "files_changed": [],
        "insertions": 0,
        "deletions": 0,
        "hour_distribution": [0] * 24,
        "day_of_week_distribution": [0] * 7,
        "commit_heatmap": [],
        "commit_message_words": {},
        "first_commit_date": "",
        "last_commit_date": "",
        "active_days": 0,
    }
