# Formal Method Specification: Grounded Value-of-Compute (GVoC)

**Document:** `research/METHOD_SPEC.md`  
**Date:** October 10, 2026  
**Auditors:** Algorithm Designer, Mathematical Auditor, ML Systems Engineer

---

## 1. Problem Formulation and Inference State

We formulate visual document question answering at test time as a sequential decision process over computational modalities.

### State Representation
At inference step $t$, the state is defined as a tuple:
$$s = (I_{\text{low}}, \mathcal{Q}, y_0, \mathcal{E}, b)$$
where:
- $I_{\text{low}} \in \mathbb{R}^{H \times W \times 3}$: The globally downsampled overview image of the document (fixed resolution, e.g. $512 \times 512$ or standard VLM patch budget).
- $\mathcal{Q}$: The input natural-language question.
- $y_0$: The initial zero-shot candidate answer generated from $(I_{\text{low}}, \mathcal{Q})$.
- $\mathcal{E}$: The accumulated visual and textual evidence acquired during previous steps.
- $b \in \mathbb{R}_+$: The remaining test-time token or monetary budget.

---

## 2. Test-Time Action Space $\mathcal{A}$

At any non-terminal state, the controller selects an action $a \in \mathcal{A} = \{a_{\text{stop}}, a_{\text{reground}}, a_{\text{reexec}}, a_{\text{abstain}}\}$:

1. **Stop ($a_{\text{stop}}$):**
   Emit the candidate answer $y_0$ immediately. Incurs zero additional intervention compute ($C(s, a_{\text{stop}}) = 0$).
2. **Re-Ground ($a_{\text{reground}}$):**
   Extract a native-resolution sub-crop $I_{\text{high}} \cap \text{BBox}(q)$ around the queried region using spatial coordinate localization. Feed the high-resolution crop to the vision encoder under format-constrained concise decoding ($B_{\text{out}} \le 60$). Incurs marginal cost $C(s, a_{\text{reground}}) \approx 60\text{--}120$ tokens.
3. **Re-Execute ($a_{\text{reexec}}$):**
   Trigger structured programmatic table parsing or OCR grid alignment to resolve complex row-column coordinates. Incurs marginal cost $C(s, a_{\text{reexec}}) \approx 180\text{--}240$ tokens.
4. **Abstain ($a_{\text{abstain}}$):**
   Safely withhold answering and output a refusal symbol $\bot$ when the evidence is unrecoverable or occluded. Incurs nominal token cost $C(s, a_{\text{abstain}}) \approx 10\text{--}20$ tokens.

---

## 3. Grounded Value-of-Compute (GVoC) Decision Objective

To decide whether spending additional compute is economically justified, the controller evaluates the **Cost-Normalized Intervention Value**:

$$\mathcal{V}(s, a) = \frac{\hat{\Delta P}_a(s) - \lambda \hat{\sigma}_a(s)}{C(s, a) + \epsilon}$$

where:
- $\hat{\Delta P}_a(s) = \hat{P}(Y=1 \mid s, a) - \hat{P}(Y=1 \mid s, a_{\text{stop}})$ is the estimated marginal gain in correctness probability over stopping immediately.
- $\hat{\sigma}_a(s) \ge 0$ is an epistemic dispersion or uncertainty penalty (used in conservative C-GVoC with penalty multiplier $\lambda \ge 0$).
- $C(s, a) > 0$ is the estimated incremental token cost of executing action $a$.
- $\epsilon = 10^{-4}$ is a small numerical stabilizer.

### Decision Rule
The optimal action is selected as:
$$a^* = \begin{cases}
\arg\max_{a \in \mathcal{A} \setminus \{a_{\text{stop}}\}} \mathcal{V}(s, a) & \text{if } \max_{a \neq a_{\text{stop}}} \mathcal{V}(s, a) > \tau_{\text{thresh}} \\
a_{\text{stop}} & \text{otherwise}
\end{cases}$$
where $\tau_{\text{thresh}} > 0$ is the threshold above which expected correctness gain justifies the token expense.

---

## 4. Verification and Context-Preservation Constraints

### A. Format-Constrained Concise Decoding
To avoid the **Truncation Ceiling Trap** (where verbose reasoning preambles consume the entire completion budget and truncate the answer), all intervention prompts enforce concise formatting:
```
System: You are an expert document reader. Inspect the provided image crop.
User: Question: {Q}
Answer directly with the exact value or phrase only. Do not explain or repeat the question.
```

### B. Spatial Context Preservation Check
To avoid the **Grounding Prerequisite Failure** (where unguided crops sever headers, page numbers, or axes):
- The crop bounding box $\text{BBox}$ must be grounded via attention attribution or question entity localization.
- If the target entity lies on an axis, table header, or margin, the crop bounding box is expanded by a context margin $\delta_{\text{margin}} = 20\%$ to preserve reference labels.

---

## 5. Complete Algorithm Pseudocode

```python
def gvoc_controller(document_image, question, budget, tau_thresh=1e-4, lambda_pen=0.1):
    # Step 1: Initial Zero-Shot Monolithic Read
    y_0, conf_0, tokens_0 = vlm_zero_shot(document_image, question)
    
    # Check if budget is exhausted
    if budget <= tokens_0:
        return y_0, tokens_0
        
    s = construct_state(document_image, question, y_0, conf_0)
    
    # Step 2: Evaluate Candidate Interventions
    candidate_actions = ["reground", "reexec", "abstain"]
    best_action = "stop"
    best_value = 0.0
    
    for a in candidate_actions:
        delta_p, sigma, cost = estimate_counterfactual_value(s, a)
        
        # Check context preservation validity
        if a == "reground" and not verify_spatial_grounding(s):
            continue  # prune ungrounded blind crops
            
        value = (delta_p - lambda_pen * sigma) / (cost + 1e-4)
        if value > best_value and value > tau_thresh and cost <= (budget - tokens_0):
            best_value = value
            best_action = a
            
    # Step 3: Execute Selected Action
    if best_action == "stop":
        return y_0, tokens_0
    elif best_action == "reground":
        crop_img = extract_grounded_crop(document_image, question)
        y_final, tokens_int = vlm_concise_inference(crop_img, question)
        return y_final, tokens_0 + tokens_int
    elif best_action == "reexec":
        y_final, tokens_int = parse_and_reexecute_table(document_image, question)
        return y_final, tokens_0 + tokens_int
    elif best_action == "abstain":
        return "REFUSAL (evidence insufficient)", tokens_0 + 10
```

---

## 6. Computational Complexity & Controller Overhead

- **Inference Overhead:** The dual-head advantage estimator is implemented as a lightweight gradient-boosted decision ensemble (LightGBM, model size $< 2$ MB). Feature extraction consumes $< 1.2$ ms on CPU.
- **VLM Calls:** Maximum of 2 calls per query (initial overview + at most 1 targeted intervention), strictly bounding test-time latency compared to iterative loops (e.g., MACT's up to $3 \times 4 = 12$ agent calls).
