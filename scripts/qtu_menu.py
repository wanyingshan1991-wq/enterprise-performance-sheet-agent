from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_tool(args: list[str]) -> int:
    proc = subprocess.run([PYTHON, str(ROOT / "scripts" / "qtu_sales_plan.py"), *args])
    return proc.returncode


def ask_month(prompt: str) -> str:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= 12:
            return raw
        print("请输入 1-12 之间的月份数字。")


def ask_channels() -> list[str]:
    print("")
    print("请选择渠道范围：")
    print("1. 全部渠道")
    print("2. 天猫")
    print("3. 抖音")
    print("4. 私域")
    print("5. 视频号")
    print("6. 小红书")
    choice = input("请输入选项 [1]: ").strip() or "1"
    mapping = {
        "2": "天猫",
        "3": "抖音",
        "4": "私域",
        "5": "视频号",
        "6": "小红书",
    }
    if choice == "1":
        return []
    if choice in mapping:
        return [mapping[choice]]
    print("未识别的选项，默认处理全部渠道。")
    return []


def preview_or_execute(execute: bool, single_channel: bool = False) -> None:
    month = ask_month("请输入目标月份，例如 9: ")
    args = ["--target-month", month]
    channels = ask_channels() if single_channel else []
    for channel in channels:
        args.extend(["--channel", channel])

    if execute:
        print("")
        print("即将写入钉钉表格，执行内容包括：")
        print("- 复制上月 sheet 为目标月份 sheet")
        print("- 替换公式里的上月引用")
        print("- 清空人工填写区 D30:T31")
        confirm = input("确认执行请输入 YES: ").strip()
        if confirm.upper() != "YES":
            print("已取消写入。")
            return
        args.append("--execute")
    else:
        args.append("--check-auth")

    run_tool(args)


def show_config() -> None:
    path = ROOT / "config" / "config.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(
        {
            "企业代号": data.get("company_code"),
            "平台": data.get("platform"),
            "知识库": data.get("workspace_id"),
            "销售计划调整文件夹": data.get("sales_plan_folder_node_id"),
            "渠道表": data.get("qtu_sales_plan", {}).get("channels", []),
        },
        ensure_ascii=False,
        indent=2,
    ))


def main() -> None:
    while True:
        print("")
        print("==============================================")
        print(" company-qtu 千图业绩管理自动化工具")
        print(" 钉钉：年月销售计划调整 sheet 生成")
        print("==============================================")
        print("1. 预览生成目标月份 sheet（不写入）")
        print("2. 执行生成目标月份 sheet（写入钉钉）")
        print("3. 单渠道预览 / 执行")
        print("4. 检查钉钉授权状态")
        print("5. 查看当前配置的表格节点")
        print("0. 退出")
        choice = input("请输入菜单选项: ").strip()

        if choice == "1":
            preview_or_execute(execute=False)
        elif choice == "2":
            preview_or_execute(execute=True)
        elif choice == "3":
            mode = input("是否只预览？直接回车为是，输入 N 则执行写入 [Y/n]: ").strip().lower()
            preview_or_execute(execute=(mode == "n"), single_channel=True)
        elif choice == "4":
            run_tool(["--target-month", "9", "--check-auth"])
        elif choice == "5":
            show_config()
        elif choice == "0":
            print("已退出。")
            return
        else:
            print("未识别的菜单选项。")


if __name__ == "__main__":
    main()
