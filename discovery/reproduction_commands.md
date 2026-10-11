# Exact Reproduction Commands

**Project:** *Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding*  
**Environment:** Python 3.13.0, MiKTeX `pdflatex` on Windows x64  
**Date:** 2026-10-10

---

## 1. Test Suite Verification (16 Unit Tests)
To run the full unit test suite (covering paired state alignment, uncertainty dynamics, budget exhaustion, clean-state gating, and safe abstention):
```bash
python -m pytest -v
```
*Expected Output:* `16 passed in ~0.12s`.

---

## 2. Decisive Prototype Head-to-Head Benchmark
To run the decisive head-to-head comparison across all candidates, baselines, and oracle on the 40 paired diagnostic scenarios with 95% bootstrap confidence intervals:
```bash
python -m discovery.experiments.run_candidate_head_to_head
```
*Expected Output:*
- Prints full benchmark performance table (Accuracy, Tokens, Normalized Regret $[0, 1]$, Harm %, Type-I %, Latency ms).
- Prints stratified Validation ($N=20$) vs Held-Out Test ($N=20$) table.
- Saves results to `discovery/experiments/benchmark_results.json`.
- Runtime: $< 2$ seconds on CPU.

---

## 3. Full 16,000-Episode Simulation Runner
To re-execute the 16,000-episode simulated benchmark across all 4 models and 4 VDU datasets:
```bash
python -m gvoc_engine.experiments.run_full_16k_benchmark
```
*Expected Output:*
- Evaluates 96,000 action inferences.
- Commits records to `gvoc_engine/gvoc_evaluation.db`.
- Prints Table 1, Table 2 (Model breakdowns), and Table 3 (Domain breakdowns).
- Runtime: $\approx 20$ seconds on CPU.

---

## 4. LaTeX Manuscript Compilation & Page Count Verification
To compile the LaTeX source and verify that the main body strictly satisfies the 4-page NAACL Short Paper limit:
```powershell
cd naacl
pdflatex -interaction=nonstopmode main.tex
python check_pages.py
```
*Expected Output:*
- `Total pages: 12`
- Page 4 ends cleanly before References.
- Page 5 starts with `References`.
- Page 7 starts with `Appendix A`.
