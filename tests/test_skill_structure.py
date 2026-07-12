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
