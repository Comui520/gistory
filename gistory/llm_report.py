"""LLM report generation module.

Calls OpenAI-compatible API to generate fun insights
based on collected git statistics.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))


def _env(key: str, default: str) -> str:
    """Get env var, reloading .env if not found (supports multi-directory use)."""
    val = os.getenv(key)
    if val:
        return val
    # Try harder: search from cwd upward
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)
        val = os.getenv(key)
        if val:
            return val
    # Try from the repo root where the user's .env likely lives
    for parent in Path.cwd().parents:
        candidate = parent / ".env"
        if candidate.exists():
            load_dotenv(candidate)
            val = os.getenv(key)
            if val:
                return val
    return default

FALLBACK_REPORT: dict[str, Any] = {
    "persona_tags": ["Code Explorer", "Diligent Dev", "Git Guardian"],
    "highlight": "You shipped code consistently throughout the year, making your mark one commit at a time.",
    "comment": "Your terminal never sleeps and neither does your ambition. Keep building!",
}

FALLBACK_REPORT_ZH: dict[str, Any] = {
    "persona_tags": ["代码探险家", "勤奋开发者", "Git守护者"],
    "highlight": "这一年，你持续不断地提交代码，用一次次提交留下了自己的印记。",
    "comment": "你的终端永不眠，你的雄心永不停。继续创造吧！",
}


def generate(stats: dict[str, Any], lang: str, style: str) -> dict[str, Any]:
    """Generate AI-powered insights from git statistics.

    Args:
        stats: Dictionary of collected git statistics.
        lang: Language for the report ("en" or "zh").
        style: Tone of the report ("fun", "neutral", or "roast").

    Returns:
        Dictionary with persona_tags, highlight, and comment.
    """
    api_key = _env("OPENAI_API_KEY", "")
    if not api_key:
        return _get_fallback(lang)

    base_url = _env("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = _env("MODEL", "gpt-4o-mini")

    system_prompt, user_prompt = _build_prompts(stats, lang, style)

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=500,
        )

        content = response.choices[0].message.content or ""
        return _parse_response(content, lang)

    except Exception:
        return _get_fallback(lang)


def _build_prompts(stats: dict[str, Any], lang: str, style: str) -> tuple[str, str]:
    """Build system and user prompts based on language and style."""
    total_commits = stats.get("total_commits", 0)
    insertions = stats.get("insertions", 0)
    deletions = stats.get("deletions", 0)
    active_days = stats.get("active_days", 0)

    top_files = stats.get("files_changed", [])[:5]
    top_files_str = ", ".join(
        f"{f['file']} ({f['changes']})" for f in top_files
    ) or "none"

    top_words = list(stats.get("commit_message_words", {}).keys())[:10]
    top_words_str = ", ".join(top_words) or "none"

    hour_dist = stats.get("hour_distribution", [0] * 24)
    peak_hour = hour_dist.index(max(hour_dist)) if any(hour_dist) else 0

    day_names_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dow_dist = stats.get("day_of_week_distribution", [0] * 7)
    peak_day_idx = dow_dist.index(max(dow_dist)) if any(dow_dist) else 0
    peak_day = day_names_en[peak_day_idx]

    if lang == "zh":
        system_prompt = (
            "你是一位机智且富有洞察力的开发者分析师。你为开发者制作有趣的\"年度总结\"风格报告。"
            "只回复JSON格式。"
        )

        style_map = {
            "fun": "用幽默庆祝的方式",
            "neutral": "用客观中立的语气",
            "roast": "用友好调侃的方式，轻轻开玩笑",
        }
        style_desc = style_map.get(style, style_map["fun"])

        user_prompt = f"""根据以下开发者Git统计数据，生成一份报告。{style_desc}。

统计信息:
- 总提交次数: {total_commits}
- 新增代码行: {insertions}
- 删除代码行: {deletions}
- 活跃天数: {active_days}
- 最活跃的时段: {peak_hour}:00
- 最活跃的星期: {peak_day}
- 改动最多的文件: {top_files_str}
- 提交信息常用词: {top_words_str}

请以JSON格式回复，包含以下字段:
{{
    "persona_tags": ["标签1", "标签2", "标签3"],
    "highlight": "开发者在代码中的具体、难忘的时刻描述。",
    "comment": "反映开发者风格的总括性机智评论。"
}}

只返回JSON，不要其他内容。"""
    else:
        system_prompt = (
            "You are a witty and insightful developer analyst. "
            "You create fun \"Wrapped\" style reports for developers. "
            "Respond only with JSON."
        )

        style_map = {
            "fun": "Celebrate humorously",
            "neutral": "Be straightforward and factual",
            "roast": "Gently tease and roast them in a friendly way",
        }
        style_desc = style_map.get(style, style_map["fun"])

        user_prompt = f"""Based on the following developer's git statistics, generate a report. {style_desc}.

Stats:
- Total commits: {total_commits}
- Lines added: {insertions}
- Lines deleted: {deletions}
- Active days: {active_days}
- Peak coding hour: {peak_hour}:00
- Most active day: {peak_day}
- Most-changed files: {top_files_str}
- Common commit words: {top_words_str}

Respond with JSON containing:
{{
    "persona_tags": ["Tag1", "Tag2", "Tag3"],
    "highlight": "A specific, memorable moment from their year in code.",
    "comment": "A witty overall remark reflecting the developer's style."
}}

Return only JSON, nothing else."""

    return system_prompt, user_prompt


def _parse_response(content: str, lang: str) -> dict[str, Any]:
    """Parse the LLM JSON response, with fallback on error."""
    content = content.strip()
    # Remove markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        data = json.loads(content)
        required = ["persona_tags", "highlight", "comment"]
        for key in required:
            if key not in data:
                data[key] = _get_fallback(lang)[key]
        return data
    except json.JSONDecodeError:
        return _get_fallback(lang)


def _get_fallback(lang: str) -> dict[str, Any]:
    """Return fallback report based on language."""
    return FALLBACK_REPORT_ZH if lang == "zh" else FALLBACK_REPORT
