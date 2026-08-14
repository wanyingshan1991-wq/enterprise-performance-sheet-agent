from typing import Any

from dws_client import DwsClient


CHANNELS = [
    {"name": "天猫", "node_id": "vy20BglGWOZYqj6lfgXeXOyA8A7depqY"},
    {"name": "抖音", "node_id": "ZgpG2NdyVXvdjmowfPn9npLe8MwvDqPk"},
    {"name": "私域", "node_id": "7NkDwLng8ZDjk7xwiN5v5ElaVKMEvZBY"},
    {"name": "视频号", "node_id": "EpGBa2Lm8aprmxdDiwKnKN2KJgN7R35y"},
    {"name": "小红书", "node_id": "6LeBq413JAKnmBMLF3d2lzR3WDOnGvpb"},
]

MANUAL_CLEAR_RANGES = ["D30:T31"]


def month_sheet_name(month: int) -> str:
    return f"{month}月"


def validate_month(month: int) -> None:
    if month < 1 or month > 12:
        raise ValueError("月份必须在 1-12 之间。")


def channels_from_config(config: dict[str, Any]) -> list[dict[str, str]]:
    configured = config.get("qtu_sales_plan", {}).get("channels")
    if configured:
        return configured
    return CHANNELS


def selected_channels(config: dict[str, Any], names: list[str] | None = None) -> list[dict[str, str]]:
    channels = channels_from_config(config)
    if not names:
        return channels
    wanted = set(names)
    selected = [channel for channel in channels if channel["name"] in wanted]
    missing = wanted - {channel["name"] for channel in selected}
    if missing:
        raise RuntimeError(f"未知渠道：{', '.join(sorted(missing))}")
    return selected


def generate(
    config: dict[str, Any],
    target_month: int,
    source_month: int | None = None,
    channel_names: list[str] | None = None,
    execute: bool = False,
    force_copy: bool = False,
) -> list[dict[str, Any]]:
    validate_month(target_month)
    source_month = source_month or target_month - 1
    validate_month(source_month)

    client = DwsClient(config)
    target_sheet = month_sheet_name(target_month)
    source_sheet = month_sheet_name(source_month)
    previous_formula_sheet = month_sheet_name(max(source_month - 1, 1))
    results: list[dict[str, Any]] = []

    for channel in selected_channels(config, channel_names):
        node_id = channel["node_id"]
        sheet_ids = client.sheet_id_by_name(node_id)
        source_sheet_id = sheet_ids.get(source_sheet)
        target_exists = target_sheet in sheet_ids
        if not source_sheet_id:
            raise RuntimeError(f"{channel['name']} 缺少源 sheet：{source_sheet}")

        action = {
            "channel": channel["name"],
            "node_id": node_id,
            "source_sheet": source_sheet,
            "target_sheet": target_sheet,
            "created": False,
            "cleared_ranges": [],
            "formula_reference_replaced": False,
            "skipped": False,
        }

        if target_exists and not force_copy:
            action["skipped"] = True
            action["reason"] = "目标 sheet 已存在；如需重新复制请使用 --force-copy。"
            results.append(action)
            continue

        if execute:
            client.copy_sheet(node_id, source_sheet_id, target_sheet, index=0)
            target_sheet_id = client.sheet_id_by_name(node_id).get(target_sheet)
            if not target_sheet_id:
                raise RuntimeError(f"{channel['name']} 复制后未找到目标 sheet：{target_sheet}")

            client.replace(
                node_id,
                target_sheet_id,
                f"'{previous_formula_sheet}'!",
                f"'{source_sheet}'!",
            )
            action["formula_reference_replaced"] = True

            for range_a1 in MANUAL_CLEAR_RANGES:
                client.clear_range(node_id, target_sheet_id, range_a1)
                action["cleared_ranges"].append(range_a1)

        action["created"] = execute
        results.append(action)

    return results
