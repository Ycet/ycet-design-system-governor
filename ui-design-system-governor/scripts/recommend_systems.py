"""对已校验的 SelectionProfile 执行透明、确定性的设计系统推荐评分。"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from contracts import ContractError, load_json, validate_selection_profile


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

PROFILE_TO_REQUEST = {
    "productTypes": "productType",
    "industries": "industry",
    "audiences": "audience",
    "tones": "tone",
    "layouts": "layoutNeeds",
    "contentNeeds": "contentNeeds",
    "themes": "theme",
    "densities": "density",
}
COMPLETENESS_FILES = (
    "manifest.json",
    "DESIGN.md",
    "tokens.css",
    "components.html",
    "components.manifest.json",
)


def _string_terms(value: Any, path: str) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ContractError(f"{path}: expected a string array")
    return set(value)


def _entry_profile(entry: dict[str, Any]) -> dict[str, Any]:
    profile = entry.get("profile")
    if not isinstance(profile, dict):
        raise ContractError(f"$.systems[{entry.get('id', '?')}].profile: expected an object")
    return profile


def hard_filter(profile: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """执行不可用候选的硬过滤，并返回可解释原因。"""

    offered = _entry_profile(entry)
    required = _string_terms(profile.get("requiredTraits"), "$.requiredTraits")
    excluded = _string_terms(profile.get("excludedTraits"), "$.excludedTraits")
    offered_required = _string_terms(offered.get("requiredTraits", []), "$.profile.requiredTraits")
    system_excluded = _string_terms(offered.get("excludedTraits", []), "$.profile.excludedTraits")
    all_offered = set().union(*(
        _string_terms(value, f"$.profile.{field}")
        for field, value in offered.items()
        if isinstance(value, list)
    ))

    reasons = []
    missing = sorted(required - offered_required)
    if missing:
        reasons.append(f"missing required traits: {', '.join(missing)}")
    prohibited = sorted(required & system_excluded)
    if prohibited:
        reasons.append(f"system excludes required traits: {', '.join(prohibited)}")
    conflicts = sorted(excluded & all_offered)
    if conflicts:
        reasons.append(f"matched excluded traits: {', '.join(conflicts)}")
    return {"eligible": not reasons, "reasons": reasons}


def score_system(profile: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """按活跃维度归一化到 95 分，再加最多 5 分资产完整度。"""

    offered = _entry_profile(entry)
    dimension_rows: dict[str, dict[str, Any]] = {}
    active_max = 0.0
    raw_fit = 0.0

    for profile_fields, group_weight in FIT_GROUPS:
        active_fields = [field for field in profile_fields if profile.get(PROFILE_TO_REQUEST[field])]
        if not active_fields:
            continue
        split_weight = group_weight / len(active_fields)
        for field in active_fields:
            request_field = PROFILE_TO_REQUEST[field]
            requested = _string_terms(profile[request_field], f"$.{request_field}")
            available = _string_terms(offered.get(field, []), f"$.profile.{field}")
            matched = sorted(requested & available)
            unmatched = sorted(requested - available)
            coverage = len(matched) / len(requested)
            raw_score = split_weight * coverage
            active_max += split_weight
            raw_fit += raw_score
            dimension_rows[request_field] = {
                "weight": split_weight,
                "coverage": coverage,
                "matched": matched,
                "unmatched": unmatched,
                "rawScore": raw_score,
            }

    fit_score = (raw_fit / active_max * 95.0) if active_max else 0.0
    for row in dimension_rows.values():
        row["normalizedScore"] = (row.pop("rawScore") / active_max * 95.0) if active_max else 0.0
        row["weight"] = round(row["weight"], 4)
        row["coverage"] = round(row["coverage"], 4)
        row["normalizedScore"] = round(row["normalizedScore"], 4)

    files = _string_terms(entry.get("files", []), f"$.systems[{entry.get('id', '?')}].files")
    present = [path for path in COMPLETENESS_FILES if path in files]
    missing_files = [path for path in COMPLETENESS_FILES if path not in files]
    completeness = min(float(len(present)), float(COMPLETENESS_WEIGHT))
    matched_terms = {field: row["matched"] for field, row in dimension_rows.items() if row["matched"]}
    unmatched_terms = {field: row["unmatched"] for field, row in dimension_rows.items() if row["unmatched"]}
    risks = [f"unmatched {field}: {', '.join(values)}" for field, values in sorted(unmatched_terms.items())]
    if missing_files:
        risks.append(f"missing asset files: {', '.join(missing_files)}")
    if not active_max:
        risks.append("no active fit dimensions")

    return {
        "id": entry.get("id"),
        "name": entry.get("name"),
        "score": round(fit_score + completeness, 4),
        "breakdown": {
            "fit": round(fit_score, 4),
            "completeness": round(completeness, 4),
            "dimensions": dimension_rows,
        },
        "matchedTerms": matched_terms,
        "unmatchedTerms": unmatched_terms,
        "risks": risks,
    }


def recommend(
    profile: dict[str, Any],
    catalog: dict[str, Any],
    requested_limit: int = 3,
) -> dict[str, Any]:
    """返回可靠候选；没有可靠候选时明确进入人工选择门。"""

    validate_selection_profile(profile)
    if profile["explicitSystem"] is not None:
        raise ContractError("$.explicitSystem: recommendation is only valid when no system was selected")
    if not isinstance(requested_limit, int) or isinstance(requested_limit, bool) or requested_limit < 1:
        raise ContractError("$.requestedLimit: expected a positive integer")
    if not isinstance(catalog, dict) or catalog.get("schemaVersion") != "ui-design-system-catalog/v1":
        raise ContractError("$.catalog.schemaVersion: unsupported catalog")
    entries = catalog.get("systems")
    if not isinstance(entries, list):
        raise ContractError("$.catalog.systems: expected an array")

    candidates = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ContractError("$.catalog.systems: every entry must be an object")
        gate = hard_filter(profile, entry)
        if not gate["eligible"]:
            continue
        result = score_system(profile, entry)
        if result["score"] >= RELIABLE_THRESHOLD:
            candidates.append(result)
    candidates.sort(key=lambda item: (-item["score"], item["id"]))
    limit = min(requested_limit, MAX_RECOMMENDATIONS)
    recommendations = candidates[:limit]
    return {
        "status": "awaiting-user-selection" if recommendations else "awaiting-manual-selection",
        "recommendations": recommendations,
        "previewUrl": PREVIEW_URL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args(argv)
    result = recommend(load_json(args.profile), load_json(args.catalog), args.limit)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
