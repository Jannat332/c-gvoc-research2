Overleaf & OpenReview Upload Package - NAACL Submission
Paper: Grounded Value-of-Compute: Cost-Aware Process Intervention for Reliable Visual Document Understanding (GVoC)
Format: NAACL-HLT (Two-Column ACL Style)

================================================================================
PACKAGE CONTENTS
================================================================================
- main.tex: Primary NAACL LaTeX source document (with Anonymous Authors for double-blind review).
- main.bbl: Pre-compiled BibTeX database for 1-click single-pass compilation.
- naacl2021.sty: Official NAACL style definitions (with line numbering in review mode).
- acl_natbib.bst: Official ACL Natbib bibliography style file.
- custom.bib: Complete BibTeX bibliography database.
- anthology.bib: Auxiliary ACL Anthology bibliography reference file.
- figures/: High-resolution diagram assets and empirical evaluation charts:
    * fig1_motivational_teaser.png (Motivational comparison: Monolithic vs. MACT vs. GVoC)
    * fig2_gvoc_architecture.png (GVoC Architecture & Value-of-Compute Interventions)
    * fig3_pareto_frontier.png (Accuracy vs. Token Cost Pareto Frontier)
    * fig4_regret_comparison.png (Counterfactual Oracle Decision Regret)
    * fig5_action_distribution.png (Discrete Repair Action Distribution)
    * fig6_qualitative_cases.png (Qualitative Forensic Success/Failure Cases)
- main.pdf: Compiled publication-grade PDF generated via pdfLaTeX.

================================================================================
OVERLEAF SETUP INSTRUCTIONS
================================================================================
1. In Overleaf, click "New Project" -> "Upload Project".
2. Select the packaged .zip archive (e.g., overleaf_package_gvoc_naacl.zip).
3. Overleaf automatically selects 'main.tex'.
4. Compiler: pdfLaTeX (TeX Live 2021 or later).
5. Output: Formatted according to official NAACL double-blind submission guidelines.

================================================================================
LOCAL COMPILATION
================================================================================
To compile from terminal:
    pdflatex main.tex
    bibtex main
    pdflatex main.tex
    pdflatex main.tex
