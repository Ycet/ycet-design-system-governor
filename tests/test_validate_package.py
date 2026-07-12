from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import unittest

from tests.support import SCRIPTS_ROOT
from validate_package import validate_package


REFERENCES = (
    "system-selection.md",
    "new-design.md",
    "redesign.md",
    "consistency-audit.md",
    "conflict-gates.md",
    "output-contracts.md",
    "selection-vocabulary.md",
)
SCRIPTS = (
    "contracts.py",
    "build_catalog.py",
    "recommend_systems.py",
    "compile_rules.py",
    "audit_static.py",
    "validate_package.py",
)
SCHEMAS = (
    "selection-profile.schema.json",
    "design-rule-bundle.schema.json",
    "conflict-report.schema.json",
    "compliance-report.schema.json",
)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def create_valid_package(root: Path) -> Path:
    skill = root / "skill"
    links = "\n".join(f"- [{name}](references/{name})" for name in REFERENCES)
    (skill / "references").mkdir(parents=True)
    (skill / "scripts").mkdir()
    (skill / "schemas").mkdir()
    (skill / "agents").mkdir()
    (skill / "assets" / "catalog").mkdir(parents=True)
    (skill / "assets" / "design-systems" / "_schema").mkdir(parents=True)
    system = skill / "assets" / "design-systems" / "system-a"
    system.mkdir()
    (skill / "SKILL.md").write_text(f"---\nname: fixture\ndescription: Use when validating a fixture.\n---\n\n{links}\n", encoding="utf-8")
    (skill / "agents" / "openai.yaml").write_text("interface:\n  display_name: Fixture\n", encoding="utf-8")
    for name in REFERENCES:
        (skill / "references" / name).write_text(f"# {name}\n\nComplete guidance.\n", encoding="utf-8")
    for name in SCRIPTS:
        (skill / "scripts" / name).write_text('"""Complete fixture module."""\n', encoding="utf-8")
    for name in SCHEMAS:
        write_json(skill / "schemas" / name, {"type": "object"})
    (skill / "assets" / "design-systems" / "_schema" / "defaults.css").write_text(":root {}\n", encoding="utf-8")
    write_json(system / "manifest.json", {"id": "system-a", "name": "System A"})
    (system / "DESIGN.md").write_text("# System A\n", encoding="utf-8")
    profile = {"id": "system-a", "aliases": ["system-a"]}
    write_json(skill / "assets" / "catalog" / "selection-profiles.json", {"schemaVersion": "ui-design-system-selection-profiles/v1", "profiles": [profile]})
    entry = {"id": "system-a", "files": ["DESIGN.md", "manifest.json"]}
    write_json(skill / "assets" / "catalog" / "design-systems.index.json", {"schemaVersion": "ui-design-system-catalog/v1", "systems": [entry]})
    inventory = []
    asset_root = skill / "assets" / "design-systems"
    for path in sorted((item for item in asset_root.rglob("*") if item.is_file()), key=lambda item: item.relative_to(asset_root).as_posix()):
        data = path.read_bytes()
        inventory.append({"path": path.relative_to(asset_root).as_posix(), "size": len(data), "sha256": sha256(data).hexdigest()})
    write_json(skill / "assets" / "catalog" / "inventory.json", {"schemaVersion": "ui-design-system-inventory/v1", "files": inventory})
    return skill


def update_json(path: Path, callback) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    callback(value)
    write_json(path, value)


class ValidatePackageTests(unittest.TestCase):
    def test_valid_minimal_package_is_clean_and_unmodified(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            before = {p.relative_to(skill).as_posix(): sha256(p.read_bytes()).hexdigest() for p in skill.rglob("*") if p.is_file()}
            self.assertEqual(validate_package(skill, expected_system_count=1), [])
            after = {p.relative_to(skill).as_posix(): sha256(p.read_bytes()).hexdigest() for p in skill.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_missing_skill_file_and_auxiliary_readme_are_reported(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            (skill / "SKILL.md").unlink()
            (skill / "README.md").write_text("extra\n", encoding="utf-8")
            errors = validate_package(skill, expected_system_count=1)
            self.assertTrue(any("SKILL.md" in error for error in errors))
            self.assertTrue(any("README.md" in error for error in errors))

    def test_unresolved_marker_and_missing_reference_link_are_reported(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            skill_file = skill / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            text = text.replace(f"- [{REFERENCES[0]}](references/{REFERENCES[0]})\n", "")
            skill_file.write_text(text + "\nTO" "DO: finish this\n", encoding="utf-8")
            errors = validate_package(skill, expected_system_count=1)
            self.assertTrue(any("SKILL.md" in error and "unfinished marker" in error for error in errors))
            self.assertTrue(any(REFERENCES[0] in error and "link" in error for error in errors))

    def test_missing_schema_directory_and_system_count_are_reported(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            shutil.rmtree(skill / "assets" / "design-systems" / "_schema")
            errors = validate_package(skill, expected_system_count=2)
            self.assertTrue(any("assets/design-systems/_schema" in error for error in errors))
            self.assertTrue(any("expected 2" in error for error in errors))

    def test_profile_index_id_drift_is_reported(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            path = skill / "assets" / "catalog" / "selection-profiles.json"
            update_json(path, lambda value: value["profiles"][0].update(id="different"))
            errors = validate_package(skill, expected_system_count=1)
            self.assertTrue(any("selection-profiles.json" in error and "ID drift" in error for error in errors))

    def test_unsafe_catalog_path_is_reported(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            path = skill / "assets" / "catalog" / "design-systems.index.json"
            update_json(path, lambda value: value["systems"][0]["files"].append("../outside.css"))
            errors = validate_package(skill, expected_system_count=1)
            self.assertTrue(any("design-systems.index.json" in error and "../outside.css" in error for error in errors))

    def test_stale_inventory_hash_is_reported(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            (skill / "assets" / "design-systems" / "system-a" / "DESIGN.md").write_text("changed\n", encoding="utf-8")
            errors = validate_package(skill, expected_system_count=1)
            self.assertTrue(any("inventory.json" in error and "system-a/DESIGN.md" in error and "hash" in error for error in errors))

    def test_errors_are_sorted(self):
        with TemporaryDirectory() as temp_dir:
            skill = create_valid_package(Path(temp_dir))
            (skill / "README.md").write_text("extra\n", encoding="utf-8")
            (skill / "references" / REFERENCES[-1]).unlink()
            errors = validate_package(skill, expected_system_count=3)
            self.assertEqual(errors, sorted(errors))


if __name__ == "__main__":
    unittest.main()
