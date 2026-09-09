# Workflow Reference

## Purpose

This skill turns a Feishu/Lark Base into a TikTok video-analysis queue:

1. Operators paste a TikTok URL into `视频链接`.
2. Operators set `任务状态` to `待处理`.
3. The runner downloads the video with `yt-dlp`; if that fails, it tries `meowload`.
4. The runner sends VTT subtitles and/or the MP4 video to Gemini.
5. Gemini returns normalized JSON.
6. The runner writes analysis fields back to the same row.

## Required Configuration

Configuration must come from environment variables, `.env`, or explicit command arguments.

- `FEISHU_BASE_TOKEN`: target Base app token
- `FEISHU_TABLE_ID`: target table id
- `GEMINI_API_KEY`: Gemini API key
- `LARK_CLI`: optional path to `lark-cli`
- `MEOWLOAD_BIN`: optional path to `meowload`

Do not hardcode company, personal, or machine-specific values in the skill.

## Table Schema

The recommended schema is stored in `references/table_schema.json`. It is intentionally optimized for scanability:

- Operational fields: link, status, owner, finish time, failure reason.
- Source metrics: platform, creator, publish time, duration, views, likes, comments, saves, shares, engagement rate.
- Analysis fields: title, transcript, translation, framework, shot script, type/mode/hook, pain point, selling point, reusable point, risk note.
- Runtime fields: downloader, download seconds, analysis seconds, estimated AI cost, analysis version.

The processing script filters writes against the live field list, so teams can delete fields they do not need without breaking the run.

## Downloader Strategy

Default path:

- Try `yt-dlp` first with subtitles and MP4 download.
- If `yt-dlp` fails and mode is `video-fast`, try `meowload`.
- If both fail, mark the row as `待人工处理` and write the failure reason.

Browser cookies and logged-in browser state are not part of the default open-source flow. Only use cookies after a user explicitly authorizes that for their own environment.

## Gemini Strategy

Use `video-fast` for quality and speed:

- VTT subtitle evidence is used when available.
- MP4 video is used for visual structure, screen text, and transcript recovery.
- Output must be JSON so the table can be updated deterministically.

Use `vtt-fast` only when teams want a cheaper subtitle-only pass and accept lower visual accuracy.

## Deployment Options

Local scheduled run:

- Put this skill on a stable workstation.
- Configure `.env`.
- Use Windows Task Scheduler, cron, or another scheduler to run `scripts/run_pending.ps1` every few minutes.

Server worker:

- Install Python, `yt-dlp`, `ffmpeg`, `lark-cli`, optional `meowload`.
- Store secrets in the server secret manager or environment variables.
- Run `scripts/process_videos.py` from a scheduled job or queue worker.
- Keep `work/` and `outputs/` out of source control.

Feishu automation or webhook:

- Let Feishu trigger a backend endpoint when a row enters `待处理`.
- The backend queues the row id and calls `scripts/process_videos.py --record-ids <record_id>`.
- Keep retries bounded and leave persistent failures as `待人工处理`.

## Status Handling

- `待处理`: ready to process.
- `解析中`: runner has claimed the row.
- `AI解析完成`: Gemini analysis has been written.
- `待人工处理`: downloader or parser failed after supported fallbacks.
- `已完成`: optional human-reviewed final state.

