import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def env_value(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def load_env_file(path):
    path = Path(path)
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def lark_cli_path(explicit=""):
    return (
        explicit
        or os.environ.get("LARK_CLI")
        or shutil.which("lark-cli")
        or shutil.which("lark-cli.cmd")
        or "lark-cli"
    )


def run_command(command, timeout):
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return {
            "code": 127,
            "stdout": "",
            "stderr": str(exc),
            "seconds": round(time.perf_counter() - started, 2),
        }
    return {
        "code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "seconds": round(time.perf_counter() - started, 2),
    }


def load_schema(schema_path):
    fields = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    if not isinstance(fields, list) or not fields:
        raise SystemExit("Schema must be a non-empty JSON array of field definitions.")
    return fields


def main():
    load_env_file(ROOT / ".env")
    load_env_file(Path.cwd() / ".env")

    parser = argparse.ArgumentParser(description="Create a Feishu/Lark table for TikTok video analysis.")
    parser.add_argument("--base-token", default=env_value("FEISHU_BASE_TOKEN", "LARK_BASE_TOKEN"))
    parser.add_argument("--table-name", default="TikTok视频分析")
    parser.add_argument("--schema", default=str(ROOT / "references" / "table_schema.json"))
    parser.add_argument("--lark-cli", default=env_value("LARK_CLI"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    fields = load_schema(args.schema)
    lark_cli = lark_cli_path(args.lark_cli)
    fields_json = json.dumps(fields, ensure_ascii=False, separators=(",", ":"))
    command = [
        lark_cli,
        "base",
        "+table-create",
        "--base-token",
        args.base_token or "<FEISHU_BASE_TOKEN>",
        "--name",
        args.table_name,
        "--fields",
        fields_json,
        "--format",
        "json",
    ]

    if args.dry_run:
        print(
            json.dumps(
                {
                    "table_name": args.table_name,
                    "schema_path": str(Path(args.schema).resolve()),
                    "field_count": len(fields),
                    "lark_cli": lark_cli,
                    "will_create_table": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if not args.base_token:
        raise SystemExit("Missing Feishu base token. Set FEISHU_BASE_TOKEN or pass --base-token.")

    result = run_command(command, timeout=90)
    print(result["stdout"] or result["stderr"])
    if result["code"] != 0:
        raise SystemExit(result["code"])


if __name__ == "__main__":
    main()

