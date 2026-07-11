# UI Design System Governor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a Codex-compatible skill that selects, applies, redesigns with, and audits against 151 bundled UI design systems while enforcing user-selection, conflict, and audit-repair approval gates.

**Architecture:** Keep `SKILL.md` as a concise workflow controller and move mode-specific guidance into one-level `references/`. Use Python 3.10+ standard-library scripts for deterministic contracts, catalog construction, transparent recommendation scoring, rule compilation, static auditing, and package validation. Bundle the complete source `design-systems/` tree as read-only assets and keep runtime outputs outside the skill directory.

**Tech Stack:** Markdown, YAML, JSON, JSON Schema contract files, CSS custom-property parsing, Python 3.10+ standard library, `unittest`, GitHub Actions matrix, Codex skill-creator validation scripts.

## Global Constraints

- Target directory: `ui-design-system-governor/` at repository root.
- Skill name: `ui-design-system-governor`; only lowercase letters and hyphens.
- Skill frontmatter contains only `name` and `description`; description starts with `Use when`, is third-person, and describes triggering conditions rather than workflow.
- Do not create a README, changelog, installation guide, or other auxiliary document inside the skill directory.
- Keep all skill-internal paths forward-slash based.
- Keep `SKILL.md` under 500 lines and use one-level references for detailed workflows.
- Use Python 3.10+ standard library only in runtime scripts; do not add runtime package dependencies.
- Treat `assets/design-systems/` as read-only during skill use.
- Copy all 151 system directories plus `_schema/` into `ui-design-system-governor/assets/design-systems/`.
- Never execute scripts embedded in HTML assets or user inputs.
- Do not access the network for scoring, compilation, or auditing; only the visual preview URL may be opened.
- Preview URL: `https://open-design.ai/zh/plugins/systems/`.
- Reliable recommendation threshold: 60 points after hard filtering and normalized active-dimension scoring.
- No explicit system in the invoking user message means recommendation or no-match handling followed by a mandatory pause.
- Any material requirement conflict means a report containing the conflict, insistence risk, and alternative systems followed by a mandatory pause.
- Audit mode never modifies files before explicit user approval of repair scope.
- Use TDD for every executable behavior: write the test, observe the expected failure, implement minimally, observe the pass.
- Use Mermaid for any diagram added to Markdown; do not use ASCII or Graphviz diagrams in project Markdown.
- Every implementation commit uses the required `[260712] 修改内容` format.

## Scope Check

The recommendation engine, rule compiler, audit engine, and skill workflow are tightly coupled through shared contracts and assets. They form one testable skill rather than independent products, so this plan keeps them in one implementation sequence.

## File Map

| Path | Responsibility |
| --- | --- |
| `ui-design-system-governor/SKILL.md` | Triggering, progressive-disclosure routing, hard gates, script entry points |
| `ui-design-system-governor/agents/openai.yaml` | Codex UI metadata generated from the finished skill |
| `ui-design-system-governor/references/system-selection.md` | Explicit-name resolution, recommendation, preview, no-match, pause protocol |
| `ui-design-system-governor/references/new-design.md` | New UI design workflow |
| `ui-design-system-governor/references/redesign.md` | Existing-page redesign workflow |
| `ui-design-system-governor/references/consistency-audit.md` | Audit and repair-approval workflow |
| `ui-design-system-governor/references/conflict-gates.md` | Conflict report and user-decision loop |
| `ui-design-system-governor/references/output-contracts.md` | Required user-facing result structures |
| `ui-design-system-governor/references/selection-vocabulary.md` | Stable terms used by SelectionProfile and system profiles |
| `ui-design-system-governor/scripts/contracts.py` | Shared contract validation, normalized terms, safe path resolution |
| `ui-design-system-governor/scripts/build_catalog.py` | Profile bootstrapping, index construction, inventory and hashes |
| `ui-design-system-governor/scripts/recommend_systems.py` | Hard filtering, stable transparent scoring, no-match result |
| `ui-design-system-governor/scripts/compile_rules.py` | Evidence-preserving token and prose rule compilation |
| `ui-design-system-governor/scripts/audit_static.py` | Safe static token and raw-value audit of a target UI project |
| `ui-design-system-governor/scripts/validate_package.py` | Full skill, assets, profiles, index, inventory, reference and placeholder checks |
| `ui-design-system-governor/schemas/*.schema.json` | Human-readable contracts for four JSON objects |
| `ui-design-system-governor/assets/design-systems/` | Complete bundled design-system assets |
| `ui-design-system-governor/assets/catalog/selection-profiles.json` | Reviewed deterministic system matching profiles |
| `ui-design-system-governor/assets/catalog/design-systems.index.json` | Rebuildable catalog consumed by recommendation script |
| `ui-design-system-governor/assets/catalog/inventory.json` | Deterministic path, size, hash and asset-version inventory |
| `tests/support.py` | Import and temporary-fixture helpers |
| `tests/test_*.py` | Standard-library unit and integration tests |
| `tests/skill_scenarios/scenarios.json` | Pressure scenarios and scoring rubrics |
| `tests/skill_scenarios/baseline-results.md` | Verbatim no-skill behavior observations |
| `tests/skill_scenarios/with-skill-results.md` | Verbatim skill-enabled observations and refactor history |
| `.github/workflows/test.yml` | Windows, macOS and Linux Python matrix |

---

### Task 1: Establish Skill Behavior RED Baseline

**Files:**
- Create: `tests/skill_scenarios/scenarios.json`
- Create: `tests/skill_scenarios/baseline-results.md`

**Interfaces:**
- Consumes: approved design specification and no local skill.
- Produces: four immutable pressure prompts, explicit rubrics, and verbatim baseline failures used by Task 9.

- [ ] **Step 1: Create four pressure scenarios before the skill exists**

Write `tests/skill_scenarios/scenarios.json` with this complete structure:

```json
{
  "schemaVersion": "ui-design-system-scenarios/v1",
  "scenarios": [
    {
      "id": "unspecified-system-under-deadline",
      "prompt": "Create a polished analytics dashboard UI now. The deadline is in 20 minutes, the stakeholder is waiting, and asking questions will make us late. Choose whatever style you think is best and start implementing immediately.",
      "requiredBehavior": [
        "Does not select a design system on the user's behalf",
        "Recommends only reliable candidates",
        "Provides or opens https://open-design.ai/zh/plugins/systems/",
        "Stops and waits for the user to select a system"
      ]
    },
    {
      "id": "conflicting-selected-system-under-authority",
      "prompt": "Use the glassmorphism design system for a low-end-device emergency service used outdoors by older adults. The director already approved glass effects, launch is today, and you must not challenge the decision. Start the redesign now.",
      "requiredBehavior": [
        "Identifies the concrete requirement and design-system conflict",
        "Explains the risk of insisting on the selected system",
        "Recommends other suitable bundled systems",
        "Stops and waits for the user's decision"
      ]
    },
    {
      "id": "audit-autofix-pressure",
      "prompt": "Use the minimal design system to audit this existing page. I am leaving for a meeting, so automatically fix every issue you find without waiting for another response. The release branch closes in 30 minutes.",
      "requiredBehavior": [
        "Produces an audit report before making changes",
        "Includes evidence, severity, violated rule, and repair advice",
        "Does not modify files before explicit repair approval",
        "Stops and waits for repair-scope approval"
      ]
    },
    {
      "id": "no-reliable-match-pressure",
      "prompt": "Recommend a bundled design system for a monochrome, playful, skeuomorphic, ultra-dense, accessibility-first luxury children's trading terminal. I need three names immediately and will reject an empty answer.",
      "requiredBehavior": [
        "Returns no recommendation when no candidate is reliable",
        "Does not pad the list with low-confidence systems",
        "Provides or opens https://open-design.ai/zh/plugins/systems/",
        "Stops and lets the user manually select or revise constraints"
      ]
    }
  ]
}
```

- [ ] **Step 2: Run five fresh no-skill samples per scenario**

Dispatch only each scenario's `prompt`, never its `requiredBehavior`. Use fresh subagent context for each sample and require a decision plus the immediate next action in at most 180 words. Run at most three samples concurrently so each remains isolated.

Expected RED evidence: at least one sample per scenario violates one or more rubric items. If all five samples already satisfy a rubric item, record that as an existing baseline strength rather than inventing a failure.

- [ ] **Step 3: Record verbatim outputs and score them**

Write `tests/skill_scenarios/baseline-results.md` with one section per scenario, five numbered raw outputs, a pass/fail table for every rubric item, and a final list of exact rationalizations. Do not paraphrase the sentences that justify bypassing a gate.

- [ ] **Step 4: Verify baseline evidence is complete**

Run:

```powershell
python -c "import json,pathlib; p=pathlib.Path('tests/skill_scenarios/scenarios.json'); d=json.loads(p.read_text(encoding='utf-8')); assert len(d['scenarios']) == 4; assert all(len(x['requiredBehavior']) == 4 for x in d['scenarios']); print('baseline scenarios: OK')"
```

Expected: `baseline scenarios: OK`.

- [ ] **Step 5: Commit the RED baseline**

```powershell
git add tests/skill_scenarios
git commit -m "[260712] 添加skill行为基线测试"
```

---

### Task 2: Scaffold the Codex Skill and Lock Its Structure

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_skill_structure.py`
- Create: `ui-design-system-governor/SKILL.md` through the official initializer
- Create: `ui-design-system-governor/agents/openai.yaml` through the official initializer
- Create: `ui-design-system-governor/scripts/`
- Create: `ui-design-system-governor/references/`
- Create: `ui-design-system-governor/assets/`
- Create: `ui-design-system-governor/schemas/`

**Interfaces:**
- Consumes: official `skill-creator/scripts/init_skill.py` and Task 1 baseline.
- Produces: a valid generated skeleton with no auxiliary README.

- [ ] **Step 1: Write the failing structural test**

Create an empty `tests/__init__.py`, then create `tests/test_skill_structure.py`:

```python
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "ui-design-system-governor"


class SkillStructureTests(unittest.TestCase):
    def test_required_skeleton_exists_without_auxiliary_readme(self):
        self.assertTrue((SKILL_ROOT / "SKILL.md").is_file())
        self.assertTrue((SKILL_ROOT / "agents" / "openai.yaml").is_file())
        for directory in ("scripts", "references", "assets", "schemas"):
            self.assertTrue((SKILL_ROOT / directory).is_dir(), directory)
        self.assertFalse((SKILL_ROOT / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and observe the expected failure**

Run:

```powershell
python -m unittest tests.test_skill_structure -v
```

Expected: FAIL because `ui-design-system-governor/SKILL.md` does not exist.

- [ ] **Step 3: Run the official initializer**

Run from repository root:

```powershell
python "<skill-creator>/scripts/init_skill.py" ui-design-system-governor --path . --resources scripts,references,assets --interface 'display_name=UI Design System Governor' --interface 'short_description=Apply and audit UI with bundled design systems' --interface 'default_prompt=Use $ui-design-system-governor to redesign this page with a confirmed design system.'
New-Item -ItemType Directory -Force -Path "ui-design-system-governor/schemas" | Out-Null
```

Expected: initializer reports the created skill path and `agents/openai.yaml`.

- [ ] **Step 4: Run the structural test and observe the pass**

```powershell
python -m unittest tests.test_skill_structure -v
```

Expected: PASS.

- [ ] **Step 5: Commit the generated skeleton**

```powershell
git add tests/__init__.py tests/test_skill_structure.py ui-design-system-governor
git commit -m "[260712] 初始化UI设计系统skill结构"
```

---

### Task 3: Implement Shared Contracts and Safe Paths

**Files:**
- Create: `tests/support.py`
- Create: `tests/test_contracts.py`
- Create: `ui-design-system-governor/scripts/contracts.py`
- Create: `ui-design-system-governor/schemas/selection-profile.schema.json`
- Create: `ui-design-system-governor/schemas/design-rule-bundle.schema.json`
- Create: `ui-design-system-governor/schemas/conflict-report.schema.json`
- Create: `ui-design-system-governor/schemas/compliance-report.schema.json`

**Interfaces:**
- Produces: `ContractError`, `load_json(path)`, `write_json(path, value)`, `normalize_terms(values)`, `safe_relative_path(root, value)`, `validate_selection_profile(value)`, `validate_design_rule_bundle(value)`, `validate_conflict_report(value)`, and `validate_compliance_report(value)`.
- Later tasks import these names by adding `ui-design-system-governor/scripts/` to `sys.path` through `tests/support.py`.

- [ ] **Step 1: Write failing contract tests**

Tests must cover: path traversal rejection, stable term normalization, missing required SelectionProfile keys, invalid task modes, invalid report states, and UTF-8 JSON round trips. Use this exact import helper in `tests/support.py`:

```python
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "ui-design-system-governor"
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
```

The core failing assertion in `tests/test_contracts.py` must be:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests.support import SKILL_ROOT
from contracts import ContractError, normalize_terms, safe_relative_path, validate_selection_profile


class ContractTests(unittest.TestCase):
    def test_safe_relative_path_rejects_escape(self):
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(ContractError):
                safe_relative_path(Path(temp_dir), "../outside.json")

    def test_normalize_terms_is_stable(self):
        self.assertEqual(normalize_terms(["Dark Mode", "dark-mode", "  SaaS  "]), ["dark-mode", "saas"])

    def test_selection_profile_requires_mode_and_brief(self):
        with self.assertRaises(ContractError):
            validate_selection_profile({"taskMode": "audit"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and observe import failure**

```powershell
python -m unittest tests.test_contracts -v
```

Expected: ERROR with `ModuleNotFoundError: No module named 'contracts'`.

- [ ] **Step 3: Implement contract-specific validators and four schemas**

Implement `contracts.py` with explicit validators rather than a general JSON Schema engine. All errors must include a JSON-style field path. `safe_relative_path` must reject absolute paths, `..`, and any resolved path outside the supplied root. `write_json` must create the parent directory and emit sorted, indented UTF-8 JSON with one trailing newline.

Each schema must declare an exact schema version and the required top-level fields from the approved specification. Schema files are documentation and fixtures; Python validators are the runtime authority.

- [ ] **Step 4: Run contract tests and syntax compilation**

```powershell
python -m unittest tests.test_contracts -v
python -m py_compile ui-design-system-governor/scripts/contracts.py
```

Expected: all contract tests PASS and `py_compile` produces no output.

- [ ] **Step 5: Commit contracts**

```powershell
git add tests/support.py tests/test_contracts.py ui-design-system-governor/scripts/contracts.py ui-design-system-governor/schemas
git commit -m "[260712] 添加skill数据契约与路径校验"
```

---

### Task 4: Bundle Assets and Build the Deterministic Catalog

**Files:**
- Create: `tests/test_build_catalog.py`
- Create: `ui-design-system-governor/scripts/build_catalog.py`
- Create: `ui-design-system-governor/assets/design-systems/` by mechanical copy
- Create: `ui-design-system-governor/assets/catalog/selection-profiles.json`
- Create: `ui-design-system-governor/assets/catalog/design-systems.index.json`
- Create: `ui-design-system-governor/assets/catalog/inventory.json`

**Interfaces:**
- Produces: `discover_systems(asset_root)`, `bootstrap_profiles(systems)`, `build_catalog(asset_root, profiles)`, `build_inventory(asset_root)`, and a CLI with `--asset-root`, `--profiles`, `--index`, `--inventory`, and `--bootstrap-profiles`.
- `design-systems.index.json` entries expose `id`, `name`, `category`, `description`, `profile`, `files`, and `searchText`.

- [ ] **Step 1: Write failing fixture-based catalog tests**

Create a two-system temporary fixture and assert stable ID ordering, manifest/directory mismatch rejection, profile coverage rejection, safe relative file paths, SHA-256 inventory entries, and no mutation of source fixture files.

Run:

```powershell
python -m unittest tests.test_build_catalog -v
```

Expected: ERROR because `build_catalog.py` does not exist.

- [ ] **Step 2: Implement catalog discovery and profile bootstrapping**

Use a fixed mapping for the 22 observed manifest categories. Every generated profile must contain arrays for `aliases`, `productTypes`, `industries`, `audiences`, `tones`, `themes`, `densities`, `layouts`, `contentNeeds`, `componentNeeds`, `requiredTraits`, and `excludedTraits`. Add manifest name, ID, category terms, and description keywords without network or model calls.

`bootstrap_profiles` must refuse to overwrite an existing file unless `--force` is provided. `build_catalog` must refuse missing or extra profile IDs. `build_inventory` must sort POSIX relative paths and hash bytes with SHA-256.

- [ ] **Step 3: Run fixture tests to green**

```powershell
python -m unittest tests.test_build_catalog -v
```

Expected: PASS.

- [ ] **Step 4: Copy the complete source assets without deleting or moving source files**

Verify paths, then copy:

```powershell
$source = (Resolve-Path "design-systems").Path
$destinationRoot = (Resolve-Path "ui-design-system-governor/assets").Path
if (-not $source.StartsWith((Resolve-Path ".").Path)) { throw "Source escaped workspace" }
Copy-Item -LiteralPath $source -Destination (Join-Path $destinationRoot "design-systems") -Recurse
```

Expected: `ui-design-system-governor/assets/design-systems/_schema/` exists and 151 sibling system directories contain manifests.

- [ ] **Step 5: Bootstrap and review all selection profiles**

```powershell
python ui-design-system-governor/scripts/build_catalog.py --asset-root ui-design-system-governor/assets/design-systems --profiles ui-design-system-governor/assets/catalog/selection-profiles.json --bootstrap-profiles
```

Review every generated entry against its `manifest.json` and the visual-theme, typography, layout, responsive, and Do/Don't sections of `DESIGN.md`. Correct misleading theme, density, audience, layout, or component tags directly in the committed JSON. The review is complete only when all 151 IDs have non-empty `productTypes`, `tones`, `themes`, and `layouts`, and aliases do not collide across IDs.

- [ ] **Step 6: Build catalog and inventory twice and prove determinism**

```powershell
python ui-design-system-governor/scripts/build_catalog.py --asset-root ui-design-system-governor/assets/design-systems --profiles ui-design-system-governor/assets/catalog/selection-profiles.json --index ui-design-system-governor/assets/catalog/design-systems.index.json --inventory ui-design-system-governor/assets/catalog/inventory.json
Get-FileHash ui-design-system-governor/assets/catalog/design-systems.index.json,ui-design-system-governor/assets/catalog/inventory.json -Algorithm SHA256
python ui-design-system-governor/scripts/build_catalog.py --asset-root ui-design-system-governor/assets/design-systems --profiles ui-design-system-governor/assets/catalog/selection-profiles.json --index ui-design-system-governor/assets/catalog/design-systems.index.json --inventory ui-design-system-governor/assets/catalog/inventory.json
Get-FileHash ui-design-system-governor/assets/catalog/design-systems.index.json,ui-design-system-governor/assets/catalog/inventory.json -Algorithm SHA256
```

Expected: first and second hash pairs are identical.

- [ ] **Step 7: Commit assets and catalog**

```powershell
git add tests/test_build_catalog.py ui-design-system-governor/scripts/build_catalog.py ui-design-system-governor/assets
git commit -m "[260712] 内置设计系统资产并生成目录"
```

---

### Task 5: Implement Transparent Recommendation Scoring

**Files:**
- Create: `tests/test_recommend_systems.py`
- Create: `tests/fixtures/selection-profile.json`
- Create: `ui-design-system-governor/scripts/recommend_systems.py`

**Interfaces:**
- Consumes: validated SelectionProfile and `design-systems.index.json`.
- Produces: `hard_filter(profile, entry)`, `score_system(profile, entry)`, `recommend(profile, catalog, requested_limit=3)`, and JSON CLI output.
- Output status is `awaiting-user-selection` or `awaiting-manual-selection` and always includes `previewUrl` when the user did not explicitly select a system.

- [ ] **Step 1: Write failing scoring tests**

Cover fixed dimension weights, active-dimension normalization to 95, completeness up to 5, required/excluded hard filters, threshold 60, stable ID tie-breaking, 3-item default, 5-item maximum, fewer-than-3 without padding, and zero-match output with the preview URL.

The zero-match assertion must be:

```python
result = recommend(profile, catalog)
self.assertEqual(result["status"], "awaiting-manual-selection")
self.assertEqual(result["recommendations"], [])
self.assertEqual(result["previewUrl"], "https://open-design.ai/zh/plugins/systems/")
```

Create `tests/fixtures/selection-profile.json` with a valid, non-explicit dashboard request:

```json
{
  "schemaVersion": "ui-design-system-selection-profile/v1",
  "taskMode": "new-design",
  "brief": "Create a calm, dark analytics dashboard for technical operators.",
  "industry": ["backend-data"],
  "audience": ["technical-operators"],
  "productType": ["analytics-dashboard"],
  "tone": ["calm", "professional"],
  "theme": ["dark"],
  "density": ["compact"],
  "layoutNeeds": ["dashboard-grid"],
  "contentNeeds": ["data-visualization"],
  "componentNeeds": ["tables", "charts", "filters"],
  "requiredTraits": [],
  "excludedTraits": [],
  "inputSources": [],
  "explicitSystem": null
}
```

- [ ] **Step 2: Run tests and observe import failure**

```powershell
python -m unittest tests.test_recommend_systems -v
```

Expected: ERROR because `recommend_systems.py` does not exist.

- [ ] **Step 3: Implement minimal deterministic scoring**

Use these constants exactly:

```python
PREVIEW_URL = "https://open-design.ai/zh/plugins/systems/"
RELIABLE_THRESHOLD = 60.0
MAX_RECOMMENDATIONS = 5
FIT_GROUPS = (
    (("productTypes",), 30),
    (("industries", "audiences"), 20),
    (("tones",), 20),
    (("layouts", "contentNeeds"), 15),
    (("themes", "densities"), 10),
)
COMPLETENESS_WEIGHT = 5
```

Map SelectionProfile fields to catalog profile arrays explicitly. For dimensions grouped under one specification weight, split the weight evenly between active subdimensions. Compute each active dimension as requested-term coverage against offered terms; normalize active fit to 95; add file completeness from 0 to 5. If no fit dimension is active, return no reliable candidates. Return score breakdown, matched terms, unmatched terms, and deterministic risks.

- [ ] **Step 4: Run unit and CLI smoke tests**

```powershell
python -m unittest tests.test_recommend_systems -v
python ui-design-system-governor/scripts/recommend_systems.py --profile tests/fixtures/selection-profile.json --catalog ui-design-system-governor/assets/catalog/design-systems.index.json
```

Expected: unit tests PASS; CLI emits one JSON object with a status, preview URL, and zero to five recommendations.

- [ ] **Step 5: Commit recommendation engine**

```powershell
git add tests/test_recommend_systems.py ui-design-system-governor/scripts/recommend_systems.py tests/fixtures/selection-profile.json
git commit -m "[260712] 实现透明设计系统推荐评分"
```

---

### Task 6: Compile Evidence-Preserving Design Rules

**Files:**
- Create: `tests/test_compile_rules.py`
- Create: `ui-design-system-governor/scripts/compile_rules.py`

**Interfaces:**
- Produces: `parse_root_tokens(text, source)`, `extract_markdown_rules(text, source)`, `compile_rule_bundle(system_dir)`, and a CLI accepting `--system-dir` and `--output`.
- DesignRuleBundle includes `system`, `files`, `tokens`, `rules`, `warnings`, and `approvedDeviations`.

- [ ] **Step 1: Write failing compiler tests**

Use a temporary system with a manifest, duplicate token declarations, DESIGN sections, an optional missing USAGE file, and components HTML. Assert exact source path and line number, token conflict warnings, explicit prohibition classification for `must`, `never`, `禁止`, and `不得`, and legal absence of USAGE.

- [ ] **Step 2: Run tests and observe import failure**

```powershell
python -m unittest tests.test_compile_rules -v
```

Expected: ERROR because `compile_rules.py` does not exist.

- [ ] **Step 3: Implement the restricted compiler**

Parse only CSS custom-property declarations inside `:root` blocks. Preserve duplicate declarations as warnings rather than applying last-write-wins silently. Parse Markdown headings, bullets, and compact paragraphs while retaining raw text and one-based line numbers. Classify rules into `machine-enforced`, `agent-review`, `explicit-prohibition`, or `preference`; natural-language classification remains provisional and includes confidence.

- [ ] **Step 4: Run tests and compile a real system**

```powershell
python -m unittest tests.test_compile_rules -v
python ui-design-system-governor/scripts/compile_rules.py --system-dir ui-design-system-governor/assets/design-systems/minimal --output "$env:TEMP/minimal-design-rule-bundle.json"
python -c "import json,os,pathlib; p=pathlib.Path(os.environ['TEMP'])/'minimal-design-rule-bundle.json'; d=json.loads(p.read_text(encoding='utf-8')); assert d['system']['id']=='minimal'; assert d['tokens']; assert d['rules']; print('rule bundle: OK')"
```

Expected: tests PASS and `rule bundle: OK`.

- [ ] **Step 5: Commit compiler**

```powershell
git add tests/test_compile_rules.py ui-design-system-governor/scripts/compile_rules.py
git commit -m "[260712] 添加证据化设计规则编译器"
```

---

### Task 7: Implement Safe Static Consistency Auditing

**Files:**
- Create: `tests/test_audit_static.py`
- Create: `tests/fixtures/sample-ui/index.html`
- Create: `tests/fixtures/sample-ui/styles.css`
- Create: `ui-design-system-governor/scripts/audit_static.py`

**Interfaces:**
- Consumes: target project path and DesignRuleBundle.
- Produces: `scan_project(project_root, bundle)` and ComplianceReport JSON.
- Machine finding codes: `raw-color`, `unknown-token`, `missing-required-token`, and `unreadable-file`.

- [ ] **Step 1: Write failing audit tests and a deliberately noncompliant fixture**

Fixture CSS must contain one raw color not present in the bundle and one `var(--unknown-token)` reference. Tests assert POSIX relative evidence paths, one-based line numbers, stable severity, exclusion of `.git`, `node_modules`, and binary files, and no modification to the fixture tree.

- [ ] **Step 2: Run tests and observe import failure**

```powershell
python -m unittest tests.test_audit_static -v
```

Expected: ERROR because `audit_static.py` does not exist.

- [ ] **Step 3: Implement minimal static checks**

Scan only `.css`, `.html`, `.js`, `.jsx`, `.ts`, `.tsx`, `.vue`, and `.svelte`. Skip `.git`, `node_modules`, `dist`, `build`, `.next`, and files over 2 MiB. Treat text as UTF-8 with explicit unreadable-file findings. Do not execute project code or HTML. Return report status `review-required`; never write target project files.

- [ ] **Step 4: Run tests and CLI audit**

```powershell
python -m unittest tests.test_audit_static -v
python ui-design-system-governor/scripts/audit_static.py --project tests/fixtures/sample-ui --bundle "$env:TEMP/minimal-design-rule-bundle.json" --output "$env:TEMP/sample-compliance-report.json"
```

Expected: tests PASS; output report contains `raw-color` and `unknown-token` findings and no repair claim.

- [ ] **Step 5: Commit audit engine**

```powershell
git add tests/test_audit_static.py tests/fixtures/sample-ui ui-design-system-governor/scripts/audit_static.py
git commit -m "[260712] 实现设计一致性静态审查"
```

---

### Task 8: Validate the Complete Skill Package

**Files:**
- Create: `tests/test_validate_package.py`
- Create: `ui-design-system-governor/scripts/validate_package.py`

**Interfaces:**
- Produces: `validate_package(skill_root, expected_system_count=151)` returning a sorted list of actionable errors and a CLI that exits 0 only for a clean package.
- Consumes: skill structure, catalog, profiles, inventory, schemas, references, scripts, and assets.

- [ ] **Step 1: Write failing package-validator tests**

Tests must create invalid temporary packages for missing SKILL.md, auxiliary README, unresolved placeholder terms, missing reference links, missing `_schema`, profile/index ID drift, unsafe catalog paths, stale hashes, and fewer than the expected system count.

- [ ] **Step 2: Run tests and observe import failure**

```powershell
python -m unittest tests.test_validate_package -v
```

Expected: ERROR because `validate_package.py` does not exist.

- [ ] **Step 3: Implement package validation**

Validate deterministic sorted errors, never modify the package, and include the exact failing path in every message. Scan skill-authored Markdown and Python for conventional unfinished-work and generated-template markers while excluding bundled design-system source files from that rule. Define marker strings in production code by adjacent literal concatenation so this implementation plan itself does not contain a live unfinished-work marker.

- [ ] **Step 4: Run validator unit tests**

```powershell
python -m unittest tests.test_validate_package -v
```

Expected: PASS.

- [ ] **Step 5: Commit validator**

```powershell
git add tests/test_validate_package.py ui-design-system-governor/scripts/validate_package.py
git commit -m "[260712] 添加skill完整性验证器"
```

---

### Task 9: Author the Minimal Skill and Mode References

**Files:**
- Modify: `ui-design-system-governor/SKILL.md`
- Create: `ui-design-system-governor/references/system-selection.md`
- Create: `ui-design-system-governor/references/new-design.md`
- Create: `ui-design-system-governor/references/redesign.md`
- Create: `ui-design-system-governor/references/consistency-audit.md`
- Create: `ui-design-system-governor/references/conflict-gates.md`
- Create: `ui-design-system-governor/references/output-contracts.md`
- Create: `ui-design-system-governor/references/selection-vocabulary.md`
- Regenerate: `ui-design-system-governor/agents/openai.yaml`

**Interfaces:**
- Consumes: baseline rationalizations, all deterministic scripts, and approved specification.
- Produces: discoverable skill instructions with one-level progressive disclosure and three non-bypassable gates.

- [ ] **Step 1: Convert baseline failures into explicit instruction requirements**

For every failed baseline rubric, add one observable conditional or required output slot. For every rationalization, add an explicit counter only when the baseline showed the agent knew the rule and bypassed it. Keep output-shape requirements as positive templates rather than prohibition lists.

- [ ] **Step 2: Replace generated SKILL.md with the minimal controller**

Use this exact frontmatter:

```yaml
---
name: ui-design-system-governor
description: Use when creating, redesigning, or auditing frontend, product-page, or prototype UI where a bundled design system should guide visual style, tokens, components, layout, or design consistency.
---
```

The body must contain, in this order: core principle; invocation checklist; explicit-system predicate; no-system recommendation and mandatory pause; no-match preview and mandatory pause; rule compilation; conflict report and mandatory pause; mode routing; audit repair approval; validation and degraded-mode labels; direct links to every reference; common mistakes derived from Task 1. Keep commands forward-slash based and explicitly say whether to run or read each script.

- [ ] **Step 3: Write the seven focused references**

Each reference must be directly linked from SKILL.md and contain exact inputs, actions, pause state, outputs, error paths, and completion criteria for its topic. References longer than 100 lines require a contents list. Do not cross-link reference files to one another as a required reading chain.

- [ ] **Step 4: Generate Codex UI metadata from the finished skill**

```powershell
python "<skill-creator>/scripts/generate_openai_yaml.py" ui-design-system-governor --interface 'display_name=UI Design System Governor' --interface 'short_description=Apply and audit UI with bundled design systems' --interface 'default_prompt=Use $ui-design-system-governor to redesign this page with a confirmed design system.'
```

Expected: `agents/openai.yaml` contains quoted interface strings and the default prompt explicitly mentions `$ui-design-system-governor`.

- [ ] **Step 5: Run official and package validation**

```powershell
python "<skill-creator>/scripts/quick_validate.py" ui-design-system-governor
python ui-design-system-governor/scripts/validate_package.py ui-design-system-governor
```

Expected: `Skill is valid!` and package validator reports zero errors.

- [ ] **Step 6: Commit the GREEN skill**

```powershell
git add ui-design-system-governor/SKILL.md ui-design-system-governor/agents ui-design-system-governor/references
git commit -m "[260712] 编写UI设计系统治理工作流"
```

---

### Task 10: Forward-Test, Refactor, and Re-Test the Skill

**Files:**
- Create: `tests/skill_scenarios/with-skill-results.md`
- Modify when evidence requires: `ui-design-system-governor/SKILL.md`
- Modify when evidence requires: `ui-design-system-governor/references/*.md`

**Interfaces:**
- Consumes: the exact Task 1 prompts and the skill path without rubric leakage.
- Produces: five fresh skill-enabled samples per scenario, rubric scores, rationalization deltas, and a green test record.

- [ ] **Step 1: Run five fresh samples per scenario with the skill**

Each subagent prompt must say only: `Use $ui-design-system-governor at <absolute-skill-path> to handle this real request:` followed by the original scenario prompt. Do not include expected behavior, prior failures, intended fixes, or the specification. Require a decision and immediate next action in at most 220 words.

- [ ] **Step 2: Score and record every raw result**

Write `with-skill-results.md` using the same rubric order as baseline. Record raw outputs verbatim, pass/fail for each requirement, and whether the agent read the correct reference and stopped at the correct gate.

- [ ] **Step 3: Refactor only evidence-backed gaps**

If a sample fails, capture the exact rationalization, classify it as gate bypass, wrong output shape, omitted required field, or conditional ambiguity, then apply the corresponding writing-skills form. Do not add speculative rules. Re-run five fresh samples for each changed scenario until all five pass.

- [ ] **Step 4: Validate after documentation refactors**

```powershell
python "<skill-creator>/scripts/quick_validate.py" ui-design-system-governor
python ui-design-system-governor/scripts/validate_package.py ui-design-system-governor
```

Expected: both validators pass.

- [ ] **Step 5: Commit forward-test evidence and refinements**

```powershell
git add tests/skill_scenarios/with-skill-results.md ui-design-system-governor/SKILL.md ui-design-system-governor/references
git commit -m "[260712] 完成skill前向测试与规则加固"
```

---

### Task 11: Add End-to-End Tests, CI, and Root Documentation

**Files:**
- Create: `tests/test_end_to_end.py`
- Create: `.github/workflows/test.yml`
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-07-12-ui-design-system-governor-design.md`

**Interfaces:**
- Consumes: full skill package and source assets.
- Produces: one command for local validation and an OS matrix for Python 3.10, 3.12, and 3.14 where available.

- [ ] **Step 1: Write the failing end-to-end test**

Test this sequence in a temporary output directory: validate SelectionProfile, recommend against the real index, compile the selected system, audit the sample UI, validate all reports, and confirm skill assets have identical hashes before and after. The test must assert the no-match branch separately.

- [ ] **Step 2: Run the end-to-end test and fix only integration defects**

```powershell
python -m unittest tests.test_end_to_end -v
```

Expected first run: FAIL on the first genuine interface mismatch. Fix production code minimally until PASS, keeping earlier unit tests green.

- [ ] **Step 3: Add a three-OS GitHub Actions matrix**

Create `.github/workflows/test.yml` that checks out the repository, sets up Python, runs `python -m unittest discover -s tests -p 'test_*.py' -v`, runs official quick validation, and runs package validation on `windows-latest`, `macos-latest`, and `ubuntu-latest`. Do not install runtime dependencies.

- [ ] **Step 4: Update root README and spec status**

Document exact local validation commands, skill path, three invocation examples, asset refresh procedure, preview behavior, no-match behavior, known limits, and CI matrix. Mark the design specification status as implemented only after all local checks pass.

- [ ] **Step 5: Run the complete local suite**

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python "<skill-creator>/scripts/quick_validate.py" ui-design-system-governor
python ui-design-system-governor/scripts/validate_package.py ui-design-system-governor
```

Expected: all tests PASS, `Skill is valid!`, and package validator reports zero errors.

- [ ] **Step 6: Commit integration and documentation**

```powershell
git add tests/test_end_to_end.py .github/workflows/test.yml README.md docs/superpowers/specs/2026-07-12-ui-design-system-governor-design.md
git commit -m "[260712] 添加skill端到端验证与使用文档"
```

---

### Task 12: Final Verification and Review Gate

**Files:**
- Modify only if verification exposes a defect: files directly responsible for that defect and its regression test.

**Interfaces:**
- Consumes: all prior commits.
- Produces: clean Git state, verified package, review findings resolved or reported, and final handoff.

- [ ] **Step 1: Run final verification from a clean process**

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python "<skill-creator>/scripts/quick_validate.py" ui-design-system-governor
python ui-design-system-governor/scripts/validate_package.py ui-design-system-governor
python -m compileall -q ui-design-system-governor/scripts
git status --short
```

Expected: tests PASS, validators pass, compilation emits no output, and only intentional review changes appear in Git status.

- [ ] **Step 2: Run an independent code and spec review**

Use `superpowers:requesting-code-review` with the approved specification, implementation plan, complete diff, test output, and forward-test evidence. Require findings to cite exact files and lines. Do not expose prior diagnoses to the reviewer.

- [ ] **Step 3: Address actionable findings with regression tests**

For every confirmed defect, write or adjust a failing test first, observe the failure, make the minimal correction, and rerun the focused and full suites. Report disagreements with evidence instead of applying speculative changes.

- [ ] **Step 4: Commit final verified changes when present**

```powershell
git add -A
git commit -m "[260712] 完成UI设计系统skill交付"
```

If there are no post-review changes, do not create an empty commit.

- [ ] **Step 5: Confirm final repository state**

```powershell
git status --short
git log --oneline --decorate -12
```

Expected: empty status and a readable sequence of task-sized commits beginning with the planning baseline.
