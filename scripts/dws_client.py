import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_DWS = r"C:\Users\Administrator\.dws\data\backups\v1.0.50-20260714-093740\binary\dws.exe"


def resolve_dws(config: dict[str, Any] | None = None) -> str:
    config = config or {}
    configured = config.get("dws_cli_path")
    if configured:
        return configured
    from_env = os.environ.get("DWS_CLI")
    if from_env:
        return from_env
    found = shutil.which("dws") or shutil.which("dws.exe")
    if found:
        return found
    if Path(DEFAULT_DWS).exists():
        return DEFAULT_DWS
    raise RuntimeError("未找到 dws CLI。请先安装/启用钉钉 DWS CLI，或在 config/config.json 设置 dws_cli_path。")


class DwsClient:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.dws = resolve_dws(self.config)
        self.profile = self.config.get("dingtalk_profile")

    def run(self, args: list[str], timeout: int = 60) -> dict[str, Any]:
        cmd = [self.dws, *args, "--format", "json"]
        if self.profile and "--profile" not in args:
            cmd.extend(["--profile", self.profile])
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
        stdout = proc.stdout.decode("utf-8", errors="replace").strip()
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        if proc.returncode != 0:
            raise RuntimeError(f"dws failed: {' '.join(args)}\n{stderr or stdout}")
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"dws returned non-JSON output: {stdout}") from exc
        if result.get("success") is False or result.get("error"):
            raise RuntimeError(f"dws returned error: {json.dumps(result, ensure_ascii=False)}")
        return result

    def auth_status(self) -> dict[str, Any]:
        return self.run(["auth", "status"])

    def profile_list(self) -> dict[str, Any]:
        return self.run(["profile", "list"])

    def sheet_list(self, node_id: str) -> list[dict[str, Any]]:
        return self.run(["sheet", "list", "--node", node_id])["sheets"]

    def sheet_id_by_name(self, node_id: str) -> dict[str, str]:
        return {sheet["name"]: sheet["sheetId"] for sheet in self.sheet_list(node_id)}

    def copy_sheet(self, node_id: str, source_sheet_id: str, target_name: str, index: int = 0) -> dict[str, Any]:
        return self.run(
            [
                "sheet",
                "copy",
                "--node",
                node_id,
                "--sheet-id",
                source_sheet_id,
                "--name",
                target_name,
                "--index",
                str(index),
            ],
            timeout=120,
        )

    def clear_range(self, node_id: str, sheet_id: str, range_a1: str) -> None:
        self.run(
            [
                "sheet",
                "range",
                "clear",
                "--node",
                node_id,
                "--sheet-id",
                sheet_id,
                "--range",
                range_a1,
                "--type",
                "content",
            ]
        )

    def replace(self, node_id: str, sheet_id: str, find: str, replacement: str) -> dict[str, Any]:
        return self.run(
            [
                "sheet",
                "replace",
                "--node",
                node_id,
                "--sheet-id",
                sheet_id,
                "--find",
                find,
                "--replacement",
                replacement,
            ],
            timeout=120,
        )
