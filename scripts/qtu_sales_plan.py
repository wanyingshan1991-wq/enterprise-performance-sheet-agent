import argparse
import json
from pathlib import Path
from typing import Any

from dws_client import DwsClient
from generators.qtu_sales_plan import generate


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.json"


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    example = ROOT / "config" / "config.example.json"
    return json.loads(example.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="千图年月销售计划调整表格生成工具")
    parser.add_argument("--target-month", type=int, required=True, help="目标月份，例如 9")
    parser.add_argument("--source-month", type=int, help="源月份，默认目标月份 - 1")
    parser.add_argument("--channel", action="append", help="只处理指定渠道，可重复传入")
    parser.add_argument("--execute", action="store_true", help="实际写入钉钉表格；不传则只预览")
    parser.add_argument("--force-copy", action="store_true", help="目标 sheet 已存在时仍尝试复制")
    parser.add_argument("--check-auth", action="store_true", help="先输出 DWS 登录和 profile 状态")
    args = parser.parse_args()

    config = load_config()
    if args.check_auth:
        client = DwsClient(config)
        print(json.dumps(client.profile_list(), ensure_ascii=False, indent=2))

    results = generate(
        config,
        target_month=args.target_month,
        source_month=args.source_month,
        channel_names=args.channel,
        execute=args.execute,
        force_copy=args.force_copy,
    )
    print(json.dumps({"execute": args.execute, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
