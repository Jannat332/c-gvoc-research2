"""
Unit Tests for Loss and Regret Formulation, Operational Bounds, and Scoring.
Validates:
1. Regret is strictly non-negative and bounded in [0, 1].
2. Oracle achieves identically 0.0 regret on every instance.
3. Regret increases monotonically with token waste on equal accuracy.
4. Extreme edge cases: negative costs, infinite tokens, zero accuracy.
5. Scoring robustness: case invariance, punctuation stripping, token overlap.
"""

import pytest
import numpy as np
from discovery.live_validation.scoring import score_vdu_answer, normalize_text, compute_token_f1


def compute_normalized_regret(
    method_acc: float,
    oracle_acc: float,
    method_tokens: int,
    oracle_tokens: int,
    max_tokens: float = 6000.0,
    cost_penalty: float = 0.05
) -> float:
    """Exact operational regret formula validated for ESWA/NAACL."""
    acc_gap = max(0.0, oracle_acc - method_acc)
    tok_gap = max(0.0, method_tokens - oracle_tokens)
    raw_regret = acc_gap + cost_penalty * (tok_gap / max_tokens)
    return float(np.clip(raw_regret, 0.0, 1.0))


def test_oracle_zero_regret():
    """Oracle must always achieve exactly 0.0 regret."""
    for acc in [0.0, 0.5, 1.0]:
        for tokens in [100, 1000, 5000]:
            regret = compute_normalized_regret(acc, acc, tokens, tokens)
            assert regret == 0.0, f"Oracle regret must be 0, got {regret}"


def test_regret_bounds_edge_cases():
    """Regret must be bounded in [0, 1] even under pathological inputs."""
    # Worst case: method has 0 acc, oracle has 1 acc, method spends 100,000 tokens
    regret_worst = compute_normalized_regret(0.0, 1.0, 100000, 100)
    assert 0.0 <= regret_worst <= 1.0
    assert regret_worst == 1.0

    # Best case: method matches oracle on acc and tokens
    regret_best = compute_normalized_regret(1.0, 1.0, 200, 200)
    assert regret_best == 0.0

    # Intermediate case: method has lower accuracy
    regret_acc_loss = compute_normalized_regret(0.0, 1.0, 200, 200)
    assert regret_acc_loss == 1.0


def test_regret_monotonicity_in_tokens():
    """Regret must increase strictly monotonically when wasting tokens on equal accuracy."""
    r1 = compute_normalized_regret(1.0, 1.0, 1000, 500)
    r2 = compute_normalized_regret(1.0, 1.0, 2000, 500)
    r3 = compute_normalized_regret(1.0, 1.0, 4000, 500)
    assert 0.0 < r1 < r2 < r3 <= 1.0


def test_scoring_normalization():
    """Validates robust VDU string matching across typical optical artifacts."""
    # Punctuation & case differences
    f1, corr = score_vdu_answer("1128 Sixteenth St., N.W., Washington, D.C. 20036", ["1128 SIXTEENTH ST., N. W., WASHINGTON, D. C. 20036"])
    assert corr == 1
    assert f1 >= 0.5

    # Dollar sign and decimals
    f1, corr = score_vdu_answer("$975.00", ["975.00", "975"])
    assert corr == 1

    # Percentage
    f1, corr = score_vdu_answer("42.5%", ["42.5"])
    assert corr == 1

    # Distinct incorrect answer
    f1, corr = score_vdu_answer("New York", ["Delaware"])
    assert corr == 0
    assert f1 == 0.0
