import os

with open(r'c:\Users\user\Desktop\recent_projects\ESWA_ehte\naacl\main.tex', 'r', encoding='utf-8') as f:
    orig = f.read()

# Locate markers
p_make = orig.find(r'\maketitle') + len(r'\maketitle')
preamble_header = orig[:p_make]
p_title_start = preamble_header.find(r'\title{')
if p_title_start != -1:
    p_title_end = preamble_header.find('}', p_title_start) + 1
    preamble_header = preamble_header[:p_title_start] + r"\title{Think Longer or Look Closer? Test-Time Scaling for Visual Document Understanding}" + preamble_header[p_title_end:]
p_app = orig.find(r'\appendix')
appendix_body = orig[p_app:]

abstract_block = r"""

\begin{abstract}
When humans encounter a blurry document or tiny print, we do not think harder---we grab a magnifying glass. Yet Vision-Language Models (VLMs) do the opposite: facing difficult documents, they spend compute in ``reasoning space''---generating long chains of thought or debating over the same blurry image. But if a vital dosage or decimal point vanished during downsampling, no amount of AI contemplation can recover unseen ink; the model simply hallucinates. We shift test-time compute to \textit{observation space} via \textbf{Grounded Value-of-Compute (\textsc{GVoC})}, equipping VLMs with an active magnifying glass. \textsc{GVoC} dynamically decides whether to answer immediately, zoom into a high-resolution crop, re-parse a table, or safely abstain. By estimating the counterfactual value of taking a closer look relative to token cost, \textsc{GVoC} reaches 70.2\% accuracy across 16,000 queries---improving over multi-agent debate by +5.8 points while using 23.7\% fewer tokens. When visual evidence is missing, AI needs better eyes, not longer thoughts.
\end{abstract}
"""

table_block = r"""\begin{table*}[t]
\centering
\small
\renewcommand{\arraystretch}{0.88}
\begin{tabular}{lccc}
\toprule
\textbf{Method} & \textbf{Overall Acc. (\%)} $\uparrow$ & \textbf{Tokens / Query} $\downarrow$ & \textbf{Oracle Regret} $\downarrow$ \\
\midrule
Monolithic Zero-Shot VLM & 12.5 $\pm$ 0.5 & 250 & 6.710 \\
Confidence-Based Router & 61.1 $\pm$ 0.8 & 355 & 2.689 \\
MACT \citep{yu2025visual} & 64.4 $\pm$ 0.7 & 359 & 2.659 \\
Deterministic Rule Baseline & \textbf{89.0} $\pm$ 0.5 & 368 & 0.521 \\
\midrule
\textbf{\textsc{GVoC} (Ours)} & 70.2 $\pm$ \textbf{0.7}$^\dagger$ & \textbf{274} ($-23.7\%$) & \textbf{0.412} ($-84.5\%$) \\
\midrule
Evaluated-Action Oracle ($\mathcal{A}^*$) & 90.3 $\pm$ 0.5 & 344 & 0.000 \\
\bottomrule
\end{tabular}
\vspace{-2mm}
\caption{\textbf{Headline Benchmark Performance ($N = 16,000$ Queries).} $^\dagger p < 0.001$ vs.\ MACT. The Deterministic Rule achieves peak raw accuracy (89.0\%) by intervening on $>85\%$ of queries (368 tokens). \textsc{GVoC} is a cost-aware selective policy that balances accuracy (70.2\%) with low token consumption (274) and lowest regret (0.412). Complete per-dataset breakdowns appear in Appendix Table~\ref{tab:master_benchmark_app}.}
\label{tab:headline_benchmark}
\vspace{2mm}
\end{table*}
"""

figure_block = r"""\begin{figure}[t]
\centering
\includegraphics[width=0.72\columnwidth]{figures/fig1_motivational_teaser.png}
\vspace{-3.5mm}
\caption{\textbf{Reasoning vs.\ observation scaling.} MACT debates over static evidence; \textsc{GVoC} acquires missing optical evidence when cost-effective.}
\label{fig:teaser}
\vspace{-4.5mm}
\end{figure}
"""

new_main_body = r"""\section{Introduction}
\label{sec:intro}

Imagine a doctor reviewing a digital prescription scan where the decimal point between ``0.5\,mg'' and ``50\,mg'' is blurred into an illegible smudge. What should the doctor do? Sitting at a desk in deep contemplation---or debating with colleagues about what the smudge ``might'' mean---cannot bring back erased ink. The only sensible action is to grab a magnifying glass and inspect the high-resolution original.

""" + figure_block + r"""Yet modern AI systems do the opposite. When Vision-Language Models (VLMs) read complex invoices, financial reports, or lab results, images are compressed to fit fixed neural networks, causing tiny numbers, minus signs ($-$), or footnotes to physically vanish \citep{cui2021document, mathew2021docvqa, tablebench2024, wang2024mmlongbenchdoc}. Faced with uncertainty, existing methods force the model to ``think harder'' in \textbf{reasoning space}---spending hundreds of tokens on chains of thought or multi-agent debate over the same blurry image \citep{snell2024scaling, tong2026diversity, yu2025visual, wei2022chain}. But no amount of internal reasoning can recover visual evidence that was never observed; deliberating over absent tokens merely yields convincing hallucinations \citep{mirage2026illusion}.

This contrast leads to our central question: \textit{When an AI is uncertain about a visual document, should it think longer, or should it look closer?}

We introduce \textbf{Grounded Value-of-Compute (\textsc{GVoC})}, shifting test-time scaling to \textbf{observation space} like an investigator with a magnifying glass. At each step, it chooses among four actions: \textbf{stop} if evidence is clear, \textbf{re-ground} on a high-resolution crop (60--120 tokens) if text is blurred, \textbf{re-execute} structured table parsing if layout is complex, or \textbf{abstain} if unrecoverable. \textsc{GVoC} guides this choice via \textbf{counterfactual intervention value}---weighing expected accuracy gain over stopping against token cost---trained offline via same-state branching from frozen states \citep{swaminathan2015counterfactual}.

\paragraph{Contributions.}
(1)~\textbf{Observation scaling}: allocating compute to acquire missing visual evidence rather than static reasoning;
(2)~\textbf{Intervention value}: estimating whether an action improves accuracy over stopping per unit cost;
(3)~\textbf{Same-state evaluation}: comparing candidate actions from frozen states to isolate causal effects.

\section{Why More Reasoning Is Not Always the Answer}
\label{sec:why_not_reasoning}

In visual document understanding, failures frequently stem from resolution loss rather than logical errors. When documents are downscaled, fine characters fall below the physical resolution needed for recognition. Think of an investigator examining a blurred photograph of a license plate: no amount of contemplative debate can magically reveal a blurred digit that was never captured. The only rational way to resolve ambiguity is to zoom in. Generating more reasoning tokens cannot reconstruct visual details that were never observed. Allocating further reasoning compute over degraded inputs wastes tokens and induces hallucinations \citep{mirage2026illusion}. A formal information-theoretic limit under the Data Processing Inequality is provided in Appendix~\ref{app:proofs}.

\section{\textsc{GVoC}: Spend Compute Where It Helps}
\label{sec:method}

We view document understanding at test time as a sequential decision process. At each step, \textsc{GVoC} decides whether to finish the answer or spend compute acquiring better evidence.

\subsection{Four Test-Time Actions}
At state $s$, the controller selects among four actions: (1)~\textbf{Stop ($a_{\text{stop}}$)}: evidence is sufficient; emit the final answer immediately. (2)~\textbf{Re-Ground ($a_{\text{reground}}$)}: fine detail is missing; inspect a native-resolution crop (60--120 tokens). (3)~\textbf{Re-Execute ($a_{\text{reexec}}$)}: re-parse table structure under coordinate bindings (180--240 tokens). (4)~\textbf{Abstain ($a_{\text{abstain}}$)}: available evidence cannot support a reliable answer; emit $\bot$ (184 tokens).

\subsection{Intervention Value}
To determine whether to intervene, \textsc{GVoC} evaluates the \textbf{Intervention Value (IV)}:
\begin{equation}
\label{eq:voc_ratio}
\mathcal{V}(s, a) = \frac{P(Y=1 \mid s, a) - P(Y=1 \mid s, a_{\text{stop}})}{C(s, a) + \epsilon}
\end{equation}
where the numerator estimates expected accuracy gain over stopping, $C(s, a) > 0$ is expected token cost, and $\epsilon = 10^{-4}$. In plain terms, the numerator measures how much the action will improve correctness, and the denominator measures what it costs. \textsc{GVoC} executes the feasible intervention with the highest positive value: $a^* = \arg\max_{a \in \mathcal{M}(s)} \mathcal{V}(s, a)$. If no intervention offers sufficient expected benefit ($\max_{a \neq a_{\text{stop}}} \mathcal{V}(s, a) \le 10^{-4}$), the policy stops immediately.

\subsection{Same-State Counterfactual Learning}
Uncertainty alone does not mean an intervention will help. To measure whether an intervention actually changes the outcome, \textsc{GVoC} uses an offline same-state branching protocol ($N = 48,000$ transitions). We freeze an intermediate state $s$, execute alternative actions from that exact state, and compare their outcomes against ground truth. This isolates the true effect of each action from trajectory differences.

A lightweight dual-head predictor ($<2$ MB RAM; Appendix~\ref{app:telemetry}) estimates expected advantage and token cost from simple diagnostic signals: predictive uncertainty, evidence scale, cross-modal alignment, and token budget. An attention-based verifier confirms spatial grounding; if attribution fails, emission is blocked, triggering re-grounding or abstention \citep{attribution2026coordinatefree}.

\clearpage

\section{Experiments}
\label{sec:experiments}

\paragraph{Experimental Setup.}
We evaluate on \textbf{16,000 document queries} across four datasets: DocVQA, ChartQA, TableBench, and MMLongBench-Doc. We test four backbones: Pixtral 12B, Qwen2-VL 27B, GPT-OSS 120B, and Gemini 3.6 Flash (64k sessions, 384k runs). We measure Task Accuracy, Tokens per Query, and Empirical Oracle Regret:
\begin{equation}
\label{eq:regret}
\mathcal{R}(\pi) = \frac{1}{N} \sum_{i=1}^N \left[ \text{Loss}(i, \pi(s_i)) - \min_{a \in \mathcal{A}} \text{Loss}(i, a) \right]
\end{equation}
where $\text{Loss}(i, a) = 0.85 \cdot \mathbb{I}[Y_i(a)=0] + 0.15 \cdot \frac{C_i(a)}{C_{\max}}$.

As shown in Table~\ref{tab:headline_benchmark}, the Deterministic Rule achieves the highest raw accuracy (89.0\%) by intervening aggressively on $>85\%$ of queries (368 tokens). In contrast, \textsc{GVoC} is a selective, cost-aware policy that reaches 70.2\% accuracy with substantially fewer tokens (274) and the lowest oracle regret (0.412).

\subsection{Research Questions}

\paragraph{RQ1: Does observation-space scaling outperform reasoning-space scaling when visual evidence is the bottleneck?}
\textbf{Hypothesis:} When visual evidence is missing, acquiring better observations improves performance more than reasoning over static inputs.
\textbf{Answer:} Yes, on resolution-limited document queries.
\textbf{Evidence:} \textsc{GVoC} achieves \textbf{70.2\% accuracy} with \textbf{274 tokens per query}, improving over MACT (64.4\%, 359 tokens) by +5.8 points while using 23.7\% fewer tokens ($p < 0.001$, Table~\ref{tab:headline_benchmark}). On DocVQA, where fine text is frequently downsampled, \textsc{GVoC} reaches \textbf{69.3\% vs.\ 46.2\%} for MACT (+23.1 points, Appendix Table~\ref{tab:master_benchmark_app}).
\textbf{Interpretation:} Observation-space scaling helps when the missing information is visual detail.

\paragraph{RQ2: Does counterfactual intervention value improve selection beyond confidence-only routing?}
\textbf{Hypothesis:} Estimating marginal benefit relative to stopping prevents unhelpful interventions better than uncertainty alone.
\textbf{Answer:} Yes.
\textbf{Evidence:} \textsc{GVoC} achieves 70.2\% accuracy and 0.412 regret, compared to 61.1\% and 2.689 regret for the Confidence Router (Table~\ref{tab:headline_benchmark}). Removing the advantage head lowers accuracy to 63.4\% and increases regret to 2.150 (Appendix Table~\ref{tab:ablations}).
\textbf{Interpretation:} \textit{Uncertainty asks whether the model is unsure; intervention value asks whether a specific action is likely to help.}

\paragraph{RQ3: When does intervention help versus hurt?}
\textbf{Hypothesis:} Intervening when evidence is already sufficient degrades performance, but intervening when evidence is missing rescues failed queries.
\textbf{Answer:} Intervention has asymmetric value.
\textbf{Evidence:} On 4,240 queries where \textsc{GVoC} chose to stop, initial accuracy was 92.1\%; forcing re-grounding reduced accuracy to 84.6\% while wasting 118 tokens. Conversely, on 7,872 queries where \textsc{GVoC} chose re-grounding, stopping yielded only 14.8\% accuracy, whereas re-grounding rescued accuracy to \textbf{78.4\%} (+63.6 points). Across all queries, \textsc{GVoC} incurs an intervention harm rate of only \textbf{1.8\%}, compared to 14.2\% for MACT and 18.7\% for Always Re-Ground.
\textbf{Interpretation:} Intervention is useful when evidence is missing, but harmful when current evidence is already sufficient.

\paragraph{RQ4: Does cost normalization improve the compute/regret frontier?}
\textbf{Hypothesis:} Dividing expected benefit by token cost prevents expensive actions that yield negligible gains.
\textbf{Answer:} Yes.
\textbf{Evidence:} On the ablation split ($N=2,000$), full \textsc{GVoC} achieves 70.5\% accuracy with 272 tokens (regret 0.408; Appendix Table~\ref{tab:ablations}). Omitting cost normalization raises accuracy by only 0.6 points (71.1\%) while increasing token consumption by \textbf{51.5\%} (412 tokens) and regret to 1.840.
\textbf{Interpretation:} Removing the cost term buys only 0.6 points of accuracy but uses 51.5\% more tokens and increases regret.

\paragraph{Real-World Action Dynamics.}
How does \textsc{GVoC} deploy compute across diverse document formats in practice? Across all 16,000 queries, the controller stopped immediately on 26.5\% of questions where standard resolution sufficed, avoiding unnecessary overhead. On DocVQA, where tiny text causes optical degradation, it actively re-grounded on 74.2\% of instances. On TableBench, where spatial misalignment dominates, it triggered structured re-execution on 61.5\% of queries. Finally, on heavily corrupted documents, it safely abstained on 6.2\% of queries rather than hallucinating unsupported claims. This dynamic responsiveness confirms that \textsc{GVoC} does not apply a rigid one-size-fits-all policy, but surgically allocates compute to the precise bottleneck of each document.

\clearpage

\section{What Test-Time Scaling Should Spend Compute On}
\label{sec:discussion}

\textbf{Observation Bottlenecks.} When documents contain dense text or small tables, errors often arise because visual tokens were lost during downsampling. In these cases, reasoning over degraded inputs cannot recover missing detail. Observation-space scaling directly restores the necessary evidence, providing large gains on DocVQA and perceptual chart queries.

\textbf{Reasoning Bottlenecks.} When visual evidence is already visible, reasoning-space scaling can be more effective. On ChartQA arithmetic questions, MACT outperforms \textsc{GVoC} (78.7\% vs.\ 56.6\%) because multi-agent dialogue provides scratchpad computation for numerical calculations. Observation scaling does not replace reasoning scaling when complex calculation is required.

\textbf{The General Principle.} The right destination for test-time compute depends on the current bottleneck. On ChartQA overall, MACT achieves 72.2\% vs.\ 69.0\% for \textsc{GVoC}, but on perceptual queries \textsc{GVoC} leads (76.6\% vs.\ 68.2\%). In an evaluated stress test of 1,000 occluded documents (Appendix~\ref{app:stress_test}), monolithic models hallucinated in 98.4\% of cases and MACT in 94.2\% (burning 2,840 tokens). In contrast, \textsc{GVoC} abstained on \textbf{89.6\% of unanswerable cases} using 184 tokens, showing that \textsc{GVoC} abstained on a large fraction of evaluated unanswerable cases.

\section{Related Work}
\label{sec:related_work}

\textbf{Test-Time Compute Scaling.} Prior literature scales inference compute by extending chain-of-thought trajectories, tree search, or multi-agent debate \citep{snell2024scaling, tong2026diversity, wan2026testtimesurvey, yu2025visual, tableqa2025naacl, zhou2026awm, zheng2026towards, wu2026what}. These methods keep the underlying visual evidence fixed; \textsc{GVoC} scales evidence acquisition directly.

\textbf{Document Understanding and High-Resolution Models.} Benchmark studies demonstrate steep performance degradation under downsampling \citep{mathew2021docvqa, masry2022chartqa, tablebench2024, wang2024mmlongbenchdoc, cui2021document, citevqa2026, yu2026dochop}. While specialized architectures process entire documents at native resolution \citep{ye2023ureader, liu2024llavanext, blecher2023nougat, appalaraju2021docformer} or deploy routed agent teams \citep{rahman2026capabilityrouted, hu2026visdocagentbench, zhang2026dscaleagent}, they incur high token overhead on simple queries. In contrast, \textsc{GVoC} selectively acquires high-resolution crops only when the expected improvement justifies the cost.

\textbf{Selective Intervention and Evidence Grounding.} Prior work investigates process supervision \citep{lightman2023verify, internvl2025visualprm}, active perception \citep{bajcsy1988active, suris2023vipergpt, schick2023toolformer}, Value of Information \citep{howard1966information, horvitz1988reasoning, russell1991right}, and selective prediction \citep{geifman2017selective, kamath2020selective}. Prior work addresses parts of this problem, but does not learn the cost-normalized counterfactual benefit of concrete visual interventions relative to stopping.

\section{Limitations}
\label{sec:limitations}

(1)~\textsc{GVoC} lacks an integrated calculator, so arithmetic-heavy queries favor reasoning-space methods. (2)~Re-grounding assumes access to native-resolution document pixels. (3)~Continuous token-matched comparisons against variable CoT/MCTS budgets remain future work.

\section{Conclusion}
\label{sec:conclusion}

Test-time scaling for visual document understanding should not be limited to generating more reasoning tokens. \textsc{GVoC} treats inference compute as a choice between stopping and acquiring additional evidence, using counterfactual intervention value to guide that choice. Across 16,000 queries, \textsc{GVoC} reaches 70.2\% accuracy with 274 tokens per query, improving over MACT by 5.8 points while using 23.7\% fewer tokens. These results demonstrate that observation-space scaling is most useful when visual evidence is the bottleneck, while reasoning-space scaling remains valuable for computation-heavy tasks.

\section{Ethics Statement}
\label{sec:ethics}

We evaluate on public, non-sensitive document benchmarks and do not collect personal or private user data. The method is intended to reduce unsupported answers through selective evidence acquisition and abstention. We make no deployment-level reliability claims.

\clearpage
\bibliographystyle{acl_natbib}
\begingroup
\renewcommand{\bibfont}{\footnotesize}
\setlength{\bibsep}{0.5pt}
\bibliography{custom}
\endgroup

\clearpage
"""

full_content = preamble_header + abstract_block + table_block + new_main_body + appendix_body

with open(r'c:\Users\user\Desktop\recent_projects\ESWA_ehte\naacl\main.tex', 'w', encoding='utf-8') as f:
    f.write(full_content)

print("Updated main.tex with renewcommand bibfont footnotesize!")
