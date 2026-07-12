# UI Design System Governor Skill

## 项目简介

本项目提供可复用的 `ui-design-system-governor` Agent skill。它在新建 UI、改版现有页面或执行设计一致性审查时，使用仓库内置的 151 套 Open Design 设计系统指导视觉风格、tokens、组件和布局，并对选择、冲突与审查修复设置强制用户确认门。

skill 运行时只依赖 Python 3.10+ 标准库；设计系统选择、规则编译、静态审查与包完整性验证均可离线执行。

## 当前状态

状态：已实现并完成本地验证。

- 151 套设计系统与 `_schema/` 已完整复制到 skill assets。
- 目录、选择画像和 SHA-256 库存清单已生成并验证确定性。
- 新建设计、现有页面改版、设计一致性审查三种模式已覆盖。
- 官方 skill 快速验证、自研包验证和 99 项本地测试全部通过。
- GitHub Actions 已配置 3 个操作系统 × 3 个 Python 版本的矩阵；仓库尚未配置远程，因此 CI 尚未在线运行。

## 关键行为

- 调用消息明确指定有效设计系统：直接验证并使用该系统。
- 未明确指定：推荐可靠候选，提供或打开[视觉预览目录](https://open-design.ai/zh/plugins/systems/)，然后暂停等待用户选择。
- 没有可靠候选：不凑数推荐，仍提供或打开预览目录，然后暂停供用户手动选择或调整条件。
- 需求与所选系统冲突：说明具体冲突、坚持使用的风险和可靠替代系统，然后暂停等待用户决定。
- 一致性审查：先交付证据化报告，等待用户批准全部或指定修复项后才可改动目标。

## 项目结构

- `ui-design-system-governor/`：可交付 skill。
  - `SKILL.md`：控制器、任务路由和强制暂停门。
  - `scripts/`：契约、目录、推荐、规则编译、静态审查和包验证工具。
  - `references/`：选择、新建、改版、审查、冲突和输出协议。
  - `schemas/`：四个跨 Agent 数据契约。
  - `assets/design-systems/`：151 套只读设计系统资产。
  - `assets/catalog/`：选择画像、目录索引和库存哈希。
- `design-systems/`：资产源目录；刷新时以此为唯一来源。
- `tests/`：单元、行为契约、压力基线和端到端测试。
- `docs/superpowers/`：设计规格与实施计划。

## 调用示例

未指定设计系统，skill 必须推荐并暂停：

```text
Use $ui-design-system-governor to create a compact analytics dashboard for technical operators.
```

明确指定设计系统，可在验证和冲突检查后继续：

```text
Use $ui-design-system-governor with the minimal design system to redesign this product page.
```

审查模式，报告后必须等待修复批准：

```text
Use $ui-design-system-governor with the minimal design system to audit this existing frontend for design consistency.
```

## 本地验证

从仓库根目录运行：

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
$env:PYTHONUTF8 = "1"
python "<skill-creator>/scripts/quick_validate.py" ui-design-system-governor
python ui-design-system-governor/scripts/validate_package.py --skill-root ui-design-system-governor --expected-system-count 151
```

端到端测试会验证：SelectionProfile → 推荐 → 规则编译 → 静态审查 → 报告契约，同时确认 skill 资产在流程前后哈希不变。

## 常用脚本

生成推荐：

```powershell
python ui-design-system-governor/scripts/recommend_systems.py --profile tests/fixtures/selection-profile.json --catalog ui-design-system-governor/assets/catalog/design-systems.index.json
```

编译已确认系统的规则：

```powershell
python ui-design-system-governor/scripts/compile_rules.py --system-dir ui-design-system-governor/assets/design-systems/minimal --output .superpowers/sdd/minimal-rules.json
```

只读审查前端项目：

```powershell
python ui-design-system-governor/scripts/audit_static.py --project tests/fixtures/sample-ui --bundle .superpowers/sdd/minimal-rules.json --output .superpowers/sdd/compliance-report.json
```

## 刷新设计系统资产

1. 先更新根目录 `design-systems/`，并核对每个系统目录名与 `manifest.json` ID。
2. 在确认源路径和目标路径都位于本仓库后，用源目录完整替换 `ui-design-system-governor/assets/design-systems/`；不要合并旧目录，否则已删除的源文件可能残留。
3. 根据新增类别或视觉证据更新 `scripts/build_catalog.py` 中的固定类别映射和逐系统复核覆盖项。
4. 重新生成画像、索引和库存：

```powershell
python ui-design-system-governor/scripts/build_catalog.py --asset-root ui-design-system-governor/assets/design-systems --profiles ui-design-system-governor/assets/catalog/selection-profiles.json --bootstrap-profiles --force
python ui-design-system-governor/scripts/build_catalog.py --asset-root ui-design-system-governor/assets/design-systems --profiles ui-design-system-governor/assets/catalog/selection-profiles.json --index ui-design-system-governor/assets/catalog/design-systems.index.json --inventory ui-design-system-governor/assets/catalog/inventory.json
```

5. 再运行完整测试和包验证。对索引与库存重复生成两次并比较 SHA-256，确认结果稳定。

## CI

`.github/workflows/test.yml` 在 `windows-latest`、`macos-latest`、`ubuntu-latest` 上分别测试 Python 3.10、3.12、3.14。矩阵运行完整测试、官方 quick-validator 快照和包验证器。skill 本身没有第三方运行时依赖；CI 仅安装官方验证器需要的 PyYAML。

## 已知限制

- 推荐画像是离线、人工可复核的数据，不会在线同步设计系统更新。
- 预览网站只用于视觉浏览，不是规则数据源。
- 静态审查只读取指定前端文本扩展名，跳过构建目录、超过 2 MiB 的文件和二进制文件；它不执行 HTML 或项目代码。
- 视觉语义、完整无障碍、跨浏览器和真实响应式表现仍需 Agent 或浏览器工具复核。
- 用户禁止继续使用子代理后，前向测试改为确定性行为契约测试；20 个独立 skill-enabled Agent 样本未运行，限制已如实记录在 `tests/skill_scenarios/with-skill-results.md`。
- 当前本地仓库尚未配置远程；`rtk` 也不在当前 PowerShell PATH 中。

## 文档索引

- [设计规格](docs/superpowers/specs/2026-07-12-ui-design-system-governor-design.md)
- [实施计划](docs/superpowers/plans/2026-07-12-ui-design-system-governor.md)
- [Skill 控制器](ui-design-system-governor/SKILL.md)
- [前向测试替代记录](tests/skill_scenarios/with-skill-results.md)
