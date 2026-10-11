import re
import subprocess

with open('main.tex', 'r', encoding='utf-8') as f:
    orig = f.read()

# Preamble is before \begin{document}
pos_begin = orig.find(r'\begin{document}')
preamble = orig[:pos_begin]

# Bibliography & Appendix starts at \bibliographystyle{acl_natbib}
pos_bib = orig.find(r'\bibliographystyle{acl_natbib}')
pos_clear = orig.rfind(r'\clearpage', 0, pos_bib)
if pos_clear != -1 and pos_bib - pos_clear < 20:
    appendix = orig[pos_clear:]
else:
    appendix = r'\clearpage' + '\n' + orig[pos_bib:]

main_body = r"""\begin{document}
\maketitle

\begin{abstract}
When Vision-Language Models (VLMs) encounter blurry text, tiny numbers, or complex tables, standard test-time scaling methods spend inference compute in ``reasoning space''---generating long chains of thought or multi-agent debate over the same compressed image. However, when visual tokens are lost during downsampling, reasoning alone cannot reconstruct unseen pixels. We investigate whether test-time compute is better spent in \textit{observation space} via \textbf{Grounded Value-of-Compute (\textsc{GVoC})}, dynamically deciding whether to answer immediately, inspect a high-resolution crop, re-parse a table, or safely abstain by weighing estimated accuracy gains against token costs. In an offline 16,000-query diagnostic benchmark simulation, selective observation scaling achieves 70.2\% accuracy---improving over multi-agent debate (64.4\%) with 23.7\% fewer tokens. However, in live empirical evaluation on 100 genuine visual documents using Mistral Pixtral-12B, unregularized intervention underperformed direct zero-shot inference (72.0\% accuracy at 2,889 tokens vs.\ 82.0\% at 1,428 tokens), caused by prompt token truncation ceilings and the loss of surrounding document context during cropping. A conservative regularizer (C-\textsc{GVoC}) partially mitigates token waste (76.0\% accuracy at 1,676 tokens). Our findings establish that while observation scaling is theoretically superior when visual evidence is absent, practical benefits require format-constrained decoding and context-preserving spatial localization rather than unguided cropping.
\end{abstract}

\begin{table*}[t]
\centering
\small
\renewcommand{\arraystretch}{0.84}
\begin{tabular}{lcccc}
\toprule
\textbf{Method} & \textbf{Correct Answers (\%)} $\uparrow$ & \textbf{Average Tokens / Question} $\downarrow$ & \textbf{Evaluation Setting} & \textbf{Outcome / Key Finding} \\
\midrule
\multicolumn{5}{l}{\textbf{Part A: Live Empirical Pilot (Mistral Pixtral-12B, $N = 100$ Unperturbed Document Instances)}} \\
Direct Inference (Zero-Shot) & \textbf{82.0} & \textbf{1,428} & Live Model API & Baseline accuracy; zero intervention overhead \\
Original \textsc{GVoC} & 72.0 & 2,889 ($+101\%$) & Live Model API & Significant degradation ($p = 0.013$); severe token inflation \\
Conservative C-\textsc{GVoC} & 76.0 & 1,676 ($+17\%$) & Live Model API & Mitigates token inflation, but remains below direct inference \\
\midrule
\multicolumn{5}{l}{\textbf{Part B: Offline Simulation Benchmark ($N = 16,000$ Synthetic Diagnostic Queries with Modeled Perturbations)}} \\
Monolithic Zero-Shot VLM & 12.5 $\pm$ 0.5 & 250 & Synthetic Simulation & Fails under severe downsampling and occlusion \\
Confidence-Based Router & 61.1 $\pm$ 0.8 & 355 & Synthetic Simulation & Over-triggers on boundary cases \\
Multi-Agent Debate (MACT) & 64.4 $\pm$ 0.7 & 359 & Synthetic Simulation & Expensive reasoning loops over degraded evidence \\
Deterministic Rule Baseline & \textbf{89.0} $\pm$ 0.5 & 368 & Synthetic Simulation & Peak accuracy by intervening on $>85\%$ of queries \\
\textsc{GVoC} (Point-Estimate) & 70.2 $\pm$ 0.7$^\dagger$ & 274 ($-23.7\%$) & Synthetic Simulation & Selective cost-aware observation scaling ($p < 0.001$ vs.\ MACT) \\
\textbf{C-\textsc{GVoC} (Conservative LCB, Ours)} & \textbf{70.4} $\pm$ \textbf{0.7}$^\dagger$ & \textbf{258} ($-28.1\%$) & Synthetic Simulation & Lowest regret (0.052) and best simulated compute efficiency \\
Evaluated-Action Oracle ($\mathcal{A}^*$) & 90.3 $\pm$ 0.5 & 344 & Simulation Bound & Theoretical upper bound across candidate actions \\
\bottomrule
\end{tabular}
\vspace{-2mm}
\caption{\textbf{Main Benchmark Performance Across Live Evaluation and Offline Simulation.} \textbf{Part A (Live Pilot):} On 100 genuine visual documents, unregularized intervention degrades accuracy ($-10.0$ points, $p=0.013$) and inflates token cost by $+101\%$. Conservative penalization (C-\textsc{GVoC}) reduces token waste (+17\% vs.\ direct) but does not outperform direct zero-shot inference. \textbf{Part B (Offline Simulation):} In a 16,000-query counterfactual simulation where inputs are synthetically degraded, C-\textsc{GVoC} achieves 70.4\% accuracy with 28.1\% fewer tokens than multi-agent debate. Real-world deployment reveals critical bottlenecks in prompt token limits and spatial context preservation that synthetic simulations obscure.}
\label{tab:main_results}
\vspace{-2.5mm}
\end{table*}

\section{Introduction}
\label{sec:intro}

Imagine a doctor reviewing a digital prescription scan where the decimal point between ``0.5\,mg'' and ``50\,mg'' is blurred into an illegible smudge. Sitting at a desk in deep contemplation---or debating with colleagues about what the smudge ``might'' mean---cannot bring back erased ink. The only sensible action is to grab a magnifying glass and inspect the high-resolution original.

\begin{figure}[t]
\centering
\includegraphics[width=0.68\columnwidth]{figures/fig1_motivational_teaser.png}
\vspace{-3mm}
\caption{\textbf{Reasoning vs.\ observation scaling (Conceptual illustration).} MACT debates over static evidence; \textsc{GVoC} acquires missing optical evidence when cost-effective. Token counts reflect benchmark simulation averages.}
\label{fig:teaser}
\vspace{-4mm}
\end{figure}

Yet modern AI systems do the opposite. When Vision-Language Models (VLMs) read complex invoices, financial reports, or lab results, images are compressed to fit fixed neural networks, causing tiny numbers, minus signs ($-$), or footnotes to physically vanish \citep{cui2021document, mathew2021docvqa, tablebench2024, wang2024mmlongbenchdoc}. Faced with uncertainty, existing methods force the model to ``think harder'' in \textbf{reasoning space}---spending hundreds of tokens on chains of thought or multi-agent debate over the same blurry image \citep{snell2024scaling, yu2025visual, wei2022chain}. But no amount of internal reasoning can recover visual evidence that was never observed; deliberating over absent tokens merely yields convincing hallucinations \citep{liu2024llavanext}.

\begin{table}[t]
\centering
\small
\renewcommand{\arraystretch}{0.84}
\resizebox{\columnwidth}{!}{
\begin{tabular}{p{2.2cm}p{2.4cm}p{2.4cm}p{2.0cm}}
\toprule
\textbf{Document \& Query} & \textbf{Direct / Reasoning Approach} & \textbf{Adaptive Observation Approach} & \textbf{Why It Matters} \\
\midrule
\textit{Prescription Scan:} ``Dosage?'' (True: 0.5\,mg; decimal blurred). & Direct inference sees ``05\,mg''; debate deliberates over blur $\to$ hallucination: ``50\,mg'' (359 tokens). & Controller inspects 300\,DPI native crop $\to$ resolves decimal point: ``0.5\,mg'' (274 tokens). & Deliberation cannot recover optical bits lost to downsampling. \\
\midrule
\textit{Financial Table:} ``Operating income?'' (True: $(14.2)\,\text{M}$). & Direct zero-shot misses parentheses in downsampled image $\to$ predicts positive ``\$14.2M''. & Re-execution parser re-aligns row stub and headers $\to$ reads negative ``$-\$14.2\text{M}$''. & Spatial context and header alignment prevent critical sign errors. \\
\bottomrule
\end{tabular}
}
\vspace{-2mm}
\caption{\textbf{Example: When document understanding requires closer inspection rather than longer deliberation.} Deliberation over degraded evidence fails; targeted observation resolves ambiguity when context is preserved.}
\label{tab:example_cases}
\vspace{-3.5mm}
\end{table}

This contrast leads to our central question: \textit{When an AI is uncertain about a visual document, should it think longer, or should it look closer?}

We introduce \textbf{Grounded Value-of-Compute (\textsc{GVoC})}, shifting test-time scaling to \textbf{observation space}. At each step, it chooses among four actions: \textbf{stop} if evidence is clear, \textbf{re-ground} on a high-resolution crop (60--120 tokens) if text is blurred, \textbf{re-execute} structured table parsing if layout is complex, or \textbf{abstain} if unrecoverable. \textsc{GVoC} guides this choice via \textbf{counterfactual intervention value}---weighing expected accuracy gain over stopping against token cost---trained offline via same-state branching from frozen states \citep{swaminathan2015counterfactual}.

\paragraph{Contributions.}
(1)~\textbf{Observation scaling}: allocating compute to acquire missing visual evidence rather than static reasoning;
(2)~\textbf{Dual empirical investigation}: rigorously evaluating observation scaling across a 16,000-query offline counterfactual simulation and a 100-query live foundation model pilot (Mistral Pixtral-12B);
(3)~\textbf{Forensic bottleneck analysis}: discovering why live interventions underperform direct zero-shot inference, identifying critical bottlenecks in prompt token limits and spatial context preservation.

\section{Why More Reasoning Is Not Always the Answer}
\label{sec:why_not_reasoning}

In visual document understanding, failures frequently stem from resolution loss rather than logical errors. When documents are downscaled, fine characters fall below the physical resolution needed for recognition. Think of an investigator examining a blurred photograph of a license plate: no amount of contemplative debate can magically reveal a blurred digit that was never captured. The only rational way to resolve ambiguity is to zoom in. Generating more reasoning tokens cannot reconstruct visual details that were never observed. Allocating further reasoning compute over degraded inputs wastes tokens and induces hallucinations. A formal information-theoretic upper bound under the Data Processing Inequality \citep{cover1991elements} showing that reasoning over downscaled inputs cannot recover missing optical tokens is provided in Appendix~\ref{app:proofs}.

\section{\textsc{GVoC}: Spend Compute Where It Helps}
\label{sec:method}

We view document understanding at test time as a sequential decision process. At each step, \textsc{GVoC} decides whether to finish the answer or spend compute acquiring better evidence.

\subsection{Four Test-Time Actions}
At state $s$, the controller selects among four actions: (1)~\textbf{Stop ($a_{\text{stop}}$)}: evidence is sufficient; emit the final answer immediately. (2)~\textbf{Re-Ground ($a_{\text{reground}}$)}: fine detail is missing; inspect a native-resolution crop (60--120 tokens). (3)~\textbf{Re-Execute ($a_{\text{reexec}}$)}: re-parse table structure under coordinate bindings (180--240 tokens). (4)~\textbf{Abstain ($a_{\text{abstain}}$)}: available evidence cannot support a reliable answer; emit $\bot$ (184 tokens).

\begin{figure}[t]
\centering
\includegraphics[width=0.82\columnwidth]{figures/fig2_gvoc_architecture.png}
\vspace{-3mm}
\caption{\textbf{\textsc{GVoC} Decision Pipeline.} The controller evaluates four actions: stop immediately, inspect a high-resolution crop, re-parse structured tables, or abstain. Choices balance estimated marginal accuracy improvement against token cost.}
\label{fig:architecture}
\vspace{-4mm}
\end{figure}

\subsection{Conservative Intervention Value (C-\textsc{GVoC})}
To determine whether to intervene, \textsc{GVoC} evaluates the \textbf{Conservative Intervention Value (CIV)} under a telemetry-conditioned Lower Confidence Bound (LCB):
\begin{equation}
\label{eq:voc_ratio}
\mathcal{V}_{\text{LCB}}(s, a) = \frac{\max\big(0,\; \hat{\Delta P}_a(s) - \kappa \cdot \hat{\sigma}_a(s)\big)}{C(s, a) + \epsilon}
\end{equation}
where $\hat{\Delta P}_a(s) = P(Y=1 \mid s, a) - P(Y=1 \mid s, a_{\text{stop}})$ is expected marginal accuracy gain over stopping, $\hat{\sigma}_a(s)$ is an epistemic dispersion proxy derived from state telemetry (cross-modal consensus discrepancy and evidence ambiguity; Appendix~\ref{app:telemetry}), $\kappa = 0.4$ is the conservative risk parameter, and $C(s, a) > 0$ is expected token cost ($\epsilon = 10^{-4}$). In plain terms, the numerator measures the conservative lower-bound improvement of taking a closer look, and the denominator measures what it costs.

\textsc{GVoC} executes the feasible intervention with highest positive conservative value: $a^* = \arg\max_{a \in \mathcal{M}(s)} \mathcal{V}_{\text{LCB}}(s, a)$. If no candidate intervention yields positive conservative benefit ($\max_{a \neq a_{\text{stop}}} \mathcal{V}_{\text{LCB}}(s, a) \le 10^{-4}$), or when initial observation confidence is already sufficient ($P_{\text{stop}} \ge 0.70$ with clean geometry), the policy terminates immediately ($a_{\text{stop}}$), eliminating spurious Type-I intervention compute. If expected correctness remains below safety threshold $\tau_{\text{safe}}$ and active repair is unviable, the controller safely abstains ($a_{\text{abstain}}$).

\subsection{Same-State Counterfactual Learning}
Uncertainty alone does not mean an intervention will help. To measure whether an intervention actually changes the outcome, \textsc{GVoC} uses an offline same-state branching protocol ($N = 48,000$ transitions). We freeze an intermediate state $s$, execute alternative actions from that exact state, and compare their outcomes against ground truth. This isolates the true effect of each action from trajectory differences.

A lightweight dual-head predictor ($<2$ MB RAM; Appendix~\ref{app:telemetry}) estimates expected advantage, epistemic uncertainty, and token cost from simple diagnostic signals: predictive uncertainty, evidence scale, cross-modal alignment, and token budget. An attention-based verifier confirms spatial grounding; if attribution fails, emission is blocked, triggering re-grounding or abstention.

\section{Empirical Evaluation: Simulation vs. Live Pilot}
\label{sec:experiments}

To test whether observation scaling improves document question answering, we conduct two distinct evaluations: an offline diagnostic simulation and a live API deployment.

\subsection{Offline Simulation Benchmark ($N = 16,000$)}
We evaluate on a diagnostic simulation of \textbf{16,000 document episodes} across DocVQA, ChartQA, TableBench, and MMLongBench-Doc, spanning four model profiles (Pixtral 12B, Qwen2-VL 27B, GPT-OSS 120B, Gemini 3.6 Flash; 96k evaluated actions). We measure Task Accuracy, Tokens per Query, and Empirical Oracle Regret under normalized loss $\text{Loss}(i, a) = 0.85 \cdot \mathbb{I}[Y_i(a)=0] + 0.15 \cdot \frac{C_i(a)}{C_{\max}}$ (Eq.~\ref{eq:regret}).

As shown in Table~\ref{tab:main_results} (Part B), when inputs undergo severe synthetic downsampling, \textsc{GVoC} reaches \textbf{70.2\% accuracy} with \textbf{274 tokens/query}, outperforming MACT (64.4\%, 359 tokens) by +5.8 points while using 23.7\% fewer tokens ($p < 0.001$). C-\textsc{GVoC} further suppresses Type-I compute harm via dispersion penalization, saving 16 tokens/query (258 tokens, regret 0.052).

\subsection{Live Model Pilot ($N = 100$, Mistral Pixtral-12B)}
To test whether these simulated gains hold in genuine deployment, we executed a preregistered live pilot on 100 untouched document queries (50 DocVQA, 50 ChartQA) using Mistral Pixtral-12B via live API inference (300 model calls).

As reported in Table~\ref{tab:main_results} (Part A), the live empirical results tell a starkly different story:
(1)~\textbf{Direct Zero-Shot Inference} achieved the highest overall accuracy (\textbf{82.0\%}, 82/100) using 1,428 tokens.
(2)~\textbf{Original \textsc{GVoC}} degraded accuracy to \textbf{72.0\%} (72/100) while inflating token consumption by $+101\%$ (2,889 tokens). A paired McNemar test confirms this accuracy degradation is statistically significant ($n_{10}=12, n_{01}=2, p = 0.0129$).
(3)~\textbf{Conservative C-\textsc{GVoC}} mitigated over-intervention, reducing token expenditure to 1,676 tokens (+17\% overhead), but achieved only \textbf{76.0\% accuracy} (76/100), failing to outperform direct inference ($p = 0.1460$).

\section{Why Live Interventions Failed: Diagnostics}
\label{sec:diagnostics}

Why did the strong advantage observed in simulation reverse in live model testing? We conducted three targeted diagnostic experiments to isolate the failure mechanisms:

\paragraph{1. Prompt Truncation Ceilings ($N = 12$).}
In the live pilot, intervention prompts were conversational and multi-turn. Under an output limit of 60 tokens, 66.7\% of intervention responses (8/12) were prematurely truncated mid-sentence. Expanding the budget to 256 tokens or switching to concise single-turn prompting eliminated truncation ($p = 0.0078$), raising accuracy from 58.3\% to 83.3\%--91.7\%. Thus, intervention failure was heavily driven by conversational formatting constraints rather than visual reasoning flaws.

\paragraph{2. Spatial Context Destruction in Cropping ($N = 20$).}
We evaluated five image transformations across 20 instances. While full-resolution images scored 85.0\% (17/20) and downsampled full images scored 60.0\% (12/20), naive center cropping collapsed accuracy to \textbf{25.0\%} (5/20; McNemar $p = 0.0391$ vs.\ downsampled). Cropping into a dense chart or table physically severed data values from their row headers, column labels, and axis units. Without learned spatial localization, zooming in destroys the relational context needed to interpret evidence.

\paragraph{3. Uncalibrated Telemetry Dispersion.}
Audit of the telemetry dispersion proxy $\hat{\sigma}$ revealed that it is negatively correlated with true prediction errors ($r = -0.2173, p = 0.0020$). Because dispersion captured cross-modal embedding variance rather than calibrated predictive uncertainty, the controller misjudged when to trigger repair.

\section{Related Work}
\label{sec:related_work}

\textbf{Test-Time Scaling.} Prior work scales reasoning tokens via chain-of-thought, search, or multi-agent debate \citep{snell2024scaling, yu2025visual, wei2022chain}, keeping visual evidence static. \textsc{GVoC} scales evidence acquisition directly.

\textbf{High-Resolution Document VLM.} Downsampling severely degrades fine document text \citep{mathew2021docvqa, masry2022chartqa, tablebench2024, wang2024mmlongbenchdoc, cui2021document}. While native architectures \citep{ye2023ureader, liu2024llavanext, blecher2023nougat, appalaraju2021docformer} process full documents at high cost, \textsc{GVoC} acquires high-resolution crops selectively.

\textbf{Selective Prediction, Tool Use \& VOI.} Grounded in active perception \citep{bajcsy1988active}, Value of Information \citep{howard1966information, horvitz1988reasoning, russell1991right}, tool learning \citep{schick2023toolformer, suris2023vipergpt}, step verification \citep{lightman2023verify}, and selective prediction \citep{geifman2017selective, kamath2020selective}, \textsc{GVoC} learns cost-normalized counterfactual benefits of concrete visual interventions relative to stopping.

\section{Limitations}
\label{sec:limitations}

(1)~\textsc{GVoC} lacks an integrated calculator; arithmetic favors reasoning-space methods. (2)~Re-grounding requires access to native-resolution pixels. (3)~The current telemetry dispersion proxy is uncalibrated on live endpoints. (4)~Continuous token-matched budget comparisons across larger live samples remain future work.

\section{Conclusion}
\label{sec:conclusion}

Test-time computation for visual document understanding should not be confined to generating reasoning tokens over degraded inputs. When fine print or decimal points vanish during downsampling, thinking longer cannot recover missing optical evidence. We investigated shifting compute to observation space through \textsc{GVoC}, which evaluates candidate visual actions by their expected benefit per token cost. In an offline 16,000-query simulation, selective observation scaling achieved 70.4\% accuracy with 28.1\% lower token cost than multi-agent debate. However, live empirical evaluation on genuine visual documents (Mistral Pixtral-12B) revealed that intervention-based methods underperform direct inference (72.0\% and 76.0\% vs.\ 82.0\% for direct inference) while consuming more tokens, primarily due to output token truncation and loss of surrounding context during localized cropping. These findings establish that observation scaling cannot rely on naive cropping or unconstrained generation: reliable test-time visual scaling requires format-constrained decoding, context-preserving region selection, and calibrated stopping.

\section{Ethics Statement}
\label{sec:ethics}

We evaluate on public, non-sensitive document benchmarks and do not collect personal or private user data. The method is intended to reduce unsupported answers through selective evidence acquisition and abstention. We make no deployment-level reliability claims.
"""

new_tex = preamble + main_body + '\n' + appendix

with open('main.tex', 'w', encoding='utf-8') as f:
    f.write(new_tex)

print('Updated main.tex written successfully.')
