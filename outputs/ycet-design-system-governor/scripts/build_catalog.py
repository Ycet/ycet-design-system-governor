"""构建设计系统目录、选择画像与字节级资产清单。"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

from contracts import ContractError, load_json, normalize_terms, safe_relative_path, write_json


PROFILE_FIELDS = (
    "aliases",
    "productTypes",
    "industries",
    "audiences",
    "tones",
    "themes",
    "densities",
    "layouts",
    "contentNeeds",
    "componentNeeds",
    "requiredTraits",
    "excludedTraits",
)

# 这些映射固定覆盖当前资产中的 22 个类别，避免运行时依赖模型或网络。
CATEGORY_PROFILES: dict[str, dict[str, list[str]]] = {
    "AI & LLM": {"productTypes": ["ai-product"], "industries": ["ai-llm"], "audiences": ["knowledge-workers"], "tones": ["intelligent", "professional"], "themes": ["modern"], "densities": ["comfortable"], "layouts": ["workspace"], "contentNeeds": ["generated-content"], "componentNeeds": ["prompt-inputs", "conversations"]},
    "Productivity & SaaS": {"productTypes": ["saas-workspace"], "industries": ["productivity-saas"], "audiences": ["knowledge-workers"], "tones": ["clear", "professional"], "themes": ["modern"], "densities": ["compact"], "layouts": ["application-shell"], "contentNeeds": ["structured-content"], "componentNeeds": ["forms", "tables", "navigation"]},
    "Media & Consumer": {"productTypes": ["consumer-app"], "industries": ["media-consumer"], "audiences": ["consumers"], "tones": ["engaging"], "themes": ["visual"], "densities": ["comfortable"], "layouts": ["content-feed"], "contentNeeds": ["media"], "componentNeeds": ["cards", "carousels"]},
    "Creative & Artistic": {"productTypes": ["creative-experience"], "industries": ["creative"], "audiences": ["creators"], "tones": ["expressive"], "themes": ["artistic"], "densities": ["spacious"], "layouts": ["visual-canvas"], "contentNeeds": ["portfolio-media"], "componentNeeds": ["galleries"]},
    "Modern & Minimal": {"productTypes": ["marketing-site"], "industries": ["general"], "audiences": ["general-users"], "tones": ["calm", "refined"], "themes": ["minimal"], "densities": ["spacious"], "layouts": ["content-sections"], "contentNeeds": ["editorial-content"], "componentNeeds": ["cards", "navigation"]},
    "Professional & Corporate": {"productTypes": ["enterprise-product"], "industries": ["corporate"], "audiences": ["business-users"], "tones": ["professional", "trustworthy"], "themes": ["corporate"], "densities": ["comfortable"], "layouts": ["application-shell"], "contentNeeds": ["business-content"], "componentNeeds": ["forms", "tables"]},
    "Developer Tools": {"productTypes": ["developer-tool"], "industries": ["developer-tools"], "audiences": ["developers"], "tones": ["technical", "focused"], "themes": ["dark"], "densities": ["compact"], "layouts": ["workspace"], "contentNeeds": ["code", "logs"], "componentNeeds": ["command-inputs", "tables"]},
    "Backend & Data": {"productTypes": ["analytics-dashboard"], "industries": ["backend-data"], "audiences": ["technical-operators"], "tones": ["calm", "professional"], "themes": ["dark"], "densities": ["compact"], "layouts": ["dashboard-grid"], "contentNeeds": ["data-visualization"], "componentNeeds": ["tables", "charts", "filters"]},
    "Bold & Expressive": {"productTypes": ["campaign-site"], "industries": ["marketing"], "audiences": ["consumers"], "tones": ["bold", "expressive"], "themes": ["high-contrast"], "densities": ["comfortable"], "layouts": ["hero-sections"], "contentNeeds": ["promotional-content"], "componentNeeds": ["calls-to-action"]},
    "Themed & Unique": {"productTypes": ["themed-experience"], "industries": ["general"], "audiences": ["enthusiasts"], "tones": ["distinctive"], "themes": ["themed"], "densities": ["comfortable"], "layouts": ["content-sections"], "contentNeeds": ["storytelling"], "componentNeeds": ["cards"]},
    "Automotive": {"productTypes": ["automotive-product"], "industries": ["automotive"], "audiences": ["drivers", "shoppers"], "tones": ["premium", "technical"], "themes": ["dark"], "densities": ["comfortable"], "layouts": ["product-showcase"], "contentNeeds": ["product-specifications"], "componentNeeds": ["galleries", "comparison-tables"]},
    "Design & Creative": {"productTypes": ["design-tool"], "industries": ["design-creative"], "audiences": ["designers"], "tones": ["creative", "clear"], "themes": ["modern"], "densities": ["compact"], "layouts": ["workspace"], "contentNeeds": ["visual-assets"], "componentNeeds": ["toolbars", "panels"]},
    "Fintech & Crypto": {"productTypes": ["financial-dashboard"], "industries": ["fintech-crypto"], "audiences": ["financial-users"], "tones": ["trustworthy", "precise"], "themes": ["dark"], "densities": ["compact"], "layouts": ["dashboard-grid"], "contentNeeds": ["financial-data"], "componentNeeds": ["tables", "charts", "transaction-forms"]},
    "Morphism & Effects": {"productTypes": ["visual-interface"], "industries": ["general"], "audiences": ["general-users"], "tones": ["polished"], "themes": ["morphism"], "densities": ["comfortable"], "layouts": ["layered-cards"], "contentNeeds": ["visual-content"], "componentNeeds": ["cards", "controls"]},
    "E-Commerce & Retail": {"productTypes": ["e-commerce"], "industries": ["e-commerce-retail"], "audiences": ["shoppers"], "tones": ["commercial", "friendly"], "themes": ["light"], "densities": ["comfortable"], "layouts": ["catalog-grid"], "contentNeeds": ["product-content"], "componentNeeds": ["product-cards", "filters", "checkout-forms"]},
    "Layout & Structure": {"productTypes": ["content-platform"], "industries": ["general"], "audiences": ["general-users"], "tones": ["structured"], "themes": ["neutral"], "densities": ["comfortable"], "layouts": ["structured-grid"], "contentNeeds": ["mixed-content"], "componentNeeds": ["navigation", "cards"]},
    "Retro & Nostalgic": {"productTypes": ["themed-experience"], "industries": ["entertainment"], "audiences": ["enthusiasts"], "tones": ["nostalgic", "playful"], "themes": ["retro"], "densities": ["comfortable"], "layouts": ["content-sections"], "contentNeeds": ["storytelling"], "componentNeeds": ["cards", "badges"]},
    "Starter": {"productTypes": ["starter-interface"], "industries": ["general"], "audiences": ["general-users"], "tones": ["neutral"], "themes": ["light"], "densities": ["comfortable"], "layouts": ["content-sections"], "contentNeeds": ["general-content"], "componentNeeds": ["forms", "navigation"]},
    "Editorial / Personal / Publication": {"productTypes": ["publication"], "industries": ["publishing"], "audiences": ["readers"], "tones": ["editorial", "personal"], "themes": ["print-inspired"], "densities": ["spacious"], "layouts": ["article-layout"], "contentNeeds": ["long-form-content"], "componentNeeds": ["article-navigation"]},
    "Social & Messaging": {"productTypes": ["social-app"], "industries": ["social-messaging"], "audiences": ["communities"], "tones": ["friendly", "conversational"], "themes": ["modern"], "densities": ["compact"], "layouts": ["conversation-layout"], "contentNeeds": ["user-generated-content"], "componentNeeds": ["messages", "feeds", "composer"]},
    "Editorial · Studio": {"productTypes": ["studio-portfolio"], "industries": ["creative-studio"], "audiences": ["clients", "creators"], "tones": ["editorial", "refined"], "themes": ["print-inspired"], "densities": ["spacious"], "layouts": ["portfolio-grid"], "contentNeeds": ["case-studies"], "componentNeeds": ["galleries", "project-cards"]},
    "Editorial & Print": {"productTypes": ["publication"], "industries": ["publishing"], "audiences": ["readers"], "tones": ["editorial", "authoritative"], "themes": ["print-inspired"], "densities": ["spacious"], "layouts": ["article-layout"], "contentNeeds": ["long-form-content"], "componentNeeds": ["article-navigation"]},
}

KEYWORDS = {
    "dashboard": (("productTypes", "analytics-dashboard"), ("layouts", "dashboard-grid")),
    "dark": (("themes", "dark"),),
    "light": (("themes", "light"),),
    "compact": (("densities", "compact"),),
    "dense": (("densities", "compact"),),
    "spacious": (("densities", "spacious"),),
    "table": (("componentNeeds", "tables"),),
    "chart": (("componentNeeds", "charts"), ("contentNeeds", "data-visualization")),
    "mobile": (("layouts", "mobile-first"),),
    "responsive": (("requiredTraits", "responsive"),),
    "accessible": (("requiredTraits", "accessible"),),
    "minimal": (("tones", "calm"), ("themes", "minimal")),
    "playful": (("tones", "playful"),),
    "serif": (("themes", "print-inspired"),),
}

# 对逐份 DESIGN.md 复核后发现的歧义进行显式修正，主要消除配色示例和反例造成的误标签。
SYSTEM_PROFILE_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "cisco": {"themes": ["dark"]},
    "clickhouse": {"themes": ["dark", "high-contrast"]},
    "miro": {"themes": ["light", "modern"], "densities": ["spacious"]},
    "openai": {"themes": ["light", "minimal", "print-inspired"], "densities": ["spacious", "comfortable"]},
    "runwayml": {"themes": ["dark", "minimal", "cinematic"]},
    "sanity": {"themes": ["dark", "minimal"]},
    "sentry": {"themes": ["dark"]},
    "spacex": {"productTypes": ["marketing-site"], "themes": ["dark", "minimal", "cinematic"], "densities": ["spacious"], "layouts": ["full-viewport-showcase"]},
    "supabase": {"themes": ["dark", "minimal"]},
    "warp": {"themes": ["dark", "minimal", "print-inspired"], "densities": ["spacious"], "layouts": ["product-showcase"]},
    "webflow": {"themes": ["light", "modern"], "layouts": ["product-showcase", "workspace"]},
    "wired": {"productTypes": ["publication"], "themes": ["light", "print-inspired"], "densities": ["compact"], "layouts": ["editorial-grid", "content-feed"]},
    "xiaohongshu": {"productTypes": ["social-app"], "themes": ["light", "minimal"], "layouts": ["masonry-feed"], "componentNeeds": ["cards", "feeds", "composer"]},
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _manifest_string(manifest: dict[str, Any], field: str, path: Path) -> str:
    value = manifest.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{path.as_posix()}: manifest field {field!r} must be a non-empty string")
    return value


def discover_systems(asset_root: str | Path) -> list[dict[str, Any]]:
    """发现并验证系统目录；结果按系统 ID 稳定排序。"""

    root = Path(asset_root).resolve()
    if not root.is_dir():
        raise ContractError(f"$: asset root is not a directory: {root}")
    systems: list[dict[str, Any]] = []
    for directory in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda p: p.name):
        if directory.name == "_schema":
            continue
        manifest_path = directory / "manifest.json"
        if not manifest_path.is_file():
            raise ContractError(f"{directory.name}: manifest.json is missing")
        manifest = load_json(manifest_path)
        if not isinstance(manifest, dict):
            raise ContractError(f"{directory.name}/manifest.json: expected an object")
        system_id = _manifest_string(manifest, "id", manifest_path)
        if system_id != directory.name:
            raise ContractError(f"{directory.name}: manifest id {system_id!r} does not match directory")
        name = _manifest_string(manifest, "name", manifest_path)
        category = _manifest_string(manifest, "category", manifest_path)
        description = _manifest_string(manifest, "description", manifest_path)
        files: list[str] = []
        for file_path in sorted((p for p in directory.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
            file_path.resolve().relative_to(directory.resolve())
            files.append(file_path.relative_to(directory).as_posix())
        design_path = directory / "DESIGN.md"
        design_text = design_path.read_text(encoding="utf-8") if design_path.is_file() else ""
        systems.append({
            "id": system_id,
            "name": name,
            "category": category,
            "description": description,
            "files": files,
            "designText": design_text,
        })
    systems.sort(key=lambda item: item["id"])
    return systems


def bootstrap_profiles(systems: list[dict[str, Any]]) -> dict[str, Any]:
    """用固定类别映射和可解释关键词生成选择画像。"""

    candidates: dict[str, set[str]] = {}
    for system in systems:
        candidates[system["id"]] = {_slug(system["id"]), _slug(system["name"])} - {""}
    counts = Counter(alias for values in candidates.values() for alias in values)

    profiles = []
    for system in sorted(systems, key=lambda item: item["id"]):
        mapped = CATEGORY_PROFILES.get(system["category"], CATEGORY_PROFILES["Starter"])
        profile: dict[str, Any] = {"id": system["id"]}
        profile["aliases"] = sorted(alias for alias in candidates[system["id"]] if counts[alias] == 1)
        for field in PROFILE_FIELDS[1:]:
            profile[field] = list(mapped.get(field, []))

        # 只从视觉主题章节补标签，避免把 Do/Don't 中的反例误判为系统特征。
        visual_section = system["designText"].split("## 2.", 1)[0]
        searchable = " ".join((system["name"], system["category"], system["description"], visual_section)).casefold()
        for keyword, additions in KEYWORDS.items():
            if keyword in searchable:
                for field, value in additions:
                    profile[field].append(value)
        profile["tones"].extend(normalize_terms([system["category"]]))
        for field, values in SYSTEM_PROFILE_OVERRIDES.get(system["id"], {}).items():
            profile[field] = list(values)
        for field in PROFILE_FIELDS:
            profile[field] = normalize_terms(profile[field])
        for field in ("productTypes", "tones", "themes", "layouts"):
            if not profile[field]:
                raise ContractError(f"$.profiles[{system['id']}].{field}: must not be empty")
        profiles.append(profile)
    return {"schemaVersion": "ui-design-system-selection-profiles/v1", "profiles": profiles}


def _profiles_by_id(profiles: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(profiles, dict) or profiles.get("schemaVersion") != "ui-design-system-selection-profiles/v1":
        raise ContractError("$.schemaVersion: invalid selection profile catalog")
    values = profiles.get("profiles")
    if not isinstance(values, list):
        raise ContractError("$.profiles: expected an array")
    result: dict[str, dict[str, Any]] = {}
    aliases: set[str] = set()
    for index, profile in enumerate(values):
        if not isinstance(profile, dict) or not isinstance(profile.get("id"), str):
            raise ContractError(f"$.profiles[{index}].id: expected a string")
        system_id = profile["id"]
        if system_id in result:
            raise ContractError(f"$.profiles[{index}].id: duplicate profile id {system_id}")
        for field in PROFILE_FIELDS:
            if not isinstance(profile.get(field), list) or not all(isinstance(item, str) for item in profile[field]):
                raise ContractError(f"$.profiles[{index}].{field}: expected a string array")
        for alias in profile["aliases"]:
            if alias in aliases:
                raise ContractError(f"$.profiles[{index}].aliases: alias collision {alias}")
            aliases.add(alias)
        result[system_id] = profile
    return result


def build_catalog(asset_root: str | Path, profiles: dict[str, Any]) -> dict[str, Any]:
    """组合资产清单与人工可修订画像，拒绝画像覆盖不完整。"""

    systems = discover_systems(asset_root)
    by_id = _profiles_by_id(profiles)
    system_ids = {system["id"] for system in systems}
    profile_ids = set(by_id)
    if system_ids != profile_ids:
        missing = sorted(system_ids - profile_ids)
        extra = sorted(profile_ids - system_ids)
        raise ContractError(f"$: profile coverage mismatch; missing={missing}, extra={extra}")

    entries = []
    for system in systems:
        profile = by_id[system["id"]]
        public_profile = {field: profile[field] for field in PROFILE_FIELDS}
        search_parts = [system["id"], system["name"], system["category"], system["description"]]
        search_parts.extend(term for field in PROFILE_FIELDS for term in public_profile[field])
        entries.append({
            "id": system["id"],
            "name": system["name"],
            "category": system["category"],
            "description": system["description"],
            "profile": public_profile,
            "files": sorted(system["files"]),
            "searchText": " ".join(dict.fromkeys(part.casefold() for part in search_parts if part)),
        })
    return {"schemaVersion": "ui-design-system-catalog/v1", "systems": entries}


def build_inventory(asset_root: str | Path) -> dict[str, Any]:
    """按 POSIX 相对路径输出确定性的 SHA-256 字节清单。"""

    root = Path(asset_root).resolve()
    if not root.is_dir():
        raise ContractError(f"$: asset root is not a directory: {root}")
    entries = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        safe_relative_path(root, relative)
        data = path.read_bytes()
        entries.append({"path": relative, "size": len(data), "sha256": sha256(data).hexdigest()})
    return {"schemaVersion": "ui-design-system-inventory/v1", "files": entries}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", required=True)
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--index")
    parser.add_argument("--inventory")
    parser.add_argument("--bootstrap-profiles", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    asset_root = Path(args.asset_root)
    profiles_path = Path(args.profiles)
    if args.bootstrap_profiles:
        if profiles_path.exists() and not args.force:
            raise ContractError(f"$: refusing to overwrite existing profiles: {profiles_path}")
        write_json(profiles_path, bootstrap_profiles(discover_systems(asset_root)))

    if args.index:
        write_json(args.index, build_catalog(asset_root, load_json(profiles_path)))
    if args.inventory:
        write_json(args.inventory, build_inventory(asset_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
