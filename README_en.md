[![中文](https://img.shields.io/badge/简体中文-red?style=for-the-badge)](README.md)
[![EN](https://img.shields.io/badge/English-blue?style=for-the-badge)](README_en.md)

# ycet-design-system-governor

An Agent Skill bundled with 151 design systems that enforces a governed flow — select, confirm, apply, audit — when creating UI, redesigning pages, or reviewing design consistency.

---

## ✨ Features

| Feature | Description |
| --- | --- |
| 🎨 Bundled design system library | 151 Open Design system assets, fully offline, Python 3.10+ standard library only |
| 🧭 Transparent recommendation | Recommends candidates from a reviewable offline selection profile; never pads when nothing reliable exists |
| 🚦 Mandatory confirmation gates | System selection, conflict overrides and audit fixes all pause until explicit user approval |
| 🛡️ Evidence-based audit | Read-only static audit produces an evidence-backed compliance report with contract output (JSON Schema) |
| 🔒 Integrity validation | SHA-256 inventory + package validator ensures assets are unchanged across runs |
| 🤖 CI matrix | GitHub Actions across 3 OS × 3 Python versions (3.10 / 3.12 / 3.14) |

## 🚀 Quick Start

```powershell
git clone https://github.com/Ycet/ycet-design-system-governor.git
cd ycet-design-system-governor

# Run the full test suite (99 tests)
python -m unittest discover -s tests -p "test_*.py" -v

# Validate the skill package
python outputs/ycet-design-system-governor/scripts/validate_package.py --skill-root outputs/ycet-design-system-governor --expected-system-count 151
```

## 📖 Usage

Invoke `$ycet-design-system-governor` in any client that supports Agent Skills.

When no design system is specified, the skill recommends candidates and pauses for selection:

```text
Use $ycet-design-system-governor to create a compact analytics dashboard for technical operators.
```

When a design system is explicitly named, it proceeds after validation and conflict checks:

```text
Use $ycet-design-system-governor with the minimal design system to redesign this product page.
```

In audit mode, it delivers a report and waits for fix approval:

```text
Use $ycet-design-system-governor with the minimal design system to audit this existing frontend for design consistency.
```

## 📁 Repository Structure

| Path | Description |
| --- | --- |
| `outputs/ycet-design-system-governor/` | The deliverable skill (SKILL.md, scripts, references, schemas, assets) |
| `design-systems/` | Source directory of the 151 design systems; single source of truth for refresh |
| `tests/` | Unit, behavior-contract, stress-baseline and end-to-end tests |
| `docs/superpowers/` | Design spec and implementation plan |
| `.github/` | CI workflow and the vendored official validator snapshot |

## 🔧 Common Scripts

```powershell
# Recommend systems from a selection profile
python outputs/ycet-design-system-governor/scripts/recommend_systems.py --profile tests/fixtures/selection-profile.json --catalog outputs/ycet-design-system-governor/assets/catalog/design-systems.index.json

# Compile rules for a confirmed system
python outputs/ycet-design-system-governor/scripts/compile_rules.py --system-dir outputs/ycet-design-system-governor/assets/design-systems/minimal --output .superpowers/sdd/minimal-rules.json

# Read-only audit of a frontend project
python outputs/ycet-design-system-governor/scripts/audit_static.py --project tests/fixtures/sample-ui --bundle .superpowers/sdd/minimal-rules.json --output .superpowers/sdd/compliance-report.json
```

## ♻️ Refreshing Design System Assets

<details>
<summary>Expand for the asset refresh workflow</summary>

1. Update the root `design-systems/` directory first, and verify each directory name matches its `manifest.json` ID.
2. After confirming both source and target paths live inside this repository, fully replace `outputs/ycet-design-system-governor/assets/design-systems/` with the source directory. Never merge old directories, or deleted source files may linger.
3. Update the fixed category mappings and per-system review overrides in `scripts/build_catalog.py` for new categories or visual evidence.
4. Regenerate profiles, index and inventory:

```powershell
python outputs/ycet-design-system-governor/scripts/build_catalog.py --asset-root outputs/ycet-design-system-governor/assets/design-systems --profiles outputs/ycet-design-system-governor/assets/catalog/selection-profiles.json --bootstrap-profiles --force
python outputs/ycet-design-system-governor/scripts/build_catalog.py --asset-root outputs/ycet-design-system-governor/assets/design-systems --profiles outputs/ycet-design-system-governor/assets/catalog/selection-profiles.json --index outputs/ycet-design-system-governor/assets/catalog/design-systems.index.json --inventory outputs/ycet-design-system-governor/assets/catalog/inventory.json
```

5. Re-run the full test suite and package validation. Generate the index and inventory twice and compare SHA-256 hashes to confirm determinism.

</details>

## 🤖 CI

`.github/workflows/test.yml` runs on `windows-latest`, `macos-latest` and `ubuntu-latest` with Python 3.10, 3.12 and 3.14. The matrix runs the full test suite, the official quick-validator snapshot and the package validator. The skill itself has no third-party runtime dependencies; CI only installs PyYAML for the official validator.

## ⚠️ Known Limitations

- The selection profile is offline, human-reviewable data; it does not sync design-system updates online.
- The preview website is for visual browsing only, not a rule data source.
- Static audit only reads specified frontend text extensions and skips build directories, files over 2 MiB, and binaries; it does not execute HTML or project code.
- Visual semantics, full accessibility, cross-browser behavior and true responsive rendering still require Agent or browser tool review.
- Forward testing uses deterministic behavior-contract tests instead of independent skill-enabled Agent samples; the limitation is recorded in `tests/skill_scenarios/with-skill-results.md`.

## 📚 Documentation Index

- [Design spec](docs/superpowers/specs/2026-07-12-ui-design-system-governor-design.md)
- [Implementation plan](docs/superpowers/plans/2026-07-12-ui-design-system-governor.md)
- [Skill controller](outputs/ycet-design-system-governor/SKILL.md)
- [Forward-test substitution record](tests/skill_scenarios/with-skill-results.md)

## 📄 License

This repository currently has no `LICENSE` file and the license type is undecided; all rights are reserved until explicit terms are provided.