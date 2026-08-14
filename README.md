# company-qtu 千图业绩管理自动化脚本

本项目基于 `enterprise-performance-sheet-agent` 生成，服务于千图的钉钉业绩管理表格维护。

- 企业代号：`company-qtu`
- 平台：钉钉
- 目标范围：年月销售计划调整表格自生成 sheet
- 正式文件夹：千图业绩管理看板

## 这个工具做什么

工具维护以下路径中的在线表格：

```text
千图业绩管理看板 / 部门计划 / 年月计划（调整填录） / 年月销售计划调整
```

当前覆盖 5 个渠道表：

- 天猫
- 抖音
- 私域
- 视频号
- 小红书

生成目标月份时，工具会：

- 检查当前钉钉 DWS 授权状态
- 检查每个渠道表是否存在源月份 sheet
- 如果目标月份 sheet 已存在，默认跳过
- 复制上月 sheet，生成目标月份 sheet
- 替换公式里的上月引用
- 清空人工填写区 `D30:T31`

工具不会删除表格或 sheet。

## 日常使用

双击：

```text
run.bat
```

会看到菜单：

```text
==============================================
 company-qtu 千图业绩管理自动化工具
 钉钉：年月销售计划调整 sheet 生成
==============================================
1. 预览生成目标月份 sheet（不写入）
2. 执行生成目标月份 sheet（写入钉钉）
3. 单渠道预览 / 执行
4. 检查钉钉授权状态
5. 查看当前配置的表格节点
0. 退出
请输入菜单选项:
```

推荐流程：

1. 先选 `1` 预览。
2. 输入目标月份，例如 `9`。
3. 确认每个渠道的源 sheet 和目标 sheet 是否符合预期。
4. 再选 `2` 执行写入。
5. 看到二次确认时，只有确认无误才输入 `YES`。

## 菜单说明

`1. 预览生成目标月份 sheet（不写入）`

只读取钉钉数据并展示将要执行的动作，不修改表格。

`2. 执行生成目标月份 sheet（写入钉钉）`

写入钉钉表格。会复制源月份 sheet、替换公式引用、清空人工填写区。

`3. 单渠道预览 / 执行`

只处理一个渠道，适合补生成或排查单个渠道问题。

`4. 检查钉钉授权状态`

查看本机 DWS profile，确认当前组织是“广州三木织造有限公司”。

`5. 查看当前配置的表格节点`

查看 5 个渠道表对应的钉钉 nodeId。

## 命令行用法

预览 9 月全部渠道：

```powershell
python scripts\qtu_sales_plan.py --target-month 9 --check-auth
```

执行生成 9 月全部渠道：

```powershell
python scripts\qtu_sales_plan.py --target-month 9 --execute
```

只预览天猫：

```powershell
python scripts\qtu_sales_plan.py --target-month 9 --channel 天猫
```

## 配置文件

默认配置在：

```text
config/config.example.json
```

如需本地覆盖配置，可创建：

```text
config/config.json
```

不要把包含私有信息的 `config/config.json` 提交到 GitHub。

## 规则文档

表格结构、公式依赖和维护规则整理在：

```text
rules/qtu_sales_plan_rules.md
```

## 安全说明

- 默认是预览模式。
- 只有菜单选项 `2` 或命令参数 `--execute` 才会写入。
- 写入前需要输入 `YES` 二次确认。
- 目标月份 sheet 已存在时默认跳过。
- 不使用删除类命令。
