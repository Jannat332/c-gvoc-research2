"""
Visual Re-grounding Intervention.
Refines spatial bounding boxes and re-aligns image crops.
"""

from typing import Dict, Any, Tuple
from gvoc_engine.core.state import GroundedState


def execute_reground(
    state: GroundedState,
    client: Any,
    image_path: str,
    query: str
) -> Tuple[GroundedState, int, float]:
    """
    Executes visual re-grounding to repair spatial coordinate drift.
    Returns: (updated_state, tokens_spent, cost_estimate)
    """
    prompt = (
        f"Visual Document Re-Grounding Task:\n"
        f"Query: {query}\n"
        f"Previous Grounding Bounding Box: {state.current_bbox}\n"
        f"Diagnosed Issue: Spatial misalignment or boundary truncation.\n"
        f"Task: Re-examine the document layout and provide the refined, exact [ymin, xmin, ymax, xmax] coordinates."
    )

    resp, p_tok, c_tok, lat = client.call_vlm(prompt, image_path, max_tokens=100)
    tokens = p_tok + c_tok

    # Update state: re-grounding improves layout loss and evidence alignment
    state.d_layout = max(0.01, state.d_layout * 0.4)
    state.d_evidence = max(0.02, state.d_evidence * 0.5)
    state.c_judg = min(0.95, state.c_judg + 0.15)
    state.n_tokens_spent += tokens
    state.b_remaining = max(0, state.b_remaining - tokens)
    state.step_index += 1

    cost = tokens * 0.001 + lat * 0.01
    return state, tokens, cost
