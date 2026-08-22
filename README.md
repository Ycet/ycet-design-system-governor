[![中文](https://img.shields.io/badge/简体中文-red?style=for-the-badge)](README.md)
[![EN](https://img.shields.io/badge/English-blue?style=for-the-badge)](README_en.md)

# ycet-design-system-governor

内置 151 套设计系统的 Agent Skill：新建 UI、改版页面或审查设计一致性时，强制走「选择 → 确认 → 应用 → 审查」治理流程。

---

## ✨ 功能特性

| 特性 | 说明 |
| --- | --- |
| 🎨 内置设计系统库 | 151 套 Open Design 设计系统资产，离线可用，仅依赖 Python 3.10+ 标准库 |
| 🧭 透明推荐 | 基于可复核的离线选择画像推荐候选系统；无可靠候选时不凑数 |
| 🚦 强制确认门 | 系统选择、冲突坚持、审查修复均需用户明确批准后才继续 |
| 🛡️ 证据化审查 | 只读静态审查生成证据化合规报告，契约化输出（JSON Schema） |
| 🔒 完整性验证 | SHA-256 库存清单 + 包验证器，确保资产在流程前后哈希不变 |
| 🤖 CI 矩阵 | GitHub Actions 覆盖 3 系统 × 3 Python 版本（3.10 / 3.12 / 3.14） |

## 🚀 快速开始

```powershell
git clone https://github.com/Ycet/ycet-design-system-governor.git
cd ycet-design-system-governor

# 运行完整测试（99 项）
python -m unittest discover -s tests -p "test_*.py" -v

# 验证 skill 包完整性
python outputs/ycet-design-system-governor/scripts/validate_package.py --skill-root outputs/ycet-design-system-governor --expected-system-count 151
```

## 📖 使用说明

在支持 Agent Skill 的客户端中调用 `$ycet-design-system-governor`：

未指定设计系统时，skill 必须推荐候选并暂停等待选择：

```text
Use $ycet-design-system-governor to create a compact analytics dashboard for technical operators.
```

明确指定设计系统时，在验证与冲突检查通过后继续：

```text
Use $ycet-design-system-governor with the minimal design system to redesign this product page.
```

审查模式下，报告交付后必须等待修复项被批准：

```text
Use $ycet-design-system-governor with the minimal design system to audit this existing frontend for design consistency.
```

## 📁 项目结构

| 目录 | 说明 |
| --- | --- |
| `outputs/ycet-design-system-governor/` | 可交付 skill 本体（SKILL.md、scripts、references、schemas、assets） |
| `design-systems/` | 151 套设计系统资产源目录；刷新时以此为唯一来源 |
| `tests/` | 单元、行为契约、压力基线与端到端测试 |
| `docs/superpowers/` | 设计规格与实施计划 |
| `.github/` | CI 工作流与官方验证器快照 |

## 🔧 常用脚本

```powershell
# 生成推荐（基于选择画像）
python outputs/ycet-design-system-governor/scripts/recommend_systems.py --profile tests/fixtures/selection-profile.json --catalog outputs/ycet-design-system-governor/assets/catalog/design-systems.index.json

# 编译已确认系统的规则
python outputs/ycet-design-system-governor/scripts/compile_rules.py --system-dir outputs/ycet-design-system-governor/assets/design-systems/minimal --output .superpowers/sdd/minimal-rules.json

# 只读审查前端项目
python outputs/ycet-design-system-governor/scripts/audit_static.py --project tests/fixtures/sample-ui --bundle .superpowers/sdd/minimal-rules.json --output .superpowers/sdd/compliance-report.json
```

## ♻️ 刷新设计系统资产

<details>
<summary>展开查看资产刷新流程</summary>

1. 先更新根目录 `design-systems/`，并核对每个系统目录名与 `manifest.json` ID。
2. 在确认源路径和目标路径都位于本仓库后，用源目录完整替换 `outputs/ycet-design-system-governor/assets/design-systems/`；不要合并旧目录，否则已删除的源文件可能残留。
3. 根据新增类别或视觉证据更新 `scripts/build_catalog.py` 中的固定类别映射和逐系统复核覆盖项。
4. 重新生成画像、索引和库存：

```powershell
python outputs/ycet-design-system-governor/scripts/build_catalog.py --asset-root outputs/ycet-design-system-governor/assets/design-systems --profiles outputs/ycet-design-system-governor/assets/catalog/selection-profiles.json --bootstrap-profiles --force
python outputs/ycet-design-system-governor/scripts/build_catalog.py --asset-root outputs/ycet-design-system-governor/assets/design-systems --profiles outputs/ycet-design-system-governor/assets/catalog/selection-profiles.json --index outputs/ycet-design-system-governor/assets/catalog/design-systems.index.json --inventory outputs/ycet-design-system-governor/assets/catalog/inventory.json
```

5. 再运行完整测试和包验证。对索引与库存重复生成两次并比较 SHA-256，确认结果稳定。

</details>

## 🤖 CI

`.github/workflows/test.yml` 在 `windows-latest`、`macos-latest`、`ubuntu-latest` 上分别测试 Python 3.10、3.12、3.14。矩阵运行完整测试、官方 quick-validator 快照和包验证器。skill 本身没有第三方运行时依赖；CI 仅安装官方验证器需要的 PyYAML。

## ⚠️ 已知限制

- 推荐画像是离线、人工可复核的数据，不会在线同步设计系统更新。
- 预览网站只用于视觉浏览，不是规则数据源。
- 静态审查只读取指定前端文本扩展名，跳过构建目录、超过 2 MiB 的文件和二进制文件；它不执行 HTML 或项目代码。
- 视觉语义、完整无障碍、跨浏览器和真实响应式表现仍需 Agent 或浏览器工具复核。
- 前向测试采用确定性行为契约测试替代独立 skill-enabled Agent 样本，限制已如实记录在 `tests/skill_scenarios/with-skill-results.md`。

## 📚 文档索引

- [设计规格](docs/superpowers/specs/2026-07-12-ui-design-system-governor-design.md)
- [实施计划](docs/superpowers/plans/2026-07-12-ui-design-system-governor.md)
- [Skill 控制器](outputs/ycet-design-system-governor/SKILL.md)
- [前向测试替代记录](tests/skill_scenarios/with-skill-results.md)

## 📄 许可证

本仓库当前未附带 `LICENSE` 文件，许可证类型待定；在明确授权条款之前保留所有权利。