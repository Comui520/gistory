# ✦ GitWrapped

从你的 Git 历史中生成一份精美的"年度总结"报告 — 支持终端渲染和独立 HTML 文件。

[English](README.md)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-purple.svg)](https://pypi.org)

## 功能特性

- **终端美化报告** — 热力图、柱状图、统计数据，丰富的彩色输出
- **AI 智能洞察** — 通过 OpenAI 生成开发者标签、高光时刻和风趣评语
- **独立 HTML 导出** — 响应式、支持深色/浅色模式、移动端优先、适配社交分享
- **多语言支持** — AI 报告支持英文和中文
- **多种风格** — 幽默、中立或调侃风格
- **零配置降级** — 无需 API Key 也能运行（仅跳过 AI 分析）

## 安装

```bash
# 克隆后本地安装
git clone https://github.com/gitwrapped/gitwrapped.git
cd gitwrapped
pip install -e .
```

通过 PyPI 安装（即将上线）：

```bash
pip install gitwrapped
```

## 配置

设置你的 OpenAI API Key（可选 — 仅 AI 分析需要）：

```bash
# 复制 .env.example 为 .env
cp .env.example .env

# 编辑 .env，填入你的 Key
OPENAI_API_KEY=sk-你的密钥
```

也可以直接导出环境变量：

```bash
export OPENAI_API_KEY="sk-..."
```

## 使用方式

```bash
# 基本用法（分析当前目录，最近一年）
gitwrapped

# 自定义时间范围
gitwrapped --since "6 months ago"

# 指定仓库路径
gitwrapped --repo /path/to/repo

# 自定义输出路径
gitwrapped --output my-wrapped.html

# 切换语言和风格
gitwrapped --lang zh --style roast

# 完整示例
gitwrapped --since "1 year ago" --repo . --output wrapped.html --lang zh --style fun
```

## 示例输出

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

## 环境要求

- Python 3.10+
- 系统已安装 Git
- OpenAI API Key（可选，用于 AI 分析）

## 参与贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源许可

MIT © 2025 GitWrapped Contributors
