# UI Design System Governor Skill

## 项目简介

本项目用于设计一个可复用的 Agent skill：在新建 UI、改版现有页面或执行设计一致性审查时，从内嵌的 Open Design 设计系统中选择并应用一套明确的视觉规则，同时保留用户确认、冲突处理和验证闭环。

主要交付物是 `ui-design-system-governor` skill、配套的 Python 标准库脚本、数据契约、测试，以及完整复制到 skill assets 中的 `design-systems/`。

## 当前状态

设计规格与实施计划已获确认；Git 仓库已初始化，即将按计划实施 skill。

## 功能范围

计划包含：

- 新建前端、产品页面和原型 UI。
- 对现有页面进行设计系统化改版。
- 设计一致性审查，以及经用户批准后的修复。
- 设计系统推荐、人工确认、需求冲突暂停和证据化合规报告。
- 本地离线索引、透明评分、规则编译和静态校验。
- 对本地代码、截图、设计稿、URL 与 Figma 等输入进行能力自适应处理。

暂不包含：

- 在线自动更新设计系统资产。
- 把设计系统预览网页作为运行时规则来源。
- 绕过用户确认自动选择未指定的设计系统。
- 在审查模式下未经批准自动修改页面。
- 承诺商标、品牌授权或完整无障碍合规。

## 项目结构

- `design-systems/`：当前 151 套源设计系统及 `_schema/` 契约目录，实施时完整复制到 skill assets。
- `docs/superpowers/specs/`：已批准的设计规格。
- `.learnings/`：执行错误与用户纠正记录。
- `.superpowers/brainstorm/`：Visual Companion 临时会话文件，不属于最终交付物。

## 技术栈与运行方式

计划使用 Markdown、JSON Schema、CSS 解析和 Python 3.10+ 标准库实现，不引入运行时第三方 Python 依赖。

当前尚无可运行命令。安装、构建索引、校验、测试和使用方式将在实现阶段补充。

## 文档索引

- [UI Design System Governor 设计规格](docs/superpowers/specs/2026-07-12-ui-design-system-governor-design.md)
- [UI Design System Governor 实施计划](docs/superpowers/plans/2026-07-12-ui-design-system-governor.md)

## 已知限制

- 当前仓库是新初始化的本地 Git 仓库，尚未配置远程仓库。
- `rtk` 不在当前 PowerShell PATH 中，现阶段使用等价的 PowerShell、Git 和 `rg` 命令。
- 目标 skill 目录和脚本尚未创建。
