# Complete Reproducibility Guide & Execution Commands

**Document:** `research/REPRODUCIBILITY.md`  
**Date:** October 10, 2026  
**Auditor:** Reproducibility & Software Engineer

---

## 1. System Environment & Dependencies

- **OS:** Windows 11 / Linux compatible
- **Python Version:** Python 3.11+ (Tested on Python 3.13.0)
- **LaTeX Distribution:** TeX Live / MiKTeX (`pdflatex`, `bibtex`)
- **Key Python Packages:**
  - `numpy`, `scipy`, `pandas`
  - `lightgbm` (Dual-head advantage estimator)
  - `sqlite3` (Database telemetry persistence)
  - `pypdf` (PDF rendering & page audits)
  - `pillow`, `matplotlib` (Image cropping and visualization)

---

## 2. Frozen Data Artifacts & Cryptographic Verification

All databases are frozen and checksummed:

| Database File | Instances | Calls | SHA-256 Checksum (Prefix) | Provenance |
| :--- | :--- | :--- | :--- | :--- |
| `discovery/live_validation/live_evaluation.db` | 100 | 300 | `a6fa89be...` | Live Mistral Pixtral-12B API evaluation |
| `discovery/live_validation/diagnostic_experiment/diagnostic_evaluation.db` | 12 | 60 | `01e8c07e...` | Prompt & token ceiling diagnostic probe |
| `discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db` | 20 | 100 | `b99fbdcb...` | Exploratory factorial image/prompt probe |
| `gvoc_engine/gvoc_evaluation.db` | 16,000 | 96,000 | `4f32a768...` | Diagnostic benchmark simulation database |

---

## 3. Reproduction Commands

### A. Regenerate 16,000-Query Benchmark Results & Regret Analysis
```bash
python gvoc_engine/experiments/run_full_16k_benchmark.py
```
Outputs master accuracy (70.2%), token count (274), and oracle regret (0.061) across DocVQA, ChartQA, TableBench, and MMLongBench.

### B. Audit Live 100-Instance Pilot Telemetry
```bash
python discovery/live_validation/independent_analysis.py
```
Recomputes exact paired McNemar contingency tables for Monolithic (82.0%), GVoC (72.0%), and C-GVoC (76.0%).

### C. Audit Diagnostic Prompt Ceiling Effects ($N=12$)
```bash
python discovery/live_validation/audit_scripts/analyze_diagnostic_results.py
```
Demonstrates that format-constrained concise decoding restores 100% completion without truncation.

### D. Audit Factorial Image/Prompt Probe ($N=20$, Exploratory)
```bash
python discovery/live_validation/audit_scripts/analyze_confirmatory_results.py
```
Evaluates the clean contrast: Center Crop (C4, 25.0%) vs. Downsampled (C2, 60.0%) under matched concise prompts ($p = 0.0391$).

### E. Compile NAACL Manuscript & Verify Page Budget
```bash
cd naacl
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python check_pages.py
```
Verifies that main text occupies strictly $\le 4$ pages, followed by references and appendices.

---

## 4. Known Blockers & Resource Constraints

1. **API Cost Gate:** Further live API calls on commercial providers (Mistral, OpenAI, Anthropic) are halted under Option A to avoid unbudgeted expenditure.
2. **Native Resolution Requirement:** Re-grounding requires access to uncompressed document pixels; when only downsampled thumbnails are provided by external servers, observation scaling falls back to stopping or abstention.
