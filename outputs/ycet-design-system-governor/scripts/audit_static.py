"""以只读方式执行有限的前端静态一致性检查。"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
from typing import Any

from contracts import (
    ContractError,
    load_json,
    validate_compliance_report,
    validate_design_rule_bundle,
    write_json,
)


ALLOWED_EXTENSIONS = {".css", ".html", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
SKIP_DIRECTORIES = {".git", "node_modules", "dist", "build", ".next"}
MAX_FILE_SIZE = 2 * 1024 * 1024
TOKEN_REFERENCE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")
HEX_COLOR = re.compile(r"(?<![A-Za-z0-9_-])#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{3})(?![0-9A-Fa-f])")

SEVERITY = {
    "raw-color": "medium",
    "unknown-token": "high",
    "missing-required-token": "high",
    "unreadable-file": "low",
}


def _finding(code: str, evidence: str, reason: str, recommendation: str, *, verified: bool = True) -> dict[str, Any]:
    return {
        "severity": SEVERITY[code],
        "ruleId": code,
        "evidence": evidence,
        "reason": reason,
        "recommendation": recommendation,
        "confidence": 1.0 if verified else 0.8,
        "verificationStatus": "verified" if verified else "degraded-unverified",
    }


def _source_files(root: Path) -> list[Path]:
    files = []
    # 在遍历层直接剪枝，避免仅过滤结果却仍递归整个 node_modules。
    for current, directories, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name for name in directories
            if name not in SKIP_DIRECTORIES and not (current_path / name).is_symlink()
        )
        for name in sorted(names):
            path = current_path / name
            if path.is_symlink() or path.suffix.casefold() not in ALLOWED_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                # 无法 stat 的候选仍交给读取阶段生成明确发现。
                pass
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def scan_project(project_root: str | Path, bundle: dict[str, Any]) -> dict[str, Any]:
    """扫描允许的文本扩展名；不执行、改写或格式化目标文件。"""

    validate_design_rule_bundle(bundle)
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ContractError(f"$.project: not a directory: {root}")

    known_tokens = {token.get("name") for token in bundle["tokens"] if isinstance(token, dict) and isinstance(token.get("name"), str)}
    required_tokens = {token["name"] for token in bundle["tokens"] if isinstance(token, dict) and token.get("required") is True and isinstance(token.get("name"), str)}
    allowed_colors = {
        match.group(0).casefold()
        for token in bundle["tokens"]
        if isinstance(token, dict) and isinstance(token.get("value"), str)
        for match in HEX_COLOR.finditer(token["value"])
    }
    used_tokens: set[str] = set()
    findings: list[dict[str, Any]] = []

    for path in _source_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError) as exc:
            findings.append(_finding(
                "unreadable-file",
                f"{relative}:1: {type(exc).__name__}",
                "The file could not be decoded as UTF-8 and was not inspected.",
                "Verify the file encoding or review it manually.",
                verified=False,
            ))
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in TOKEN_REFERENCE.finditer(line):
                token = match.group(1)
                used_tokens.add(token)
                if token not in known_tokens:
                    findings.append(_finding(
                        "unknown-token",
                        f"{relative}:{line_number}: {token}",
                        "The source references a token absent from the selected design system.",
                        "Replace it with a declared token or document an approved deviation.",
                    ))
            for match in HEX_COLOR.finditer(line):
                color = match.group(0).casefold()
                if color not in allowed_colors:
                    findings.append(_finding(
                        "raw-color",
                        f"{relative}:{line_number}: {match.group(0)}",
                        "The raw color is not declared by the selected design system.",
                        "Use an existing color token or request an approved deviation.",
                    ))

    for token in sorted(required_tokens - used_tokens):
        findings.append(_finding(
            "missing-required-token",
            f"<bundle>:1: {token}",
            "A token marked required by the rule bundle is not referenced in the project.",
            "Apply the required token where the corresponding design role is implemented.",
        ))

    findings.sort(key=lambda item: (item["evidence"], item["ruleId"], item["reason"]))
    report = {
        "schemaVersion": "ui-design-system-compliance-report/v1",
        "status": "review-required",
        "system": dict(bundle["system"]),
        "machineChecks": [{"name": "safe-static-scan", "status": "verified"}],
        "agentReviews": [],
        "findings": findings,
        "diffSummary": {
            "before": f"Static audit found {len(findings)} issue(s).",
            "after": None,
            "modified": False,
        },
    }
    validate_compliance_report(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    write_json(args.output, scan_project(args.project, load_json(args.bundle)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
