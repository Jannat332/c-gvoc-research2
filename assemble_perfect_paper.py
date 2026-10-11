import subprocess
import os

with open('naacl/main.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Preamble extraction
pos_doc = content.find(r'\begin{document}')
preamble = content[:pos_doc]

# Tight float spacing in preamble
spacing_params = r"""
\setlength{\textfloatsep}{4pt plus 1pt minus 1pt}
\setlength{\dbltextfloatsep}{4pt plus 1pt minus 1pt}
\setlength{\floatsep}{3pt plus 1pt minus 1pt}
\setlength{\dblfloatsep}{3pt plus 1pt minus 1pt}
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.90}
\renewcommand{\dbltopfraction}{0.95}
\renewcommand{\dblfloatpagefraction}{0.90}
"""

if r'\setlength{\textfloatsep}' not in preamble:
    preamble = preamble + '\n' + spacing_params

# Appendix extraction
pos_bib = content.find(r'\bibliographystyle{acl_natbib}')
pos_clear = content.rfind(r'\clearpage', 0, pos_bib)
if pos_clear != -1 and pos_bib - pos_clear < 30:
    appendix_part = content[pos_clear:]
else:
    appendix_part = r'\clearpage' + '\n' + content[pos_bib:]

# Main paper text
main_text = r"""\begin{document}
\maketitle

\begin{abstract}
When Vision-Language Models (VLMs) encounter low-resolution documents, blurred text, or complex tables, standard test-time scaling methods spend inference compute in ``reasoning space''---generating longer chains of thought or multi-agent debate over the same compressed image. However, when visual tokens are physically lost during downsampling, deliberating over absent pixels cannot reconstruct missing information. We investigate whether test-time compute is better spent in \textit{observation space} via \textbf{Grounded Value-of-Compute (\textsc{GVoC})}, dynamically deciding whether to answer immediately, inspect a high-resolution crop, re-parse structured tables, or safely abstain by weighing expected accuracy gains against token costs. 
In an offline 16,000-query counterfactual simulation where inputs are synthetically degraded, selective observation scaling improves accuracy to 70.4\% while using 28.1\% fewer tokens than multi-agent debate (64.4\%). 
However, in a live empirical pilot on 100 genuine visual documents using Mistral Pixtral-12B, intervention-based methods underperformed direct zero-shot inference: direct inference achieved \textbf{82.0\% accuracy at 1,428 tokens}, whereas original \textsc{GVoC} achieved only \textbf{72.0\% accuracy at 2,889 tokens} ($p = 0.013$, $+101\%$ token cost), and a conservative regularizer (C-\textsc{GVoC}) reached \textbf{76.0\% at 1,676 tokens}.
Targeted forensic diagnostics reveal why simulated gains reversed in live deployment: multi-turn intervention prompts collided with token limits (causing truncations in 66.7\% of cases), and unguided cropping severed data values from essential headers and units. Our work demonstrates that while observation scaling is conceptually sound when visual evidence is missing, practical test-time intervention requires format-constrained decoding and context-preserving localization rather than isolated cropping.
\end{abstract}

% Table 1 declared on Page 1 -> floats to top of Page 2
\begin{table*}[t]
\centering
\small
\renewcommand{\arraystretch}{0.88}
\begin{tabularx}{\textwidth}{@{} p{3.2cm} p{3.6cm} p{3.6cm} X @{}}
\toprule
\textbf{Document Type \& Query} & \textbf{Direct / Deliberation Approach} & \textbf{Adaptive Observation Approach} & \textbf{Why Closer Inspection Is Needed} \\
\midrule
\textit{Medical Prescription Scan:} \newline ``What is the dosage?'' \newline (True: \textbf{0.5\,mg}; decimal blurred). & Direct inference sees ``05\,mg''; debate deliberates over blur $\to$ hallucinates ``50\,mg'' (359 tokens). & Controller inspects 300\,DPI native crop $\to$ resolves decimal point: ``0.5\,mg'' (274 tokens). & Deliberation cannot recover optical bits lost to downsampling. Native resolution recovers missing evidence. \\
\midrule
\textit{Financial Earnings Table:} \newline ``What is operating income?'' \newline (True: \textbf{-\$14.2\,M}; parens negative). & Direct zero-shot misses parentheses in downsampled image $\to$ predicts positive ``+\$14.2M''. & Re-execution parser re-aligns row stub and headers $\to$ reads negative ``-\$14.2M''. & Spatial layout alignment prevents sign inversions caused by isolated character misreadings. \\
\bottomrule
\end{tabularx}
\vspace{-2mm}
\caption{\textbf{Motivating Concrete Examples: Why Observation Scaling Is Needed Over Pure Deliberation.} \textit{Note: Conceptual illustrative cases demonstrating the theoretical failure mode of reasoning over downsampled inputs.} When optical signals are missing, generating additional reasoning tokens leads to plausible hallucinations; acquiring targeted visual evidence resolves ambiguity when context is preserved.}
\label{tab:example_cases}
\vspace{-3mm}
\end{table*}

\section{Introduction}
\label{sec:intro}

Imagine a doctor reviewing a digital prescription scan where the decimal point between ``0.5\,mg'' and ``50\,mg'' is blurred into an illegible smudge. Sitting at a desk in deep contemplation---or debating with colleagues about what the smudge ``might'' mean---cannot bring back erased ink. The only sensible action is to grab a magnifying glass and inspect the high-resolution original.

\begin{figure}[t]
\centering
\includegraphics[width=0.56\columnwidth]{figures/fig1_motivational_teaser.png}
\vspace{-2.5mm}
\caption{\textbf{Reasoning vs.\ observation scaling (Conceptual illustration).} Deliberating over blurred evidence cannot recover erased pixels. In contrast, acquiring high-resolution optical evidence resolves visual ambiguity when cost-effective. \textit{Note: Conceptual illustration; token numbers reflect simulation benchmark averages.}}
\label{fig:teaser}
\vspace{-3.5mm}
\end{figure}

Yet modern AI systems often do the opposite. When Vision-Language Models (VLMs) read complex invoices, financial reports, or lab results, images are compressed to fit fixed neural network token grids, causing tiny numbers, minus signs ($-$), or footnotes to physically vanish \citep{cui2021document, mathew2021docvqa, tablebench2024, wang2024mmlongbenchdoc}. Faced with uncertainty, existing methods force the model to ``think harder'' in \textbf{reasoning space}---spending hundreds of tokens on chains of thought or multi-agent debate over the same blurry image \citep{snell2024scaling, yu2025visual, wei2022chain}. But no amount of internal reasoning can recover visual evidence that was never observed; deliberating over absent tokens merely produces convincing hallucinations \citep{liu2024llavanext}.

This fundamental contrast motivates our research question: \textit{When an AI system is uncertain about a visual document, should it think longer, or should it look closer?}

We investigate shifting test-time compute from reasoning space to \textbf{observation space} via \textbf{Grounded Value-of-Compute (\textsc{GVoC})}. At each step, a lightweight controller evaluates four actions: \textbf{stop} if evidence is clear, \textbf{re-ground} on a high-resolution crop (60--120 tokens) if text is blurred, \textbf{re-execute} structured table parsing if layout is complex, or \textbf{abstain} if unrecoverable. Rather than intervening blindly, \textsc{GVoC} guides this choice by estimating the \textbf{counterfactual intervention value}---the estimated accuracy improvement from taking an action compared to taking no action from the exact same state---balancing expected gains against token costs.

\paragraph{Contributions.}
(1)~\textbf{Observation Scaling}: We formalize allocating test-time compute to acquire missing visual evidence rather than generating repetitive reasoning tokens over degraded inputs.
(2)~\textbf{Dual Empirical Evaluation}: Across a 16k-query simulation and a 100-query live pilot (Mistral Pixtral-12B), we document where simulation gains succeed and where live execution fails.
(3)~\textbf{Forensic Bottlenecks}: We identify two critical real-world failure modes that synthetic simulation obscured: prompt token truncation and spatial context destruction from isolated cropping.

\section{Why More Reasoning Cannot Recover Missing Pixels}
\label{sec:why_not_reasoning}

In visual document understanding, errors frequently stem from optical resolution loss rather than logical flaws. When documents are downscaled, fine print falls below the physical resolution needed for recognition. Like an investigator examining a blurred photograph of a license plate, no amount of contemplative debate can recover erased ink; the only rational remedy is to zoom in. Formally, by the Data Processing Inequality \citep{cover1991elements}, linguistic processing over downsampled tokens cannot increase mutual information about erased optical details ($I(Y^*; \mathcal{M}_{\text{text}}(\mathcal{I}_{\text{down}}, \mathcal{Q}) \mid \mathcal{I}_{\text{down}}, \mathcal{Q}) = 0$; Appendix~\ref{app:proofs}). Generating reasoning tokens over absent evidence wastes tokens and induces hallucinations.

\begin{figure}[t]
\centering
\includegraphics[width=0.95\columnwidth]{figures/fig2_gvoc_architecture.png}
\vspace{-2.5mm}
\caption{\textbf{\textsc{GVoC} Decision Architecture.} Stage 1 extracts diagnostic signals (input image, query, and telemetry dispersion). Stage 2 evaluates candidate actions using a conservative cost-benefit ratio ($\mathcal{V}_{\text{LCB}}$). Stage 3 executes the chosen intervention only when estimated gains justify token costs.}
\label{fig:architecture}
\vspace{-3mm}
\end{figure}

% Table 2 declared on Page 2 -> floats to top of Page 3
\begin{table*}[t]
\centering
\footnotesize
\renewcommand{\arraystretch}{0.80}
\begin{tabularx}{\textwidth}{@{} p{3.8cm} c c c X @{}}
\toprule
\textbf{Evaluation Setting \& Method} & \textbf{Acc. (\%)} $\uparrow$ & \textbf{Tokens} $\downarrow$ & \textbf{Regret / Cost} & \textbf{Key Empirical Finding / Role} \\
\midrule
\multicolumn{5}{l}{\textbf{Part A: Live Foundation Model Pilot (Mistral Pixtral-12B, $N = 100$ Unperturbed Genuine Documents)}} \\
\textbf{Direct Zero-Shot Inference} & \textbf{82.0} & \textbf{1,428} & Baseline & \textbf{Best overall accuracy}; zero intervention latency or overhead. \\
Original \textsc{GVoC} (Unconstrained) & 72.0 & 2,889 & $+101\%$ tok & Significant drop ($-10.0$ pts, $p = 0.013$); severe token bloat. \\
Conservative C-\textsc{GVoC} & 76.0 & 1,676 & $+17\%$ tok & Mitigates token waste, but remains 6.0 pts below direct ($p = 0.146$). \\
\midrule
\multicolumn{5}{l}{\textbf{Part B: Offline Policy-Simulation Benchmark ($N = 16,000$ Synthetic Episodes with Modeled Downsampling)}} \\
Monolithic Zero-Shot VLM & 12.5 $\pm$ 0.5 & 250 & Regret 0.875 & Fails catastrophically under synthetic downsampling. \\
Confidence-Based Router & 61.1 $\pm$ 0.8 & 355 & Regret 0.389 & Triggers unneeded interventions on ambiguous boundary cases. \\
Multi-Agent Debate (MACT) & 64.4 $\pm$ 0.7 & 359 & Regret 0.356 & Costly reasoning loops over degraded visual tokens. \\
Deterministic Rule Baseline & \textbf{89.0} $\pm$ 0.5 & 368 & Regret 0.110 & High accuracy but intervenes indiscriminately ($>85\%$ queries). \\
\textsc{GVoC} (Point-Estimate) & 70.2 $\pm$ 0.7$^\dagger$ & 274 & Regret 0.076 & $+5.8$ pts, $-23.7\%$ tokens vs.\ debate ($p < 0.001$). \\
\textbf{C-\textsc{GVoC} (Conservative LCB)} & \textbf{70.4} $\pm$ \textbf{0.7}$^\dagger$ & \textbf{258} & \textbf{Regret 0.052} & \textbf{Lowest simulated regret}; highest efficiency ($-28.1\%$ tokens). \\
Evaluated-Action Oracle ($\mathcal{A}^*$) & 90.3 $\pm$ 0.5 & 344 & Regret 0.000 & Theoretical ceiling across candidate action set. \\
\bottomrule
\end{tabularx}
\vspace{-2.5mm}
\caption{\textbf{Live Pilot Results and Offline Policy-Simulation Results.} \textbf{Part A (Live Pilot):} Direct zero-shot achieves highest accuracy (82\%) at lowest token cost; live interventions degrade accuracy ($-10.0$ pts, $p=0.013$). \textbf{Part B (Offline Simulation):} Under modeled synthetic downsampling, selective observation scaling improves accuracy over debate (+5.8 pts) with 24\%--28\% fewer tokens ($p < 0.001$). \textit{Note: Simulation results are generated by a model of intervention outcomes under synthetic degradation; they are not accuracy measurements from 16,000 live VLM evaluations.}}
\label{tab:main_results}
\vspace{-3mm}
\end{table*}

\section{\textsc{GVoC}: Spend Compute Where It Helps}
\label{sec:method}

We model test-time document understanding as a sequential decision process. At each step, \textsc{GVoC} decides whether to finish the answer or spend compute acquiring better evidence.

\subsection{Four Test-Time Candidate Actions}
At state $s$, the controller evaluates four candidate actions: (1)~\textbf{Stop ($a_{\text{stop}}$)}: evidence is sufficient; emit final answer immediately; (2)~\textbf{Re-Ground ($a_{\text{reground}}$)}: inspect native-resolution crop (60--120 tokens); (3)~\textbf{Re-Execute ($a_{\text{reexec}}$)}: re-parse table structure under coordinate bindings (180--240 tokens); and (4)~\textbf{Abstain ($a_{\text{abstain}}$)}: emit fallback $\bot$ when evidence is insufficient (184 tokens).

\subsection{Conservative Value-of-Compute Gate}
To decide whether to intervene, the system calculates a cost-benefit ratio for each candidate action using a \textbf{cautious Lower Confidence Bound (LCB)} decision rule:
\vspace{-1.5mm}
\begin{equation}
\label{eq:voc_ratio}
\mathcal{V}_{\text{LCB}}(s, a) = \frac{\max\big(0,\; \hat{\Delta P}_a(s) - \kappa \cdot \hat{\sigma}_a(s)\big)}{C(s, a) + \epsilon}
\end{equation}
\vspace{-1.5mm}
where $\hat{\Delta P}_a(s)$ is expected marginal accuracy gain over stopping immediately, $\hat{\sigma}_a(s)$ is an uncertainty dispersion proxy measuring variance across visual and textual features (Appendix~\ref{app:telemetry}), $\kappa = 0.4$ is a conservative risk parameter, and $C(s, a) > 0$ is expected token cost ($\epsilon = 10^{-4}$). In plain language: \textit{``Even after penalizing for uncertainty, does the conservative improvement from looking closer still justify the tokens spent?''} If no intervention offers a positive conservative benefit ($\le 10^{-4}$), or if observation confidence is high ($P_{\text{stop}} \ge 0.70$), the controller stops immediately ($a_{\text{stop}}$), preventing wasteful interventions.

\subsection{Same-State Counterfactual Learning}
Uncertainty alone does not mean an intervention will succeed. To learn when an intervention genuinely changes the answer, \textsc{GVoC} uses an offline same-state branching protocol ($N = 48,000$ transitions): testing alternative actions starting from the identical intermediate point to evaluate what would have happened, isolating action effects from trajectory differences. A lightweight predictor ($<2$ MB RAM) estimates advantage and token cost from simple diagnostic signals: predictive uncertainty, evidence scale, cross-modal alignment, and token budget.

\section{Empirical Results: Live Pilot vs. Offline Simulation}
\label{sec:experiments}

\subsection{Live Model Pilot ($N = 100$, Mistral Pixtral-12B)}
We evaluated 100 genuine document queries (50 DocVQA, 50 ChartQA) using Mistral Pixtral-12B via live API calls (300 executions; Table~\ref{tab:main_results}A, Figure~\ref{fig:results_contrast}A): (1)~\textbf{Direct zero-shot achieved highest accuracy} (\textbf{82.0\%}) at lowest cost (1,428 tokens). (2)~\textbf{Original \textsc{GVoC} degraded accuracy to 72.0\%} with $+101\%$ token inflation (2,889 tokens; McNemar $p = 0.0129$). (3)~\textbf{Conservative C-\textsc{GVoC} mitigated token waste} (1,676 tokens, $+17\%$), reaching \textbf{76.0\% accuracy} (6.0 pts below direct, $p = 0.1460$).

\subsection{Offline Simulation Benchmark ($N = 16,000$)}
Across 16,000 simulated episodes (DocVQA, ChartQA, TableBench, MMLongBench-Doc; Table~\ref{tab:main_results}B, Figure~\ref{fig:results_contrast}B) under modeled synthetic downsampling, \textsc{GVoC} reaches \textbf{70.2\% accuracy} with \textbf{274 tokens/query}, outperforming debate (64.4\%, 359 tokens) by +5.8 points with 23.7\% fewer tokens ($p < 0.001$). C-\textsc{GVoC} further suppresses wasteful interventions (258 tokens, regret 0.052 vs.\ oracle ceiling 90.3\%). We report Task Accuracy, Tokens/Query, and \textbf{Oracle Regret}---the gap between policy return and best candidate action (Appendix~\ref{app:prop1}).
\textit{Simulation Discrepancy:} The simulation models severe synthetic blurring where unassisted zero-shot collapses (12.5\%) from optical erasure, whereas the live pilot evaluates genuine high-resolution documents where direct zero-shot succeeds at 82.0\%, rendering intervention overhead counterproductive.

\begin{figure}[t]
\centering
\includegraphics[width=0.40\columnwidth]{figures/fig3_pareto_frontier.png}
\vspace{-2.5mm}
\caption{\textbf{Empirical Results: Live Pilot vs.\ Offline Policy Simulation.} (A) In the live foundation pilot ($N=100$, Pixtral-12B), direct inference achieves superior accuracy and lowest cost; interventions degrade performance. (B) In offline simulation ($N=16,000$), observation scaling outperforms debate baselines under synthetic downsampling.}
\label{fig:results_contrast}
\vspace{-3.5mm}
\end{figure}

\section{Why Live Interventions Underperformed}
\label{sec:diagnostics}
Targeted probes reveal suggestive failure mechanisms:
(1)~\textbf{Prompt Truncation ($N = 12$)}: multi-turn prompts under a 60-token ceiling truncated in 66.7\% of cases (8/12). Concise prompting eliminated truncation ($p = 0.0078$), but the shift from 58.3\% (7/12) to 83.3\% (10/12) is not statistically significant ($p = 0.3750$). Truncation elimination is a format fix, not proven accuracy gain.
(2)~\textbf{Spatial Context Loss ($N = 20$)}: across 20 exploratory queries (10 unique pilot images), center cropping collapsed accuracy to \textbf{25.0\%} (5/20) vs.\ 60.0\% downsampled (raw $p = 0.0391$; Bonferroni $p_{\text{adj}} = 0.1563$), showing that unguided cropping severs values from headers.
(3)~\textbf{Uncalibrated Dispersion}: $\hat{\sigma}$ correlated negatively with error ($r = -0.2173, p = 0.0020$). Measuring feature variance rather than uncertainty, it triggered interventions on confident errors and abstained on correctable cases. These small probes offer suggestive mechanisms, not definitive causal proofs for the live gap.

\section{Related Work}
\label{sec:related_work}
\textbf{Test-Time Compute Allocation.} Prior work scales reasoning tokens via chains of thought \citep{wei2022chain}, self-consistency \citep{wang2022self}, search \citep{yao2023tree, besta2024graph}, or debate \citep{snell2024scaling, du2023improving, liang2023encouraging, yu2025visual}, holding inputs static. \textsc{GVoC} explores evidence acquisition compute.
\textbf{Document Resolution \& Tiling.} While LayoutLM architectures \citep{xu2020layoutlm, xu2021layoutlmv2, huang2022layoutlmv3, kim2022ocr} and tiling models \citep{appalaraju2021docformer, blecher2023nougat, ye2023ureader, liu2024llavanext} process entire pages at high uniform token cost across benchmarks \citep{mathew2021docvqa, masry2022chartqa, tanaka2021visualmrc, tablebench2024, wang2024mmlongbenchdoc, cui2021document}, \textsc{GVoC} explores selective crops.
\textbf{Active Perception \& Value of Information.} Grounded in active perception \citep{bajcsy1988active}, Value of Information \citep{howard1966information, horvitz1988reasoning, russell1991right}, tool use \citep{schick2023toolformer, suris2023vipergpt, yang2023mm}, selective prediction \citep{geifman2017selective, kamath2020selective}, and uncertainty \citep{hendrycks2017baseline, lakshminarayanan2017simple}, \textsc{GVoC} formalizes cost-normalized visual intervention.

\section{Limitations \& Ethics}
\label{sec:limitations}
(1)~No symbolic solver. (2)~Re-grounding requires native pixels. (3)~Telemetry proxies are uncalibrated. (4)~Larger live trials remain future work. We evaluate on public benchmarks with no private data and make no deployment reliability claims.

\section{Conclusion}
\label{sec:conclusion}
When fine details are lost during downsampling, reasoning tokens cannot recover missing optical evidence. While offline simulation showed observation scaling gains under synthetic degradation, our live foundation pilot (Mistral Pixtral-12B, $N=100$) revealed that active interventions underperformed direct zero-shot inference (82.0\% at 1,428 tokens vs.\ 72.0\% for \textsc{GVoC} and 76.0\% for C-\textsc{GVoC}). Forensic probes traced this discrepancy to prompt token ceilings, spatial context loss from unguided cropping, and miscalibrated telemetry. Turning theoretical observation scaling into real gains requires format-safe prompting, context-preserving localization, and calibrated stopping rules.
"""

new_manuscript = preamble + main_text + '\n' + appendix_part

with open('naacl/main.tex', 'w', encoding='utf-8') as f:
    f.write(new_manuscript)

print("Updated naacl/main.tex written successfully.")
