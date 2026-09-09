param(
    [string]$Python = "py",
    [string]$BaseToken = "",
    [string]$TableId = "",
    [string]$LarkCli = "",
    [string]$MeowloadBin = "",
    [int]$Limit = 200,
    [int]$MaxRecords = 50,
    [int]$Workers = 3,
    [ValidateSet("video-fast", "vtt-fast")]
    [string]$Mode = "video-fast",
    [string]$RecordIds = "",
    [switch]$DryRun,
    [switch]$SkipTableWrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "process_videos.py"
$arguments = @(
    $scriptPath,
    "--limit", "$Limit",
    "--max-records", "$MaxRecords",
    "--workers", "$Workers",
    "--mode", "$Mode"
)

if ($BaseToken) { $arguments += @("--base-token", $BaseToken) }
if ($TableId) { $arguments += @("--table-id", $TableId) }
if ($LarkCli) { $arguments += @("--lark-cli", $LarkCli) }
if ($MeowloadBin) { $arguments += @("--meowload-bin", $MeowloadBin) }
if ($RecordIds) { $arguments += @("--record-ids", $RecordIds) }
if ($DryRun) { $arguments += "--dry-run" }
if ($SkipTableWrite) { $arguments += "--skip-table-write" }

& $Python @arguments
