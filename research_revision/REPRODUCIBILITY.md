# Master Reproducibility Guide & Execution Commands

**Date:** October 11, 2026  
**Auditor:** Agent F (Research Software Engineer)  
**Location:** `research_revision/REPRODUCIBILITY.md`

---

## 1. Environment & Software Stack

- **Operating System:** Windows 11 Pro / Linux compatible
- **Python Version:** Python 3.11+ (Tested on Python 3.13.0)
- **LaTeX Distribution:** MiKTeX / TeX Live (`pdflatex`, `bibtex`)
- **Key Python Libraries:**
  - `numpy`, `scipy`, `pandas`
  - `lightgbm` (Dual-head advantage predictor)
  - `sqlite3` (Telemetry database engine)
  - `pypdf` (Automated PDF page count & text extraction)
  - `pillow`, `matplotlib` (Image processing and visualization)

---

## 2. Frozen Database Artifacts

| Database | Rows / Scope | Cryptographic SHA-256 Checksum | Command to Inspect |
| :--- | :--- | :--- | :--- |
| `gvoc_engine/gvoc_evaluation.db` | 16,000 queries | `6690c9b3aa111b35b6fa723f5480ba086786ee461bcfa07153a8080f4886e0fc` | `python gvoc_engine/experiments/run_full_16k_benchmark.py` |
| `discovery/live_validation/live_evaluation.db` | 100 instances | `a6fa89be48304fe885b54bb46571439247c7c0062a4d33eb43cb8d7ce8718873` | `python discovery/live_validation/independent_analysis.py` |
| `discovery/live_validation/diagnostic_experiment/diagnostic_evaluation.db` | 12 instances | `5e9f80366cf4aeca542848c66e27931f60fa0d65b1aa9224483ae89be6bfbfd4` | `python discovery/live_validation/audit_scripts/analyze_diagnostic_results.py` |
| `discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db` | 20 instances | `495e0c243679dfc303f83d02462e2ffb28cb487fef4045f3a0972fe01804b901` | `python discovery/live_validation/audit_scripts/analyze_confirmatory_results.py` |

---

## 3. End-to-End Reproduction Commands

### Command 1: Reproduce Master 16k Benchmark Simulation Results
```powershell
python gvoc_engine/experiments/run_full_16k_benchmark.py
```
*Expected Output:* Master accuracy 70.2%, 274 tokens/query, oracle regret 0.061.

### Command 2: Recompute Live Pilot McNemar Contingency Tables
```powershell
python discovery/live_validation/independent_analysis.py
```
*Expected Output:* Monolithic (82.0%), GVoC (72.0%, $p = 0.0129$), C-GVoC (76.0%, $p = 0.1460$).

### Command 3: Audit Prompt Truncation Effects ($N=12$)
```powershell
python discovery/live_validation/audit_scripts/analyze_diagnostic_results.py
```
*Expected Output:* Truncation rate drops from 58.3% to 0.0% under format-constrained decoding ($p = 0.0078$).

### Command 4: Audit Clean Crop vs. Downsample Contrast ($N=20$)
```powershell
python discovery/live_validation/audit_scripts/analyze_confirmatory_results.py
```
*Expected Output:* Downsampled (60.0%) vs. Center Crop (25.0%), $p = 0.0391$ McNemar exact test.

### Command 5: Compile NAACL LaTeX Manuscript & Audit Page Limits
```powershell
cd naacl
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python check_pages.py
```
*Expected Output:* 0 errors; main text ends strictly on page 4, references on pages 5-6, appendices on pages 7-12.
