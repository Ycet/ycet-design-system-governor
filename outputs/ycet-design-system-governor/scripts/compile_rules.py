"""把设计系统原始文件编译为保留证据位置的 DesignRuleBundle。"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

from contracts import (
    ContractError,
    load_json,
    safe_relative_path,
    validate_design_rule_bundle,
    write_json,
)


ROOT_BLOCK = re.compile(r":root\s*\{(?P<body>.*?)\}", re.DOTALL | re.IGNORECASE)
CUSTOM_PROPERTY = re.compile(r"(?P<name>--[A-Za-z0-9_-]+)\s*:\s*(?P<value>[^;{}]+);", re.DOTALL)
HEADING = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?P<text>.+?)\s*$")
EXPLICIT = re.compile(r"\b(?:must|never)\b|必须|禁止|不得", re.IGNORECASE)
AGENT_REVIEW = re.compile(r"\b(?:should|avoid|use|keep|prefer)\b|应当|应该|避免|使用|保持|优先", re.IGNORECASE)
TOKEN_REFERENCE = re.compile(r"--[A-Za-z0-9_-]+")


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "general"


def parse_root_tokens(text: str, source: str) -> list[dict[str, Any]]:
    """只读取 :root 块中的 CSS 自定义属性，并保留重复声明。"""

    tokens = []
    for block in ROOT_BLOCK.finditer(text):
        body = block.group("body")
        body_start = block.start("body")
        for declaration in CUSTOM_PROPERTY.finditer(body):
            tokens.append({
                "name": declaration.group("name"),
                "value": declaration.group("value").strip(),
                "source": source,
                "location": {"line": _line_number(text, body_start + declaration.start())},
            })
    return tokens


def _classify(text: str) -> tuple[str, float, list[str]]:
    if EXPLICIT.search(text):
        return "explicit-prohibition", 0.95, ["provisional-natural-language-classification"]
    if TOKEN_REFERENCE.search(text):
        return "machine-enforced", 0.9, ["verify-token-contract-before-enforcement"]
    if AGENT_REVIEW.search(text):
        return "agent-review", 0.75, ["provisional-natural-language-classification"]
    return "preference", 0.6, ["provisional-natural-language-classification"]


def _make_rule(raw: str, source: str, line: int, heading: str) -> dict[str, Any]:
    category = _slug(heading)
    enforcement, confidence, warnings = _classify(raw)
    digest = sha256(f"{source}\0{line}\0{raw}".encode("utf-8")).hexdigest()[:12]
    return {
        "id": f"rule-{digest}",
        "category": category,
        "scope": [category],
        "enforcement": enforcement,
        "evidence": raw,
        "source": source,
        "location": {"line": line, "heading": heading},
        "confidence": confidence,
        "warnings": warnings,
    }


def extract_markdown_rules(text: str, source: str) -> list[dict[str, Any]]:
    """抽取二级及以下章节中的项目符号和紧凑段落。"""

    rules: list[dict[str, Any]] = []
    heading = "General"
    active_section = False
    in_fence = False
    paragraph: list[str] = []
    paragraph_line = 0

    def flush() -> None:
        nonlocal paragraph, paragraph_line
        if paragraph:
            rules.append(_make_rule(" ".join(paragraph), source, paragraph_line, heading))
            paragraph = []
            paragraph_line = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(stripped)
        if match:
            flush()
            if len(match.group("level")) >= 2:
                active_section = True
                heading = match.group("title").strip()
            continue
        if not active_section:
            continue
        bullet = BULLET.match(line)
        if bullet:
            flush()
            rules.append(_make_rule(bullet.group("text"), source, line_number, heading))
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith(("|", ">", "<!--")):
            flush()
            continue
        if not paragraph:
            paragraph_line = line_number
        paragraph.append(stripped)
    flush()
    return rules


def _manifest_relative(system_dir: Path, value: Any, field_path: str, optional: bool = False) -> tuple[str, Path] | None:
    if not isinstance(value, str) or not value.strip():
        if optional:
            return None
        raise ContractError(f"{field_path}: expected a non-empty relative path")
    path = safe_relative_path(system_dir, value)
    if not path.is_file():
        if optional:
            return None
        raise ContractError(f"{field_path}: file does not exist: {value}")
    return Path(value).as_posix(), path


def compile_rule_bundle(system_dir: str | Path) -> dict[str, Any]:
    """编译一个设计系统目录，任何证据文件都只读。"""

    root = Path(system_dir).resolve()
    manifest_path = root / "manifest.json"
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ContractError("$.manifest: expected an object")
    system_id = manifest.get("id")
    name = manifest.get("name")
    if not isinstance(system_id, str) or not system_id:
        raise ContractError("$.manifest.id: expected a non-empty string")
    if system_id != root.name:
        raise ContractError(f"$.manifest.id: {system_id!r} does not match directory {root.name!r}")
    if not isinstance(name, str) or not name:
        raise ContractError("$.manifest.name: expected a non-empty string")
    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, dict):
        raise ContractError("$.manifest.files: expected an object")

    design = _manifest_relative(root, manifest_files.get("design"), "$.manifest.files.design")
    tokens_file = _manifest_relative(root, manifest_files.get("tokens"), "$.manifest.files.tokens")
    components = _manifest_relative(root, manifest_files.get("components"), "$.manifest.files.components")
    usage = _manifest_relative(root, manifest.get("usage"), "$.manifest.usage", optional=True)

    files = ["manifest.json", design[0], tokens_file[0]]
    if components:
        files.append(components[0])
    if usage:
        files.append(usage[0])
    files = sorted(set(files))

    tokens = parse_root_tokens(tokens_file[1].read_text(encoding="utf-8"), tokens_file[0])
    warnings: list[str] = []
    declarations: dict[str, list[dict[str, Any]]] = {}
    for token in tokens:
        declarations.setdefault(token["name"], []).append(token)
    for token_name, values in sorted(declarations.items()):
        if len(values) > 1:
            locations = ", ".join(f"{item['source']}:{item['location']['line']}={item['value']}" for item in values)
            warnings.append(f"duplicate token declaration {token_name}: {locations}")

    rules = extract_markdown_rules(design[1].read_text(encoding="utf-8"), design[0])
    if usage:
        rules.extend(extract_markdown_rules(usage[1].read_text(encoding="utf-8"), usage[0]))
    rules.sort(key=lambda rule: (rule["source"], rule["location"]["line"], rule["id"]))

    bundle = {
        "schemaVersion": "ui-design-system-design-rule-bundle/v1",
        "system": {
            "id": system_id,
            "name": name,
            "assetVersion": f"sha256:{sha256(manifest_path.read_bytes()).hexdigest()[:16]}",
        },
        "files": files,
        "tokens": tokens,
        "rules": rules,
        "warnings": warnings,
        "approvedDeviations": [],
    }
    validate_design_rule_bundle(bundle)
    return bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    write_json(args.output, compile_rule_bundle(args.system_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
