from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from tests.support import SCRIPTS_ROOT
from build_catalog import (
    bootstrap_profiles,
    build_catalog,
    build_inventory,
    discover_systems,
    main,
)
from contracts import ContractError


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


def write_fixture(root: Path, system_id: str, name: str, category: str) -> None:
    system_root = root / system_id
    system_root.mkdir(parents=True)
    manifest = {
        "schemaVersion": "od-design-system-project/v1",
        "id": system_id,
        "name": name,
        "category": category,
        "description": f"A calm dashboard-oriented package for {name}.",
        "files": {"design": "DESIGN.md", "tokens": "tokens.css"},
    }
    (system_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (system_root / "DESIGN.md").write_text(
        "# Design\nDark compact dashboard grid. Responsive tables and charts.\n", encoding="utf-8"
    )
    (system_root / "tokens.css").write_text(":root { --space-1: 4px; }\n", encoding="utf-8")


class BuildCatalogTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> None:
        write_fixture(root, "zeta", "Zeta", "Developer Tools")
        write_fixture(root, "alpha", "Alpha", "Backend & Data")

    def test_discovery_and_catalog_are_stably_sorted(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            systems = discover_systems(root)
            profiles = bootstrap_profiles(systems)
            catalog = build_catalog(root, profiles)

            self.assertEqual([item["id"] for item in systems], ["alpha", "zeta"])
            self.assertEqual([item["id"] for item in catalog["systems"]], ["alpha", "zeta"])
            self.assertEqual(
                set(catalog["systems"][0]),
                {"id", "name", "category", "description", "profile", "files", "searchText"},
            )

    def test_discovery_rejects_manifest_directory_mismatch(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root, "folder-id", "Wrong", "Starter")
            manifest_path = root / "folder-id" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["id"] = "other-id"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, r"folder-id.*other-id"):
                discover_systems(root)

    def test_catalog_rejects_missing_and_extra_profile_ids(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            profiles = bootstrap_profiles(discover_systems(root))
            missing = {"schemaVersion": profiles["schemaVersion"], "profiles": profiles["profiles"][:-1]}
            with self.assertRaisesRegex(ContractError, r"profile coverage"):
                build_catalog(root, missing)
            extra = json.loads(json.dumps(profiles))
            extra["profiles"].append({"id": "extra", **{field: [] for field in PROFILE_FIELDS}})
            with self.assertRaisesRegex(ContractError, r"profile coverage"):
                build_catalog(root, extra)

    def test_profiles_have_required_arrays_and_nonempty_core_tags(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            profiles = bootstrap_profiles(discover_systems(root))["profiles"]
            aliases = []
            for profile in profiles:
                for field in PROFILE_FIELDS:
                    self.assertIsInstance(profile[field], list, field)
                for field in ("productTypes", "tones", "themes", "layouts"):
                    self.assertTrue(profile[field], f"{profile['id']}:{field}")
                aliases.extend(profile["aliases"])
            self.assertEqual(len(aliases), len(set(aliases)))

    def test_catalog_paths_are_safe_posix_relative_paths(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            catalog = build_catalog(root, bootstrap_profiles(discover_systems(root)))
            for entry in catalog["systems"]:
                self.assertEqual(entry["files"], sorted(entry["files"]))
                for value in entry["files"]:
                    self.assertNotIn("\\", value)
                    self.assertFalse(value.startswith("/"))
                    self.assertNotIn("..", Path(value).parts)

    def test_inventory_hashes_bytes_and_is_sorted(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            inventory = build_inventory(root)
            paths = [entry["path"] for entry in inventory["files"]]
            self.assertEqual(paths, sorted(paths))
            target = root / paths[0]
            self.assertEqual(inventory["files"][0]["sha256"], sha256(target.read_bytes()).hexdigest())
            self.assertEqual(inventory["files"][0]["size"], target.stat().st_size)

    def test_building_does_not_mutate_source_files(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            before = {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
            systems = discover_systems(root)
            profiles = bootstrap_profiles(systems)
            build_catalog(root, profiles)
            build_inventory(root)
            after = {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(after, before)

    def test_bootstrap_cli_refuses_to_overwrite_without_force(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_fixture(root)
            profiles_path = root / "profiles.json"
            profiles_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, r"refusing to overwrite"):
                main([
                    "--asset-root",
                    str(root),
                    "--profiles",
                    str(profiles_path),
                    "--bootstrap-profiles",
                ])


if __name__ == "__main__":
    unittest.main()
