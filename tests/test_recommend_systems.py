from copy import deepcopy
import unittest

from tests.support import SCRIPTS_ROOT
from recommend_systems import (
    COMPLETENESS_WEIGHT,
    FIT_GROUPS,
    MAX_RECOMMENDATIONS,
    PREVIEW_URL,
    RELIABLE_THRESHOLD,
    hard_filter,
    recommend,
    score_system,
)


def profile(**overrides):
    value = {
        "schemaVersion": "ui-design-system-selection-profile/v1",
        "taskMode": "new-design",
        "brief": "Create a calm dark analytics dashboard.",
        "industry": ["backend-data"],
        "audience": ["technical-operators"],
        "productType": ["analytics-dashboard"],
        "tone": ["calm", "professional"],
        "theme": ["dark"],
        "density": ["compact"],
        "layoutNeeds": ["dashboard-grid"],
        "contentNeeds": ["data-visualization"],
        "componentNeeds": ["tables"],
        "requiredTraits": [],
        "excludedTraits": [],
        "inputSources": [],
        "explicitSystem": None,
    }
    value.update(overrides)
    return value


def entry(system_id, offered=None, files=None):
    dimensions = {
        "aliases": [system_id],
        "productTypes": ["analytics-dashboard"],
        "industries": ["backend-data"],
        "audiences": ["technical-operators"],
        "tones": ["calm", "professional"],
        "themes": ["dark"],
        "densities": ["compact"],
        "layouts": ["dashboard-grid"],
        "contentNeeds": ["data-visualization"],
        "componentNeeds": ["tables", "charts"],
        "requiredTraits": [],
        "excludedTraits": [],
    }
    if offered:
        dimensions.update(offered)
    return {
        "id": system_id,
        "name": system_id.title(),
        "category": "Backend & Data",
        "description": "Fixture",
        "profile": dimensions,
        "files": files if files is not None else [
            "manifest.json",
            "DESIGN.md",
            "tokens.css",
            "components.html",
            "components.manifest.json",
        ],
        "searchText": system_id,
    }


def catalog(*entries):
    return {"schemaVersion": "ui-design-system-catalog/v1", "systems": list(entries)}


class RecommendationTests(unittest.TestCase):
    def test_constants_match_the_scoring_contract(self):
        self.assertEqual(PREVIEW_URL, "https://open-design.ai/zh/plugins/systems/")
        self.assertEqual(RELIABLE_THRESHOLD, 60.0)
        self.assertEqual(MAX_RECOMMENDATIONS, 5)
        self.assertEqual(COMPLETENESS_WEIGHT, 5)
        self.assertEqual(sum(weight for _, weight in FIT_GROUPS), 95)

    def test_perfect_fit_scores_100_with_complete_files(self):
        result = score_system(profile(), entry("perfect"))
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["breakdown"]["fit"], 95.0)
        self.assertEqual(result["breakdown"]["completeness"], 5.0)
        self.assertEqual(result["unmatchedTerms"], {})

    def test_active_dimensions_are_normalized_to_95(self):
        request = profile(
            industry=[], audience=[], tone=[], theme=[], density=[],
            layoutNeeds=[], contentNeeds=[]
        )
        result = score_system(request, entry("only-product"))
        self.assertEqual(result["breakdown"]["fit"], 95.0)

    def test_group_weight_splits_between_active_subdimensions(self):
        request = profile(
            productType=[], tone=[], theme=[], density=[], layoutNeeds=[], contentNeeds=[],
            industry=["backend-data"], audience=["missing-audience"]
        )
        result = score_system(request, entry("split"))
        self.assertEqual(result["breakdown"]["fit"], 47.5)
        self.assertEqual(result["breakdown"]["dimensions"]["industry"]["normalizedScore"], 47.5)
        self.assertEqual(result["breakdown"]["dimensions"]["audience"]["normalizedScore"], 0.0)

    def test_completeness_is_capped_at_five_and_reports_missing_files(self):
        result = score_system(profile(), entry("partial", files=["manifest.json", "DESIGN.md"]))
        self.assertEqual(result["breakdown"]["completeness"], 2.0)
        self.assertTrue(any("missing asset files" in risk for risk in result["risks"]))

    def test_required_and_excluded_traits_are_hard_filters(self):
        candidate = entry("candidate", {"requiredTraits": ["accessible", "morphism"]})
        self.assertTrue(hard_filter(profile(requiredTraits=["accessible"]), candidate)["eligible"])
        self.assertFalse(hard_filter(profile(requiredTraits=["offline"]), candidate)["eligible"])
        self.assertFalse(hard_filter(profile(excludedTraits=["morphism"]), candidate)["eligible"])

    def test_threshold_and_stable_id_tie_breaking(self):
        good_b = entry("b-good")
        good_a = entry("a-good")
        weak = entry("weak", {"productTypes": ["other"], "industries": ["other"], "audiences": ["other"], "tones": ["other"], "themes": ["other"], "densities": ["other"], "layouts": ["other"], "contentNeeds": ["other"]})
        result = recommend(profile(), catalog(good_b, weak, good_a))
        self.assertEqual([item["id"] for item in result["recommendations"]], ["a-good", "b-good"])
        self.assertTrue(all(item["score"] >= RELIABLE_THRESHOLD for item in result["recommendations"]))

    def test_default_three_maximum_five_and_no_padding(self):
        values = [entry(f"system-{index}") for index in range(7)]
        self.assertEqual(len(recommend(profile(), catalog(*values))["recommendations"]), 3)
        self.assertEqual(len(recommend(profile(), catalog(*values), requested_limit=9)["recommendations"]), 5)
        self.assertEqual(len(recommend(profile(), catalog(entry("only")))["recommendations"]), 1)

    def test_no_active_fit_dimension_returns_no_candidates(self):
        request = profile(
            productType=[], industry=[], audience=[], tone=[], theme=[], density=[],
            layoutNeeds=[], contentNeeds=[]
        )
        result = recommend(request, catalog(entry("unused")))
        self.assertEqual(result["status"], "awaiting-manual-selection")
        self.assertEqual(result["recommendations"], [])

    def test_zero_match_includes_preview_and_manual_status(self):
        request = profile(requiredTraits=["impossible-trait"])
        result = recommend(request, catalog(entry("candidate")))
        self.assertEqual(result["status"], "awaiting-manual-selection")
        self.assertEqual(result["recommendations"], [])
        self.assertEqual(result["previewUrl"], "https://open-design.ai/zh/plugins/systems/")

    def test_result_exposes_matches_unmatched_terms_and_deterministic_risks(self):
        request = profile(tone=["calm", "luxury"])
        first = recommend(request, catalog(entry("candidate")))
        second = recommend(deepcopy(request), catalog(entry("candidate")))
        recommendation = first["recommendations"][0]
        self.assertEqual(first, second)
        self.assertIn("calm", recommendation["matchedTerms"]["tone"])
        self.assertIn("luxury", recommendation["unmatchedTerms"]["tone"])
        self.assertTrue(recommendation["risks"])


if __name__ == "__main__":
    unittest.main()
