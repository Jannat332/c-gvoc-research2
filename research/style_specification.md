# Style Specification: Lessons from STRAND Reference Paper

**Reference Document:** `naacl2021_revised_v13.pdf` ("STRAND: Detecting Unsupported Causal Inferences in LLMs")  
**Target Paper:** "Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding" (NAACL Short Paper Track)  
**Date:** October 10, 2026

---

## 1. High-Level Narrative Architecture

STRAND achieves exceptional clarity and persuasive power by adhering to an invariant 8-step narrative progression:
1. **The Real-World Dilemma:** Starts with an intuitive, non-jargony high-stakes situation (e.g. emergency management, autonomous coordination).
2. **The Concrete Blindspot / Failure:** Highlights an exact flaw where standard tools fail completely (e.g., true facts combined into an invented causal connection; standard fact-checkers raise no alarm because every fact is true).
3. **The Motivating Before-and-After Example (Page 2, Table 1):** Illustrates the dilemma with a clean, concrete 3-4 row table before any complex mathematics or architecture is described.
4. **The Research Question:** Formulates a single sharp question (e.g., "When facts are true, how do we prevent models from inventing unsupported links?").
5. **Modular Method Exposition (Section 2):** Divides the solution into 3 intuitive, sequentially linked modules ("Module 1: The Quick Screen", "Module 2: The Graph Audit", "Module 3: The Fix").
6. **Equation followed by Plain-Language Intuition:** Immediately glosses formal mathematical terms in accessible conversational English ("In plain terms, the numerator measures...").
7. **Empirical Results Organized Around Clear Takeaways:** Presents clean, legible tables and figures (Table 2, Table 3, Figure 2) that directly answer the core questions without visual clutter.
8. **Explicit Discussion of Trade-offs & Limitations:** Openly identifies failure boundaries (attackers pacing claims slowly, open vs. closed models, latency distribution).

---

## 2. Adaptation to Our Paper (GVoC / Observation-Space Scaling)

### A. Narrative Flow for "Think Longer or Look Closer?"
- **The Real-World Dilemma:** Reading fine print on invoices, lab reports, or medical prescriptions where a tiny decimal point, minus sign, or dosage is crucial.
- **The Concrete Blindspot:** Downsampling physically erases fine characters or small table borders. Existing methods force models to "think longer" in reasoning space (generating long chains of thought or multi-agent debate), but deliberating over missing pixels only produces confident hallucinations.
- **The Motivating Before-and-After Example (Table 1 / Teaser):**
  - *Input:* Prescription / invoice with tiny print blurred under standard resolution.
  - *Standard Approach (Monolithic / MACT):* Deliberates over blurred pixels $\to$ hallucinates wrong value (e.g., 50 mg instead of 0.5 mg) using 350+ tokens.
  - *GVoC Approach:* Evaluates that observation evidence is ambiguous $\to$ triggers localized high-resolution re-grounding $\to$ acquires native pixels $\to$ extracts exact value ("0.5 mg") in 15 tokens.
- **The Research Question:** *"When a vision-language model is uncertain about a visual document, should it think longer, or should it look closer?"*
- **Modular Method Breakdown:**
  - *Module 1: State & Action Space* (Stop, Re-Ground Crop, Re-Execute Table, Abstain).
  - *Module 2: Grounded Value-of-Compute Gating* (Balancing expected accuracy gain against token cost).
  - *Module 3: Spatial Context Preservation & Verification* (Ensuring crops preserve necessary peripheral context and bounding-box attribution).
- **Mathematical Clarity:**
  - Define Intervention Value $\mathcal{V}(s, a)$ clearly.
  - State Data Processing Inequality (DPI) with explicit Markov assumptions ($Y^* \to X_{\text{high}} \to X_{\text{low}} \to T$) as an information-theoretic bound on reasoning, not an algorithmic proof.
  - State Proposition 1 as a stylized perturbation bound under uniform error bounds.
- **Experimental Exposition:**
  - Clearly separate the offline 16,000-query benchmark simulation from the live model evaluations.
  - Transparently report the 100-instance live pilot (Mistral Pixtral-12B), highlighting the Truncation Ceiling Trap and the Grounding Prerequisite.

---

## 3. Formatting & Aesthetic Guidelines

| Element | Reference Standard (STRAND) | Implementation in NAACL Submission |
| :--- | :--- | :--- |
| **Length** | Exactly 4 pages of main text. | `naacl/check_pages.py` verified; pages 1–4 main text, page 5 references, pages 6+ appendix. |
| **Typography** | Times, clean microtype, compact headers. | `microtype`, `times`, proper section spacing. |
| **Tables** | Booktabs, alternating row stretch (0.88–0.92), bold headers, clear metric arrows ($\uparrow, \downarrow$). | Professional booktabs styling across all tables. |
| **Figures** | Clean vector/high-res raster, high contrast, readable font size ($\ge 8$ pt in print), comprehensive captions answering: What is shown? What to look at? What is the takeaway? What does it mean? | Ensure Fig 1, Fig 2, Fig 3 have self-contained 4-part captions. |
| **Citations** | Approximately 35 relevant, fully verified citations in `custom.bib`. | Verified bibliographic records with zero hallucinated entries. |

---

## 4. Tone and Vocabulary Checklist

- **Prohibited Words:** "revolutionary", "groundbreaking", "decisively outperforms", "proves that GVoC succeeds", "eliminates all errors", "universal guarantee".
- **Approved Precise Phrasing:** "improves sample accuracy by", "empirically reduces intervention frequency", "provides an information-theoretic upper bound", "under the assumed uniform bounds", "in our evaluated pilot sample".
