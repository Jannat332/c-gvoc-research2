"""
Grounded Value-of-Compute (GVoC) Controller.

Learns to map intermediate grounded states s_t to optimal process-repair
interventions based on expected marginal reliability gain per unit compute.
"""

import math
from typing import Dict, Any, Tuple, List, Optional
from gvoc_engine.core.action_space import Action, ActionSpace
from gvoc_engine.core.state import GroundedState
from gvoc_engine.config import DEFAULT_UTILITY_WEIGHTS


class GVoCRouter:
    """Action-value controller implementing Grounded Value-of-Compute Routing."""

    def __init__(self, utility_weights: Optional[Dict[str, float]] = None):
        self.weights = utility_weights or DEFAULT_UTILITY_WEIGHTS
        self.lambda_r = self.weights["lambda_R"]
        self.lambda_c = self.weights["lambda_C"]
        self.lambda_s = self.weights["lambda_S"]
        self.tau_safe = self.weights["tau_safe"]
        self.epsilon = self.weights["epsilon"]

    def predict_outcome(
        self,
        state: GroundedState,
        action: Action
    ) -> Tuple[float, float]:
        """
        f_theta(s_t, a) -> (p_hat_correct, Cost_hat)
        Estimates the probability of downstream correctness and expected compute cost.
        """
        # Baseline intrinsic correctness without further intervention
        base_p = (
            state.c_plan * 0.25 +
            state.c_exec * 0.25 +
            state.c_judg * 0.20 +
            state.c_consensus * 0.15 -
            state.d_layout * 0.35 -
            state.d_traj * 0.20 -
            state.d_evidence * 0.20
        )
        base_p = max(0.05, min(0.98, base_p))

        if action == Action.STOP:
            return base_p, 0.0

        if action == Action.ABSTAIN:
            return 0.0, 0.0  # Abstention yields 0 task correctness, 0 extra compute

        # Action-specific reliability gains conditioned on diagnosed deficiencies
        p_gain = 0.0
        cost = 1.0

        if action == Action.REGROUND:
            # Re-grounding has highest payoff when layout loss or evidence discrepancy is high
            gain_factor = (state.d_layout * 1.8) + (state.d_evidence * 1.2) - (state.c_judg * 0.3)
            p_gain = max(0.02, min(0.40, gain_factor))
            cost = 1.2

        elif action == Action.REPLAN:
            # Re-planning pays off when trajectory drift is high or planner confidence is weak
            gain_factor = (state.d_traj * 1.6) + ((1.0 - state.c_plan) * 0.8)
            p_gain = max(0.02, min(0.38, gain_factor))
            cost = 1.8

        elif action == Action.REEXEC:
            # Re-execution pays off when executor confidence is depressed or answer unstable
            gain_factor = ((1.0 - state.c_exec) * 1.4) + (state.d_answer * 1.0)
            p_gain = max(0.03, min(0.42, gain_factor))
            cost = 1.5

        elif action == Action.VERIFY:
            # Verification pays off when consensus is moderate and cost is low
            gain_factor = (0.25 - state.d_layout) + ((1.0 - state.c_consensus) * 0.5)
            p_gain = max(0.01, min(0.25, gain_factor))
            cost = 0.8

        p_correct = max(0.05, min(0.99, base_p + p_gain))
        return p_correct, cost

    def compute_gvoc_value(
        self,
        state: GroundedState,
        action: Action
    ) -> float:
        """
        V_hat(s_t, a) = [p_hat(s_t, a) - p_hat(s_t, stop)] / [C_hat(s_t, a) + epsilon]
        """
        p_act, cost_act = self.predict_outcome(state, action)
        p_stop, _ = self.predict_outcome(state, Action.STOP)

        if ActionSpace.is_terminal(action):
            return 0.0

        delta_p = p_act - p_stop
        return delta_p / (cost_act + self.epsilon)

    def compute_utility(
        self,
        state: GroundedState,
        action: Action
    ) -> float:
        """
        Terminal safety utility formulation:
        U(s_t, a) = lambda_R * delta_R - lambda_C * C + lambda_S * S
        """
        p_act, cost_act = self.predict_outcome(state, action)
        p_stop, _ = self.predict_outcome(state, Action.STOP)

        delta_r = p_act - p_stop

        # Safety bonus S(s_t, a)
        safety_bonus = 0.0
        if action == Action.ABSTAIN:
            # Safe abstention triggered when intrinsic reliability is below safety threshold
            if p_stop < self.tau_safe:
                safety_bonus = (self.tau_safe - p_stop) * 2.0
            else:
                safety_bonus = -1.0  # Penalty for abstaining on a likely correct answer

        return (self.lambda_r * delta_r) - (self.lambda_c * cost_act) + (self.lambda_s * safety_bonus)

    def select_action(
        self,
        state: GroundedState,
        remaining_budget: int = 2000
    ) -> Tuple[Action, Dict[str, Any]]:
        """
        Selects a_t^* = argmax_a U(s_t, a) subject to Cost <= B_t.
        Returns: (chosen_action, diagnostic_metadata)
        """
        p_stop, _ = self.predict_outcome(state, Action.STOP)
        
        # 1. Evaluate candidate active actions
        action_scores: Dict[Action, Dict[str, float]] = {}
        best_active_action = Action.STOP
        max_active_val = -float("inf")

        for act in ActionSpace.ACTIVE_ACTIONS:
            p_pred, c_pred = self.predict_outcome(state, act)
            gvoc_val = self.compute_gvoc_value(state, act)
            util = self.compute_utility(state, act)

            action_scores[act] = {
                "p_correct": p_pred,
                "cost": c_pred,
                "gvoc_val": gvoc_val,
                "utility": util
            }

            # Enforce budget constraint
            estimated_tokens = int(c_pred * 150)
            if estimated_tokens <= remaining_budget and gvoc_val > max_active_val:
                max_active_val = gvoc_val
                best_active_action = act

        # 2. Evaluate terminal actions (Stop vs Abstain)
        stop_util = self.compute_utility(state, Action.STOP)
        abstain_util = self.compute_utility(state, Action.ABSTAIN)
        action_scores[Action.STOP] = {"p_correct": p_stop, "cost": 0.0, "gvoc_val": 0.0, "utility": stop_util}
        action_scores[Action.ABSTAIN] = {"p_correct": 0.0, "cost": 0.0, "gvoc_val": 0.0, "utility": abstain_util}

        # Terminal Decision Logic
        if max_active_val <= 0.0:
            # Active repairs do not yield positive value
            if p_stop < self.tau_safe and abstain_util > stop_util:
                chosen = Action.ABSTAIN
            else:
                chosen = Action.STOP
        else:
            # Active repair yields positive marginal improvement
            chosen = best_active_action

        metadata = {
            "p_stop": p_stop,
            "max_active_val": max_active_val,
            "scores": {k.value: v for k, v in action_scores.items()}
        }
        return chosen, metadata
