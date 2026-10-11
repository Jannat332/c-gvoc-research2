"""
Candidate 2: Clean-State Suppression Gating Router

Decouples clean-state stopping pre-gate from uncalibrated point-estimate GVoC:
    If d_layout < 0.15 and d_evidence < 0.15 and P_stop >= 0.70 -> STOP immediately
    Else -> Standard point-estimate GVoC (kappa = 0)
"""

from typing import Dict, Any, Tuple, Optional
from gvoc_engine.core.action_space import Action, ActionSpace
from gvoc_engine.core.state import GroundedState
from gvoc_engine.controllers.gvoc_router import GVoCRouter


class CleanGatedPrototype:
    """Candidate 2 Router: Two-stage cascaded clean-state gating."""

    def __init__(
        self,
        base_router: Optional[GVoCRouter] = None,
        tau_safe: float = 0.40,
        tau_clean: float = 0.70,
        epsilon: float = 1e-4
    ):
        self.base_router = base_router or GVoCRouter(calibration_mode="point_estimate", kappa=0.0)
        self.tau_safe = tau_safe
        self.tau_clean = tau_clean
        self.epsilon = epsilon

    def select_action(
        self,
        state: GroundedState,
        remaining_budget: int = 2000
    ) -> Tuple[Action, Dict[str, Any]]:
        p_stop, _ = self.base_router.predict_outcome(state, Action.STOP)

        # Stage 1: Fast Clean Gating Pre-filter
        if state.d_layout < 0.15 and state.d_evidence < 0.15 and p_stop >= self.tau_clean:
            return Action.STOP, {"decision_path": "clean_state_gated", "score": 0.0}

        # Stage 2: Standard Point-Estimate GVoC (kappa = 0)
        best_action = Action.STOP
        best_score = -float("inf")
        scores = {}

        for act in ActionSpace.ACTIVE_ACTIONS:
            p_act, cost_act = self.base_router.predict_outcome(state, act)
            delta_p = p_act - p_stop
            score = max(0.0, delta_p) / (cost_act + self.epsilon)

            scores[act.value] = {
                "score": score,
                "delta_p": delta_p,
                "cost": cost_act,
                "p_act": p_act
            }

            est_tokens = int(cost_act * 150)
            if est_tokens <= remaining_budget and p_act >= 0.45 and score > best_score:
                best_score = score
                best_action = act

        if best_score > 0.02:
            return best_action, {"decision_path": "point_estimate_active", "scores": scores}
        elif p_stop < self.tau_safe:
            return Action.ABSTAIN, {"decision_path": "safe_abstention", "scores": scores}
        else:
            return Action.STOP, {"decision_path": "standard_stop", "scores": scores}
