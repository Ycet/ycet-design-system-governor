from pathlib import Path
import unittest

from tests.support import SKILL_ROOT


class SkillBehaviorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    def assert_contains_all(self, *values):
        for value in values:
            with self.subTest(value=value):
                self.assertIn(value, self.skill)

    def test_controller_sections_remain_in_required_order(self):
        headings = (
            "## Core principle",
            "## Invocation checklist",
            "## Explicit-system predicate",
            "## No-system recommendation and mandatory pause",
            "## No reliable match and mandatory pause",
            "## Rule compilation",
            "## Conflict report and mandatory pause",
            "## Mode routing",
            "## Audit repair approval",
            "## Validation and degraded-mode labels",
            "## Direct references",
            "## Common mistakes and counters",
        )
        positions = [self.skill.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))

    def test_unspecified_system_gate_is_non_bypassable(self):
        self.assert_contains_all(
            "is not an explicit selection",
            "assets/catalog/design-systems.index.json",
            "https://open-design.ai/zh/plugins/systems/",
            "awaiting-user-selection",
            "Do not start design or implementation in the same turn",
        )

    def test_no_match_gate_forbids_padding_and_stops(self):
        self.assert_contains_all(
            "no bundled system is a reliable match",
            "Do not add weak candidates merely to reach a requested count",
            "awaiting-manual-selection",
            "invite the user to choose manually or revise constraints",
        )

    def test_conflict_gate_requires_three_outputs_and_user_decision(self):
        self.assert_contains_all(
            "The concrete requirement and design-system rule that conflict",
            "risk of insisting on the current system",
            "Other reliable bundled systems",
            "switch-system",
            "keep-current-system",
            "adjust-requirements",
            "awaiting-user-decision",
            "A director’s approval, launch deadline, or technical workaround does not resolve",
        )

    def test_audit_is_report_first_and_requires_later_scope_approval(self):
        self.assert_contains_all(
            "Audit mode is report-first",
            "without editing the target",
            "awaiting-repair-approval",
            "Only a later, explicit user response",
            "fix everything automatically",
        )
        audit = (SKILL_ROOT / "references" / "consistency-audit.md").read_text(encoding="utf-8")
        for value in ("severity", "rule ID", "actual evidence", "repair advice", "confidence", "verification status"):
            with self.subTest(value=value):
                self.assertIn(value, audit)

    def test_all_focused_references_are_directly_linked(self):
        for name in (
            "system-selection.md",
            "new-design.md",
            "redesign.md",
            "consistency-audit.md",
            "conflict-gates.md",
            "output-contracts.md",
            "selection-vocabulary.md",
        ):
            with self.subTest(name=name):
                self.assertIn(f"references/{name}", self.skill)
                self.assertTrue((SKILL_ROOT / "references" / name).is_file())


if __name__ == "__main__":
    unittest.main()
