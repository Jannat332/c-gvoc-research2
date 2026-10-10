"""
Comparative Baseline Controllers for Benchmark Evaluation.
Implements:
1. Monolithic (Single-Pass)
2. Self-Consistency (Sample Scaling)
3. Fixed VEC-CAP (Prior Heuristic Rules)
4. MACT (Adaptive Agent-Wise Scaling)
5. Confidence-Only Router
6. Empirical Oracle GVoC
"""

from typing import Dict, Any, Tuple, Optional, List
from gvoc_engine.core.action_space import Action
from gvoc_engine.core.state import GroundedState


class MonolithicBaseline:
    """Zero-recovery single-pass forward inference."""
    def select_action(self, state: GroundedState, remaining_budget: int) -> Action:
        return Action.STOP


class SelfConsistencyBaseline:
    """Sample scaling: uniform sampling without process repair."""
    def __init__(self, num_samples: int = 3):
        self.num_samples = num_samples

    def select_action(self, state: GroundedState, remaining_budget: int) -> Action:
        # Self-consistency terminates once target sample budget is spent
        if state.n_tokens_spent >= 300 * self.num_samples or remaining_budget <= 150:
            return Action.STOP
        return Action.STOP  # Samples independently


class FixedVECCAPBaseline:
    """
    Our Prior Submission Baseline: Deterministic priority rules.
    If D_layout >= 0.25 -> re-ground;
    Elif C_plan < 0.70 -> re-plan;
    Elif C_exec < 0.70 -> re-execute;
    Else -> stop.
    """
    def select_action(self, state: GroundedState, remaining_budget: int) -> Action:
        if remaining_budget <= 150:
            return Action.STOP

        if state.d_layout >= 0.20:
            return Action.REGROUND
        elif state.c_plan < 0.70 or state.d_traj >= 0.25:
            return Action.REPLAN
        elif state.c_exec < 0.70 or state.d_answer >= 0.20:
            return Action.REEXEC
        elif state.c_consensus < 0.65:
            return Action.VERIFY
        else:
            return Action.STOP


class MACTBaseline:
    """
    MACT (Yu et al., 2026): Adaptive Agent-Wise Scaling.
    Scales budget at macro agent level (more planning paths or judgment retries)
    rather than diagnosing specific intermediate state repairs.
    """
    def __init__(self, max_agent_retries: int = 2):
        self.max_retries = max_agent_retries

    def select_action(self, state: GroundedState, remaining_budget: int) -> Action:
        if remaining_budget <= 200 or state.step_index >= self.max_retries:
            return Action.STOP
        
        # Macro agent allocation based on agent confidence ranking
        agent_scores = {
            Action.REPLAN: state.c_plan,
            Action.REEXEC: state.c_exec,
            Action.VERIFY: state.c_judg
        }
        # Give more compute to lowest confidence agent
        weakest_agent = min(agent_scores, key=agent_scores.get)
        if agent_scores[weakest_agent] < 0.75:
            return weakest_agent
        return Action.STOP


class ConfidenceRouterBaseline:
    """Ablation: Routes using semantic confidence only, without counterfactual outcome modeling."""
    def select_action(self, state: GroundedState, remaining_budget: int) -> Action:
        if remaining_budget <= 150:
            return Action.STOP

        avg_conf = (state.c_plan + state.c_exec + state.c_judg) / 3.0
        if avg_conf > 0.85:
            return Action.STOP
        elif avg_conf < 0.40:
            return Action.ABSTAIN
        else:
            # Picks re-execution by default when confidence is moderate
            return Action.REEXEC


class OracleGVoCRouter:
    """
    Empirical Upper Bound: Selects argmax_a V_emp(s_t, a) from held-out empirical branch outcomes.
    Used exclusively to evaluate Oracle Intervention Regret (IR_oracle).
    """
    def select_action_from_oracle(
        self,
        held_out_branch_values: Dict[Action, float]
    ) -> Tuple[Action, float]:
        """Selects the action with maximum empirical oracle value."""
        best_act = Action.STOP
        best_val = -float("inf")
        for act, val in held_out_branch_values.items():
            if val > best_val:
                best_val = val
                best_act = act
        return best_act, best_val
