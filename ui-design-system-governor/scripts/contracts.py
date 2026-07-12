"""UI Design System Governor 的共享数据契约。"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Iterable


class ContractError(ValueError):
    """表示输入不符合 skill 数据契约。"""


_SCHEMA_VERSIONS = {
    "selection-profile": "ui-design-system-selection-profile/v1",
    "design-rule-bundle": "ui-design-system-design-rule-bundle/v1",
    "conflict-report": "ui-design-system-conflict-report/v1",
    "compliance-report": "ui-design-system-compliance-report/v1",
}
_TASK_MODES = {"new-design", "redesign", "audit"}
_ENFORCEMENT = {"machine-enforced", "agent-review", "explicit-prohibition", "preference"}
_DECISIONS = {"switch-system", "keep-current-system", "adjust-requirements", "other"}
_REPORT_STATES = {"review-required", "compliant", "repair-approved", "repair-complete"}
_SEVERITIES = {"critical", "high", "medium", "low"}
_VERIFICATION_STATES = {
    "verified",
    "agent-judgment",
    "degraded-unverified",
    "user-approved-deviation",
}

_SELECTION_FIELDS = (
    "schemaVersion",
    "taskMode",
    "brief",
    "industry",
    "audience",
    "productType",
    "tone",
    "theme",
    "density",
    "layoutNeeds",
    "contentNeeds",
    "componentNeeds",
    "requiredTraits",
    "excludedTraits",
    "inputSources",
    "explicitSystem",
)
_DESIGN_RULE_FIELDS = (
    "schemaVersion",
    "system",
    "files",
    "tokens",
    "rules",
    "warnings",
    "approvedDeviations",
)
_CONFLICT_FIELDS = ("schemaVersion", "system", "conflicts", "alternatives", "decisions", "status")
_COMPLIANCE_FIELDS = (
    "schemaVersion",
    "status",
    "system",
    "machineChecks",
    "agentReviews",
    "findings",
    "diffSummary",
)


def _error(path: str, message: str) -> None:
    raise ContractError(f"{path}: {message}")


def _object(value: Any, path: str = "$") -> dict[str, Any]:
    if not isinstance(value, dict):
        _error(path, "expected an object")
    return value


def _array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        _error(path, "expected an array")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _error(path, "expected a non-empty string")
    return value


def _required(value: dict[str, Any], fields: tuple[str, ...], path: str = "$") -> None:
    for field in fields:
        if field not in value:
            _error(f"{path}.{field}", "required field is missing")
    extras = sorted(set(value) - set(fields))
    if extras:
        _error(f"{path}.{extras[0]}", "unexpected field")


def _enum(value: Any, allowed: set[str], path: str) -> None:
    if value not in allowed:
        _error(path, f"expected one of {sorted(allowed)}")


def _string_array(value: Any, path: str) -> list[Any]:
    items = _array(value, path)
    for index, item in enumerate(items):
        _string(item, f"{path}[{index}]")
    return items


def _object_array(value: Any, path: str) -> list[Any]:
    items = _array(value, path)
    for index, item in enumerate(items):
        _object(item, f"{path}[{index}]")
    return items


def _version(value: dict[str, Any], contract: str) -> None:
    path = "$.schemaVersion"
    if value["schemaVersion"] != _SCHEMA_VERSIONS[contract]:
        _error(path, f"expected {_SCHEMA_VERSIONS[contract]!r}")


def _system(value: Any, path: str = "$.system") -> None:
    system = _object(value, path)
    for field in ("id", "name", "assetVersion"):
        if field not in system:
            _error(f"{path}.{field}", "required field is missing")
        _string(system[field], f"{path}.{field}")


def _relative_text(value: Any, path: str) -> None:
    text = _string(value, path)
    candidate = Path(text)
    if candidate.is_absolute() or candidate.drive or ".." in candidate.parts:
        _error(path, "expected a safe relative path")


def load_json(path: str | Path) -> Any:
    """读取 UTF-8 JSON，并把解析及 I/O 错误统一包装。"""

    try:
        text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
        raise ContractError(f"$: unable to load JSON: {exc}") from exc


def write_json(path: str | Path, value: Any) -> None:
    """以确定性 UTF-8 格式写入 JSON，并保证一个 LF 结尾。"""

    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
        target.write_text(text, encoding="utf-8", newline="\n")
    except (OSError, TypeError, ValueError) as exc:
        raise ContractError(f"$: unable to write JSON: {exc}") from exc


def normalize_terms(values: Iterable[str]) -> list[str]:
    """按输入顺序生成小写连字符术语，并稳定去重。"""

    if isinstance(values, (str, bytes)):
        _error("$", "expected an iterable of strings")
    try:
        items = list(values)
    except TypeError as exc:
        raise ContractError(f"$: expected an iterable of strings: {exc}") from exc

    result: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(items):
        if not isinstance(value, str):
            _error(f"$[{index}]", "expected a string")
        normalized = re.sub(r"(?:[^\w]|_)+", "-", value.strip().casefold()).strip("-")
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def safe_relative_path(root: str | Path, value: str | Path) -> Path:
    """解析 root 内的相对路径，并拒绝绝对路径、父级段和解析逃逸。"""

    try:
        root_path = Path(root).resolve()
        relative = Path(value)
    except (OSError, TypeError) as exc:
        raise ContractError(f"$: invalid path: {exc}") from exc

    if relative.is_absolute() or relative.drive:
        _error("$", "absolute paths are not allowed")
    if ".." in relative.parts:
        _error("$", "parent path segments are not allowed")

    try:
        resolved = (root_path / relative).resolve()
        resolved.relative_to(root_path)
    except (OSError, ValueError) as exc:
        raise ContractError(f"$: resolved path escapes root: {exc}") from exc
    return resolved


def validate_selection_profile(value: Any) -> dict[str, Any]:
    profile = _object(value)
    _required(profile, _SELECTION_FIELDS)
    _version(profile, "selection-profile")
    _enum(profile["taskMode"], _TASK_MODES, "$.taskMode")
    _string(profile["brief"], "$.brief")
    for field in _SELECTION_FIELDS[3:14]:
        _string_array(profile[field], f"$.{field}")
    _object_array(profile["inputSources"], "$.inputSources")
    if profile["explicitSystem"] is not None:
        _string(profile["explicitSystem"], "$.explicitSystem")
    return profile


def validate_design_rule_bundle(value: Any) -> dict[str, Any]:
    bundle = _object(value)
    _required(bundle, _DESIGN_RULE_FIELDS)
    _version(bundle, "design-rule-bundle")
    _system(bundle["system"])
    for index, path in enumerate(_string_array(bundle["files"], "$.files")):
        _relative_text(path, f"$.files[{index}]")
    _object_array(bundle["tokens"], "$.tokens")
    for index, rule in enumerate(_object_array(bundle["rules"], "$.rules")):
        path = f"$.rules[{index}].enforcement"
        if "enforcement" not in rule:
            _error(path, "required field is missing")
        _enum(rule["enforcement"], _ENFORCEMENT, path)
        if "source" in rule:
            _relative_text(rule["source"], f"$.rules[{index}].source")
    _array(bundle["warnings"], "$.warnings")
    _object_array(bundle["approvedDeviations"], "$.approvedDeviations")
    return bundle


def validate_conflict_report(value: Any) -> dict[str, Any]:
    report = _object(value)
    _required(report, _CONFLICT_FIELDS)
    _version(report, "conflict-report")
    _system(report["system"])
    _object_array(report["conflicts"], "$.conflicts")
    _object_array(report["alternatives"], "$.alternatives")
    for index, decision in enumerate(_string_array(report["decisions"], "$.decisions")):
        _enum(decision, _DECISIONS, f"$.decisions[{index}]")
    if report["status"] != "awaiting-user-decision":
        _error("$.status", "expected 'awaiting-user-decision'")
    return report


def validate_compliance_report(value: Any) -> dict[str, Any]:
    report = _object(value)
    _required(report, _COMPLIANCE_FIELDS)
    _version(report, "compliance-report")
    _enum(report["status"], _REPORT_STATES, "$.status")
    _system(report["system"])
    _object_array(report["machineChecks"], "$.machineChecks")
    _object_array(report["agentReviews"], "$.agentReviews")
    for index, finding in enumerate(_object_array(report["findings"], "$.findings")):
        base = f"$.findings[{index}]"
        for field in ("severity", "verificationStatus"):
            if field not in finding:
                _error(f"{base}.{field}", "required field is missing")
        _enum(finding["severity"], _SEVERITIES, f"{base}.severity")
        _enum(finding["verificationStatus"], _VERIFICATION_STATES, f"{base}.verificationStatus")
    _object(report["diffSummary"], "$.diffSummary")
    return report
