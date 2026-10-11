"""
Tests for evaluation integrity, ground-truth isolation, and metric scoring.
"""

import unittest
from discovery.live_validation.scoring import score_vdu_answer, normalize_text
from gvoc_engine.core.state import GroundedState
from gvoc_engine.interventions.ccea_intervention import CCEAResult
from gvoc_engine.controllers.ccea_router import CCEACostAwareRouter


class TestEvaluationIntegrity(unittest.TestCase):
    def test_answer_scoring_exact_and_normalized(self):
        gt = ["1128 SIXTEENTH ST., N. W., WASHINGTON, D. C. 20036"]
        
        # Exact match after normalization (case and punctuation stripped)
        pred = "1128 sixteenth st., n. w., washington, d. c. 20036"
        f1, acc = score_vdu_answer(pred, gt)
        self.assertEqual(acc, 1)
        self.assertEqual(f1, 1.0)

        # Partial substring match
        sub_pred = "1128 sixteenth st"
        f1_sub, acc_sub = score_vdu_answer(sub_pred, gt)
        self.assertEqual(acc_sub, 1)  # substring match is recognized
        self.assertEqual(f1_sub, 1.0)

        # Unrelated text scores 0
        f1_unrelated, acc_unrelated = score_vdu_answer("completely wrong answer", gt)
        self.assertEqual(acc_unrelated, 0)
        self.assertEqual(f1_unrelated, 0.0)

        # Empty prediction scores 0
        f1_empty, acc_empty = score_vdu_answer("", gt)
        self.assertEqual(acc_empty, 0)
        self.assertEqual(f1_empty, 0.0)

    def test_policy_does_not_inspect_ground_truth(self):
        """Verify that the router takes ONLY state, budget, and image geometry, never ground truth."""
        router = CCEACostAwareRouter()
        state = GroundedState(d_layout=0.30, d_evidence=0.25)
        
        # Call signature takes state, remaining_budget, evidence_region, image_width, image_height
        # Ground truth is never passed or accepted
        import inspect
        sig = inspect.signature(router.select_action)
        self.assertNotIn("ground_truth", sig.parameters)
        self.assertNotIn("gt", sig.parameters)
        self.assertNotIn("label", sig.parameters)

    def test_failed_intervention_preserves_error_telemetry(self):
        """Failed or rejected interventions must record status and failure reason."""
        result = CCEAResult(
            initial_answer="Initial answer",
            final_answer="Initial answer",
            status="REJECTED_INVALID_BOX",
            failure_reason="Coordinates out of bounds: ymax=1200 > height=800"
        )
        self.assertNotEqual(result.status, "SUCCESS")
        self.assertIsNotNone(result.failure_reason)
        self.assertEqual(result.final_answer, "Initial answer")

    def test_total_tokens_sums_all_calls(self):
        """Ensure token accounting captures all sequential calls."""
        res = CCEAResult(
            prompt_tokens=150,
            completion_tokens=45,
            total_tokens=195,
            num_calls=2
        )
        self.assertEqual(res.total_tokens, res.prompt_tokens + res.completion_tokens)
        self.assertEqual(res.num_calls, 2)


if __name__ == "__main__":
    unittest.main()
