---
name: feishu-tiktok-video-analysis
description: Run or customize an open-source Feishu/Lark multidimensional-table workflow that downloads TikTok links, analyzes videos with Gemini, and writes structured results back.
---

# Feishu TikTok Video Analysis

Use this skill when the user wants to run, install, customize, or fork the TikTok video-analysis workflow for their own Feishu/Lark Base.

This is a template skill. It must not assume any private Base, table, account, cookie, API key, local path, or company credential. Before mutating a live table, confirm the target configuration comes from the user's own environment variables, `.env`, or explicit command arguments.

## Setup

The workflow needs:

- Python 3.10+
- `yt-dlp`
- `lark-cli`
- `GEMINI_API_KEY`
- Optional `meowload` as a fallback downloader

Configuration is externalized through environment variables or a local `.env` file copied from `.env.example`:

- `FEISHU_BASE_TOKEN`
- `FEISHU_TABLE_ID`
- `GEMINI_API_KEY`
- optional `LARK_CLI`
- optional `MEOWLOAD_BIN`

Never display, commit, or paste real secrets in responses, logs, examples, or documentation.

## Main Scripts

- `scripts/setup_table.py`: creates a new table from `references/table_schema.json` in the user's own Base.
- `scripts/process_videos.py`: scans rows whose `任务状态` is `待处理`, downloads TikTok videos, sends video/subtitle evidence to Gemini, and writes results back.
- `scripts/run_pending.ps1`: Windows-friendly runner for scheduled execution.

Typical dry run:

```powershell
python scripts/process_videos.py --dry-run --max-records 20 --limit 200
```

Typical batch run:

```powershell
python scripts/process_videos.py --max-records 50 --workers 3 --limit 200 --mode video-fast
```

Retry specific records:

```powershell
python scripts/process_videos.py --record-ids recxxxx,recyyyy --max-records 2 --workers 2 --mode video-fast
```

## Output Contract

Keep the table easy to scan. The script reads the live field list and writes only fields that exist.

Important field formats:

- `视频框架`: 3-5 short Chinese action labels joined with `+`, for example `痛点介绍+产品展示+使用演示+引导下单`.
- `视频标题`: source caption or concise localized title.
- `原文口播`: line-based transcript, preferably `00:00-00:03 原文句子`; use `无口播/以画面和屏幕文字为主` when appropriate.
- `中文翻译`: line-based translation aligned with the transcript.
- `纯口播文本`: Chinese spoken text with timestamps removed, derived from `中文翻译`.
- `痛点分析`, `卖点分析`, `可复用点`: single-select values only.

Read `references/workflow.md` before changing schema mappings, retry behavior, deployment, or table operations.
