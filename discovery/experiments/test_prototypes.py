"""
Unit tests for the three prototype candidate routers.
"""

import pytest
from gvoc_engine.core.action_space import Action
from gvoc_engine.core.state import GroundedState
from discovery.experiments.candidate_1_risk_bounded.router import RiskBoundedPrototype
from discovery.experiments.candidate_2_clean_gated.router import CleanGatedPrototype
from discovery.experiments.candidate_3_harm_aware.router import HarmAwarePrototype


@pytest.fixture
def clean_state():
    return GroundedState(
        c_plan=0.95, c_exec=0.92, c_judg=0.95, c_consensus=0.96,
        d_layout=0.02, d_traj=0.03, d_evidence=0.04, d_answer=0.01,
        rho_visual=0.55
    )


@pytest.fixture
def blurry_state():
    return GroundedState(
        c_plan=0.85, c_exec=0.80, c_judg=0.30, c_consensus=0.75,
        d_layout=0.45, d_traj=0.08, d_evidence=0.45, d_answer=0.10,
        rho_visual=0.60
    )


@pytest.fixture
def hopeless_state():
    return GroundedState(
        c_plan=0.15, c_exec=0.10, c_judg=0.10, c_consensus=0.05,
        d_layout=0.90, d_traj=0.85, d_evidence=0.95, d_answer=0.85,
        rho_visual=0.90
    )


def test_clean_state_suppression_across_all(clean_state):
    r1 = RiskBoundedPrototype()
    r2 = CleanGatedPrototype()
    r3 = HarmAwarePrototype()

    act1, meta1 = r1.select_action(clean_state)
    act2, meta2 = r2.select_action(clean_state)
    act3, meta3 = r3.select_action(clean_state)

    assert act1 == Action.STOP
    assert act2 == Action.STOP
    assert act3 == Action.STOP


def test_blurry_state_intervention_trigger(blurry_state):
    r1 = RiskBoundedPrototype(kappa=0.10)
    r2 = CleanGatedPrototype()
    r3 = HarmAwarePrototype()

    act1, _ = r1.select_action(blurry_state)
    act2, _ = r2.select_action(blurry_state)
    act3, _ = r3.select_action(blurry_state)

    assert act1 in [Action.REGROUND, Action.REEXEC, Action.REPLAN]
    assert act2 in [Action.REGROUND, Action.REEXEC, Action.REPLAN]
    assert act3 in [Action.REGROUND, Action.REEXEC, Action.REPLAN]


def test_safe_abstention_on_hopeless_state(hopeless_state):
    r1 = RiskBoundedPrototype(kappa=1.5, tau_safe=0.40)
    r2 = CleanGatedPrototype(tau_safe=0.40)
    r3 = HarmAwarePrototype(lambda_harm=5.0, tau_safe=0.40)

    # With high conservatism / unviable actions on hopeless state, controllers safely abstain
    act1, _ = r1.select_action(hopeless_state)
    act2, _ = r2.select_action(hopeless_state, remaining_budget=0)
    act3, _ = r3.select_action(hopeless_state)

    assert act1 == Action.ABSTAIN
    assert act2 == Action.ABSTAIN
    assert act3 == Action.ABSTAIN


def test_budget_exhaustion(blurry_state):
    r1 = RiskBoundedPrototype()
    # Zero remaining budget forces STOP or ABSTAIN
    act1, _ = r1.select_action(blurry_state, remaining_budget=10)
    assert act1 in [Action.STOP, Action.ABSTAIN]
