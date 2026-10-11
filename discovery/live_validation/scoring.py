"""
Standardized Scoring Module for Visual Document Understanding.
Implements:
1. Exact Match after standard punctuation & whitespace normalization.
2. Token-level F1 overlap.
3. Relaxed Substring / Numeric equivalence.
"""

import re
import string

def normalize_text(text: str) -> str:
    """Lowercases, removes punctuation, and collapses whitespace."""
    if not text:
        return ""
    text = str(text).lower()
    # Strip common currency and percentage symbols
    text = re.sub(r'[\$,%]', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Collapse whitespace
    text = ' '.join(text.split())
    return text

def compute_token_f1(pred: str, gt: str) -> float:
    p_tokens = normalize_text(pred).split()
    g_tokens = normalize_text(gt).split()
    if not p_tokens or not g_tokens:
        return 1.0 if p_tokens == g_tokens else 0.0
    
    common = set(p_tokens) & set(g_tokens)
    if not common:
        return 0.0
    
    p_count = sum(min(p_tokens.count(w), g_tokens.count(w)) for w in common)
    precision = p_count / len(p_tokens)
    recall = p_count / len(g_tokens)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1

def score_vdu_answer(pred: str, ground_truth_list: list) -> tuple:
    """
    Evaluates prediction against ground-truth list.
    Returns: (best_f1, is_correct) where is_correct is 1 if exact normalized match or f1 >= 0.5.
    """
    if not ground_truth_list:
        return 0.0, 0
    
    norm_pred = normalize_text(pred)
    best_f1 = 0.0
    is_correct = 0

    for gt in ground_truth_list:
        norm_gt = normalize_text(str(gt))
        if norm_pred == norm_gt or (norm_gt and norm_gt in norm_pred) or (norm_pred and norm_pred in norm_gt):
            is_correct = 1
            best_f1 = 1.0
            break
        f1 = compute_token_f1(pred, str(gt))
        if f1 > best_f1:
            best_f1 = f1
        if f1 >= 0.5:
            is_correct = 1

    return best_f1, is_correct
