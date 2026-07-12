"""验证 UI Design System Governor skill 包的结构、索引与资产完整性。"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import sys
from typing import Any

from contracts import ContractError, load_json, safe_relative_path


REQUIRED_REFERENCES = (
    "system-selection.md",
    "new-design.md",
    "redesign.md",
    "consistency-audit.md",
    "conflict-gates.md",
    "output-contracts.md",
    "selection-vocabulary.md",
)
REQUIRED_SCRIPTS = (
    "contracts.py",
    "build_catalog.py",
    "recommend_systems.py",
    "compile_rules.py",
    "audit_static.py",
    "validate_package.py",
)
REQUIRED_SCHEMAS = (
    "selection-profile.schema.json",
    "design-rule-bundle.schema.json",
    "conflict-report.schema.json",
    "compliance-report.schema.json",
)

# 相邻字符串让验证器自身源码不会包含一个可被自己命中的完整标记。
UNFINISHED_MARKERS = (
    "TO" "DO",
    "FIX" "ME",
    "T" "BD",
    "<" "place" "holder" ">",
    "replace" "-me",
)


def _relative(skill_root: Path, path: Path) -> str:
    try:
        return path.relative_to(skill_root).as_posix()
    except ValueError:
        return path.as_posix()


def _load_document(skill_root: Path, path: Path, errors: list[str]) -> Any | None:
    label = _relative(skill_root, path)
    if not path.is_file():
        errors.append(f"{label}: required JSON file is missing")
        return None
    try:
        return load_json(path)
    except ContractError as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return None


def _ids(document: Any, field: str, path: str, errors: list[str]) -> set[str]:
    if not isinstance(document, dict) or not isinstance(document.get(field), list):
        errors.append(f"{path}: expected an object containing array {field!r}")
        return set()
    result: set[str] = set()
    for index, item in enumerate(document[field]):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            errors.append(f"{path}: {field}[{index}].id must be a non-empty string")
            continue
        if item["id"] in result:
            errors.append(f"{path}: duplicate ID {item['id']!r}")
        result.add(item["id"])
    return result


def _validate_authored_sources(skill_root: Path, errors: list[str]) -> None:
    files = [skill_root / "SKILL.md"]
    files.extend((skill_root / "references").glob("*.md") if (skill_root / "references").is_dir() else [])
    files.extend((skill_root / "scripts").glob("*.py") if (skill_root / "scripts").is_dir() else [])
    for path in sorted((item for item in files if item.is_file()), key=lambda item: item.as_posix()):
        label = _relative(skill_root, path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{label}: unreadable authored source: {exc}")
            continue
        folded = text.casefold()
        for marker in UNFINISHED_MARKERS:
            if marker.casefold() in folded:
                errors.append(f"{label}: unresolved unfinished marker {marker!r}")


def _validate_inventory(skill_root: Path, asset_root: Path, inventory: Any, errors: list[str]) -> None:
    label = "assets/catalog/inventory.json"
    if not isinstance(inventory, dict) or not isinstance(inventory.get("files"), list):
        errors.append(f"{label}: expected an object containing array 'files'")
        return
    recorded: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(inventory["files"]):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append(f"{label}: files[{index}].path must be a string")
            continue
        relative = item["path"]
        try:
            path = safe_relative_path(asset_root, relative)
        except ContractError:
            errors.append(f"{label}: files[{index}] has unsafe path {relative!r}")
            continue
        if relative in recorded:
            errors.append(f"{label}: duplicate inventory path {relative!r}")
        recorded[relative] = item
        if not path.is_file():
            errors.append(f"{label}: recorded file is missing: {relative}")
            continue
        data = path.read_bytes()
        if item.get("size") != len(data):
            errors.append(f"{label}: stale size for {relative}")
        if item.get("sha256") != sha256(data).hexdigest():
            errors.append(f"{label}: stale hash for {relative}")

    actual = {
        path.relative_to(asset_root).as_posix()
        for path in asset_root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    for relative in sorted(actual - set(recorded)):
        errors.append(f"{label}: asset missing from inventory: {relative}")
    for relative in sorted(set(recorded) - actual):
        errors.append(f"{label}: inventory path has no asset: {relative}")


def validate_package(skill_root: str | Path, expected_system_count: int = 151) -> list[str]:
    """返回排序后的可执行错误；验证过程永不修改 skill 包。"""

    root = Path(skill_root).resolve()
    errors: list[str] = []
    if not root.is_dir():
        return [f"{root.as_posix()}: skill root is not a directory"]

    for relative in ("SKILL.md", "agents/openai.yaml"):
        if not (root / relative).is_file():
            errors.append(f"{relative}: required file is missing")
    if (root / "README.md").exists():
        errors.append("README.md: auxiliary README is not allowed at skill root")
    for relative in ("scripts", "references", "schemas", "assets"):
        if not (root / relative).is_dir():
            errors.append(f"{relative}: required directory is missing")

    skill_text = ""
    if (root / "SKILL.md").is_file():
        try:
            skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"SKILL.md: unreadable: {exc}")
    for name in REQUIRED_REFERENCES:
        path = root / "references" / name
        if not path.is_file():
            errors.append(f"references/{name}: required reference is missing")
        if f"references/{name}" not in skill_text:
            errors.append(f"SKILL.md: missing link to references/{name}")
    for name in REQUIRED_SCRIPTS:
        if not (root / "scripts" / name).is_file():
            errors.append(f"scripts/{name}: required script is missing")
    for name in REQUIRED_SCHEMAS:
        path = root / "schemas" / name
        _load_document(root, path, errors)
    _validate_authored_sources(root, errors)

    asset_root = root / "assets" / "design-systems"
    if not asset_root.is_dir():
        errors.append("assets/design-systems: bundled asset root is missing")
        system_ids: set[str] = set()
    else:
        if not (asset_root / "_schema").is_dir():
            errors.append("assets/design-systems/_schema: required schema directory is missing")
        system_ids = set()
        for directory in sorted((item for item in asset_root.iterdir() if item.is_dir() and item.name != "_schema"), key=lambda item: item.name):
            manifest_path = directory / "manifest.json"
            manifest = _load_document(root, manifest_path, errors)
            if isinstance(manifest, dict) and manifest.get("id") != directory.name:
                errors.append(f"assets/design-systems/{directory.name}/manifest.json: ID does not match directory")
            system_ids.add(directory.name)

    catalog_path = root / "assets" / "catalog" / "design-systems.index.json"
    profiles_path = root / "assets" / "catalog" / "selection-profiles.json"
    inventory_path = root / "assets" / "catalog" / "inventory.json"
    catalog = _load_document(root, catalog_path, errors)
    profiles = _load_document(root, profiles_path, errors)
    inventory = _load_document(root, inventory_path, errors)
    catalog_ids = _ids(catalog, "systems", "assets/catalog/design-systems.index.json", errors) if catalog is not None else set()
    profile_ids = _ids(profiles, "profiles", "assets/catalog/selection-profiles.json", errors) if profiles is not None else set()

    if catalog_ids != profile_ids:
        errors.append(f"assets/catalog/selection-profiles.json: ID drift from index; missing={sorted(catalog_ids-profile_ids)}, extra={sorted(profile_ids-catalog_ids)}")
    if system_ids != catalog_ids:
        errors.append(f"assets/catalog/design-systems.index.json: ID drift from assets; missing={sorted(system_ids-catalog_ids)}, extra={sorted(catalog_ids-system_ids)}")
    for label, values in (("assets/design-systems", system_ids), ("assets/catalog/design-systems.index.json", catalog_ids), ("assets/catalog/selection-profiles.json", profile_ids)):
        if len(values) != expected_system_count:
            errors.append(f"{label}: expected {expected_system_count} systems, found {len(values)}")

    if isinstance(catalog, dict) and isinstance(catalog.get("systems"), list):
        for index, entry in enumerate(catalog["systems"]):
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("files"), list):
                continue
            system_root = asset_root / entry["id"]
            for file_index, relative in enumerate(entry["files"]):
                if not isinstance(relative, str):
                    errors.append(f"assets/catalog/design-systems.index.json: systems[{index}].files[{file_index}] must be a string")
                    continue
                try:
                    path = safe_relative_path(system_root, relative)
                except ContractError:
                    errors.append(f"assets/catalog/design-systems.index.json: unsafe path {relative!r} for {entry['id']}")
                    continue
                if not path.is_file():
                    errors.append(f"assets/catalog/design-systems.index.json: missing file {entry['id']}/{relative}")

    if inventory is not None and asset_root.is_dir():
        _validate_inventory(root, asset_root, inventory, errors)
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--expected-system-count", type=int, default=151)
    args = parser.parse_args(argv)
    errors = validate_package(args.skill_root, args.expected_system_count)
    if errors:
        for error in errors:
            sys.stderr.write(error + "\n")
        return 1
    sys.stdout.write("skill package: OK\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
