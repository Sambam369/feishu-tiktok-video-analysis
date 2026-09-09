# Feishu TikTok Video Analysis

一个可开源的 Codex skill 模板：从飞书/维格表多维表格读取 TikTok 链接，自动下载视频，用 Gemini 快速拆解，再把结构化结果回填到表格。

这个版本已经移除私人配置。仓库里不包含任何 Base token、Table ID、API Key、账号密码、cookies 或本机绝对路径。

## 你需要准备

- Python 3.10+
- `yt-dlp`
- `lark-cli`，并完成你自己账号/应用的授权
- Gemini API Key
- 可选：`meowload`，作为 TikTok 下载失败时的备用下载器

Windows 如果 `python` 指向 Microsoft Store 占位入口，可以把下面命令里的 `python` 改成 `py`。

## 快速开始

如果是给 Codex 安装，把整个仓库或 skill 子目录发给同事，让他们在 Codex 里说：

```text
帮我从这个 GitHub 地址安装 skill：<你的 GitHub 仓库或子目录地址>
```

1. 复制配置模板：

```powershell
Copy-Item .env.example .env
```

2. 安装 Python 依赖：

```powershell
py -m pip install -r requirements.txt
```

3. 在 `.env` 里填你自己的配置：

```text
FEISHU_BASE_TOKEN=replace_with_your_base_token
FEISHU_TABLE_ID=replace_with_your_table_id
GEMINI_API_KEY=replace_with_your_gemini_api_key
```

4. 如果还没有表格，先创建一张新表：

```powershell
python scripts/setup_table.py --base-token YOUR_BASE_TOKEN --table-name "TikTok视频分析"
```

把命令返回的 table id 填入 `.env` 的 `FEISHU_TABLE_ID`。

5. 在表格里新增一行，把 TikTok 链接填到 `视频链接`，并把 `任务状态` 设为 `待处理`。

6. 先试运行：

```powershell
python scripts/process_videos.py --dry-run --max-records 20
```

7. 正式批量执行：

```powershell
python scripts/process_videos.py --max-records 50 --workers 3 --mode video-fast
```

## 自动化运行

Windows 可以用任务计划程序定时执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_pending.ps1
```

公司服务器版本建议用定时任务、队列 worker 或 Feishu 自动化/webhook 触发同一个脚本。详见 `references/workflow.md`。

## 安全约定

- 不提交 `.env`。
- 不把真实 API Key、账号密码、cookies 写入代码或文档。
- 不默认读取浏览器 cookies；只有用户明确授权时才允许把登录态作为下载备用方案。
- 运行脚本会修改飞书表格，正式执行前先用 `--dry-run` 检查目标表和待处理记录。
