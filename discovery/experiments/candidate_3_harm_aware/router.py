"""
Candidate 3: Harm-Aware Decomposed Repair Router

Decomposes net advantage into explicit Repair and Harm components:
    Expected Gain = P(Repair | s) * (1 - P_stop) - lambda_harm * P(Harm | s) * P_stop
"""

from typing import Dict, Any, Tuple, Optional
from gvoc_engine.core.action_space import Action, ActionSpace
from gvoc_engine.core.state import GroundedState
from gvoc_engine.controllers.gvoc_router import GVoCRouter


class HarmAwarePrototype:
    """Candidate 3 Router: Decomposed repair vs harm optimization."""

    def __init__(
        self,
        base_router: Optional[GVoCRouter] = None,
        lambda_harm: float = 2.0,
        tau_safe: float = 0.40,
        tau_clean: float = 0.70,
        epsilon: float = 1e-4
    ):
        self.base_router = base_router or GVoCRouter(calibration_mode="point_estimate", kappa=0.0)
        self.lambda_harm = lambda_harm
        self.tau_safe = tau_safe
        self.tau_clean = tau_clean
        self.epsilon = epsilon

    def select_action(
        self,
        state: GroundedState,
        remaining_budget: int = 2000
    ) -> Tuple[Action, Dict[str, Any]]:
        p_stop, _ = self.base_router.predict_outcome(state, Action.STOP)

        # Clean-State early stopping
        if state.d_layout < 0.15 and state.d_evidence < 0.15 and p_stop >= self.tau_clean:
            return Action.STOP, {"decision_path": "clean_state_suppression", "score": 0.0}

        best_action = Action.STOP
        best_score = -float("inf")
        scores = {}

        for act in ActionSpace.ACTIVE_ACTIONS:
            p_act, cost_act = self.base_router.predict_outcome(state, act)

            # Heuristic model of repair vs harm
            if state.c_consensus < 0.15 and state.d_evidence > 0.80:
                p_repair = 0.0  # Physically destroyed / unrecoverable content cannot be repaired
            else:
                p_repair = min(0.95, max(0.05, (p_act - p_stop * 0.5) / max(0.1, 1.0 - p_stop)))
            # Harm probability is non-zero when initial confidence is high and distortion is low
            p_harm = max(0.01, min(0.30, p_stop * 0.15 * (1.0 - state.d_layout)))

            expected_gain = (p_repair * (1.0 - p_stop)) - (self.lambda_harm * p_harm * p_stop)
            score = max(0.0, expected_gain) / (cost_act + self.epsilon)

            scores[act.value] = {
                "score": score,
                "p_repair": p_repair,
                "p_harm": p_harm,
                "cost": cost_act
            }

            est_tokens = int(cost_act * 150)
            if est_tokens <= remaining_budget and p_act >= 0.45 and score > best_score:
                best_score = score
                best_action = act

        if best_score > 0.02:
            return best_action, {"decision_path": "harm_aware_intervention", "scores": scores}
        elif p_stop < self.tau_safe:
            return Action.ABSTAIN, {"decision_path": "safe_abstention", "scores": scores}
        else:
            return Action.STOP, {"decision_path": "conservative_stop", "scores": scores}
