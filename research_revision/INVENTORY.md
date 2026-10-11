# Comprehensive Repository Inventory & Provenance Record

**Date:** October 11, 2026  
**Git Branch:** `naacl_master_loop_audit` (Commit: `2f92f78`)  
**Auditor:** Agent F (Research Software Engineer) & Agent E (Experimental Scientist)  
**Location:** `research_revision/INVENTORY.md`

---

## 1. Primary Repository Structure

```
c:\Users\user\Desktop\recent_projects\ESWA_ehte\
├── 2508.03404v2.pdf                 # MACT Base Paper (Yu et al., 2025, arXiv:2508.03404v2)
├── naacl2021_revised_v13.pdf        # STRAND Presentation & Style Reference (Anonymous, 2026)
├── ESWA_old.pdf                     # Historical ESWA baseline draft
├── GVoC_ESWA_Full_Paper.pdf         # Historical full-length paper draft
├── discovery/                       # Live validation, diagnostic probes, and audits
│   ├── live_validation/             # 100-instance pilot evaluation & audit scripts
│   │   ├── live_evaluation.db       # FROZEN SQLite DB (100 instances, 300 calls on Pixtral-12B)
│   │   ├── diagnostic_experiment/   # 12-instance prompt/budget diagnostic probe
│   │   │   └── diagnostic_evaluation.db # FROZEN SQLite DB (12 instances, 60 calls)
│   │   └── confirmatory_experiment/ # 20-instance exploratory probe (100% overlap with pilot)
│   │       └── confirmatory_evaluation.db # FROZEN SQLite DB (20 instances, 100 calls)
│   └── audit_scripts/               # Forensic scripts for crop failures, truncation, and McNemar tests
├── gvoc_engine/                     # Core simulation & decision engine
│   ├── benchmark/                   # 16k synthetic diagnostic dataset generator
│   ├── controllers/                 # GVoC router, baselines, risk-bounded router
│   ├── core/                        # POMDP state, action space, database schemas
│   ├── experiments/                 # Full 16k benchmark execution scripts
│   └── gvoc_evaluation.db           # Master 16k diagnostic simulation database
├── naacl/                           # NAACL LaTeX manuscript, styles, and figures
│   ├── main.tex                     # Primary LaTeX source (4-page short paper + references + app)
│   ├── custom.bib                   # Bibliography (35 verified references)
│   ├── naacl2021.sty                # Official NAACL style package
│   ├── acl_natbib.bst               # Official BibTeX style
│   ├── check_pages.py               # Page budget verification script
│   ├── figures/                     # 6 publication-grade figures (300 DPI)
│   └── main.pdf                     # Compiled manuscript PDF
├── research/                        # Historical Phase 1 audit & spec files
└── research_revision/               # ACTIVE REVISION ARTIFACTS & AUDIT LOGS
```

---

## 2. Evidence Classification & Cryptographic Provenance

Every dataset, database, and numerical claim is classified into its strict evidentiary category:

| Artifact Path | Size (Bytes) | SHA-256 (Prefix) | Evidentiary Class | Status & Role |
| :--- | :--- | :--- | :--- | :--- |
| `gvoc_engine/gvoc_evaluation.db` | 5,099,520 | `6690c9b3aa111b35...` | **Offline Simulation** | 16,000 synthetic diagnostic episodes; counterfactual perturbations across 4 VLM profiles. |
| `discovery/live_validation/live_evaluation.db` | 544,768 | `a6fa89be48304fe8...` | **Live Model Evaluation** | 100 genuine visual documents evaluated on Mistral Pixtral-12B API (300 calls). |
| `discovery/live_validation/diagnostic_experiment/diagnostic_evaluation.db` | 40,960 | `5e9f80366cf4aeca...` | **Live Diagnostic Probe** | 12 selected instances under 5 prompt/budget conditions (60 calls). Isolates truncation. |
| `discovery/live_validation/confirmatory_experiment/confirmatory_evaluation.db` | 77,824 | `495e0c243679dfc3...` | **Exploratory Probe** | 20 instances across 5 image/prompt conditions (100 calls). 100% overlap with pilot. |
| `naacl/main.tex` | 52,290 | `aeb61bc13daae851...` | **Manuscript Source** | Main text strictly $\le 4$ pages; qualified causal statements. |
| `naacl/custom.bib` | 58,062 | `1394a9eaf31a53bb...` | **Bibliography** | 35 verified citations from authoritative sources. |
| `2508.03404v2.pdf` | 1,377,439 | `8c5449119489a7e9...` | **Published Literature** | MACT base paper (Yu et al., arXiv:2508.03404v2). |
| `naacl2021_revised_v13.pdf` | 1,843,184 | `df8944bf7b1ee74a...` | **Published Literature** | STRAND style reference paper (Anonymous, NAACL 2021 format). |

---

## 3. Tool & Execution Environment

- **Operating System:** Windows 11 Pro (Build 26100)
- **Shell:** PowerShell
- **Python:** Python 3.13.0
- **LaTeX Engine:** MiKTeX `pdflatex` (pdfTeX 3.141592653-2.6-1.40.26)
- **BibTeX:** 0.99d
