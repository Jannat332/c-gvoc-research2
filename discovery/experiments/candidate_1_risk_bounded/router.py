"""
Candidate 1: Risk-Bounded Counterfactual Intervention Policy (C-GVoC LCB)

Computes Lower Confidence Bound on estimated accuracy gain over stopping:
    Score_LCB(s, a) = max(0, Delta_P_hat(s, a) - kappa * sigma_hat(s, a)) / (Cost_hat + eps)
"""

import math
from typing import Dict, Any, Tuple, Optional
from gvoc_engine.core.action_space import Action, ActionSpace
from gvoc_engine.core.state import GroundedState
from gvoc_engine.controllers.gvoc_router import GVoCRouter


class RiskBoundedPrototype:
    """Candidate 1 Router: Evaluates telemetry-conditioned LCB intervention utility."""

    def __init__(
        self,
        base_router: Optional[GVoCRouter] = None,
        kappa: float = 0.10,
        tau_safe: float = 0.40,
        tau_clean: float = 0.70,
        epsilon: float = 1e-4
    ):
        self.base_router = base_router or GVoCRouter(calibration_mode="point_estimate", kappa=0.0)
        self.kappa = kappa
        self.tau_safe = tau_safe
        self.tau_clean = tau_clean
        self.epsilon = epsilon

    def estimate_uncertainty(self, state: GroundedState, action: Action) -> float:
        """Estimates epistemic standard error from state telemetry."""
        if ActionSpace.is_terminal(action):
            return 0.0
        var_consensus = (1.0 - state.c_consensus) ** 2
        var_evidence = state.d_evidence ** 2
        var_layout = state.d_layout ** 2
        variance = 0.012 + 0.14 * var_consensus + 0.08 * (var_evidence + var_layout)
        return min(0.40, max(0.03, math.sqrt(variance)))

    def select_action(
        self,
        state: GroundedState,
        remaining_budget: int = 2000
    ) -> Tuple[Action, Dict[str, Any]]:
        p_stop, _ = self.base_router.predict_outcome(state, Action.STOP)

        # Clean-State early stopping
        if state.d_layout < 0.15 and state.d_evidence < 0.15 and p_stop >= self.tau_clean:
            return Action.STOP, {"decision_path": "clean_state_suppression", "score_lcb": 0.0}

        best_action = Action.STOP
        best_score = -float("inf")
        scores = {}

        for act in ActionSpace.ACTIVE_ACTIONS:
            p_act, cost_act = self.base_router.predict_outcome(state, act)
            delta_p = p_act - p_stop
            sigma = self.estimate_uncertainty(state, act)
            delta_p_lcb = max(0.0, delta_p - self.kappa * sigma)
            score_lcb = delta_p_lcb / (cost_act + self.epsilon)

            scores[act.value] = {
                "score_lcb": score_lcb,
                "delta_p": delta_p,
                "sigma": sigma,
                "cost": cost_act,
                "p_act": p_act
            }

            est_tokens = int(cost_act * 150)
            if est_tokens <= remaining_budget and p_act >= 0.45 and score_lcb > best_score:
                best_score = score_lcb
                best_action = act

        if best_score > 0.02:
            return best_action, {"decision_path": "certified_intervention", "scores": scores}
        elif p_stop < self.tau_safe:
            return Action.ABSTAIN, {"decision_path": "safe_abstention", "scores": scores}
        else:
            return Action.STOP, {"decision_path": "conservative_stop", "scores": scores}
