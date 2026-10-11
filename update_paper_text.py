with open('assemble_perfect_paper.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_sec4 = text.find(r'\section{Empirical Results: Live Pilot vs. Offline Simulation}')
end_sec_ethics = text.find(r'"""', start_sec4)

new_tail = r'''\section{Empirical Results: Live Pilot vs. Offline Simulation}
\label{sec:experiments}

\subsection{Live Model Pilot ($N = 100$, Mistral Pixtral-12B)}
We evaluated 100 genuine document queries (50 DocVQA, 50 ChartQA) using Mistral Pixtral-12B via live API calls (300 model executions). As shown in Table~\ref{tab:main_results}A and Figure~\ref{fig:results_contrast}A:
(1)~\textbf{Direct zero-shot inference achieved the highest accuracy} (\textbf{82.0\%}) at lowest cost (1,428 tokens).
(2)~\textbf{Original \textsc{GVoC} degraded accuracy to 72.0\%} while inflating tokens by $+101\%$ (2,889 tokens; McNemar $p = 0.0129$).
(3)~\textbf{Conservative C-\textsc{GVoC} mitigated token waste} (1,676 tokens, $+17\%$), but reached \textbf{76.0\% accuracy}, remaining 6.0 points below direct inference ($p = 0.1460$).

\subsection{Offline Simulation Benchmark ($N = 16,000$)}
Across 16,000 simulated episodes (DocVQA, ChartQA, TableBench, MMLongBench-Doc; Table~\ref{tab:main_results}B, Figure~\ref{fig:results_contrast}B) with synthetic downsampling, \textsc{GVoC} reaches \textbf{70.2\% accuracy} with \textbf{274 tokens/query}, outperforming multi-agent debate (64.4\%, 359 tokens) by +5.8 points with 23.7\% fewer tokens ($p < 0.001$). C-\textsc{GVoC} further suppresses wasteful interventions (258 tokens, regret 0.052 vs.\ oracle ceiling 90.3\%).

\begin{figure}[t]
\centering
\includegraphics[width=0.58\columnwidth]{figures/fig3_pareto_frontier.png}
\vspace{-2.5mm}
\caption{\textbf{Empirical Results: Live Pilot vs.\ Offline Simulation.} (A) In the live pilot ($N=100$, Pixtral-12B), direct inference achieves superior accuracy and lowest cost. (B) In offline simulation ($N=16,000$), observation scaling outperforms debate baselines.}
\label{fig:results_contrast}
\vspace{-3.5mm}
\end{figure}

\section{Why Live Interventions Underperformed}
\label{sec:diagnostics}
Targeted probes reveal three primary failure mechanisms behind live pilot degradation:

\paragraph{1. Conversational Prompt Truncation ($N = 12$).}
Multi-turn intervention prompts under a 60-token ceiling truncated in 66.7\% of cases (8/12). Switching to concise single-turn prompting eliminated truncation ($p = 0.0078$), raising accuracy from 58.3\% to 83.3\%--91.7\%. Degradation was thus driven by prompt formatting overhead rather than reasoning flaws.

\paragraph{2. Spatial Context Loss in Cropping ($N = 20$).}
While full-resolution scored 85.0\% and downsampled scored 60.0\%, naive center cropping collapsed accuracy to \textbf{25.0\%} (5/20; McNemar $p = 0.0391$). Cropping severed data values from headers and units; zooming in without spatial coordinates destroys relational structure.

\paragraph{3. Uncalibrated Telemetry Dispersion.}
The dispersion proxy $\hat{\sigma}$ correlated negatively with prediction errors ($r = -0.2173, p = 0.0020$). Capturing feature variance rather than uncertainty, it triggered interventions on confident errors and abstained on correctable cases.

\section{Related Work}
\label{sec:related_work}
\textbf{Test-Time Compute.} Prior work scales reasoning tokens via chains of thought or multi-agent debate \citep{snell2024scaling, yu2025visual, wei2022chain}, holding visual inputs static. \textsc{GVoC} instead investigates allocating compute to evidence acquisition.
\textbf{Document Resolution.} While whole-image tiling models \citep{ye2023ureader, liu2024llavanext, blecher2023nougat, appalaraju2021docformer} process entire pages at high cost, \textsc{GVoC} explores selective crop inspection.
\textbf{Selective Prediction \& VOI.} Grounded in active perception \citep{bajcsy1988active}, Value of Information \citep{howard1966information, horvitz1988reasoning, russell1991right}, and selective prediction \citep{geifman2017selective, kamath2020selective}, \textsc{GVoC} formalizes cost-normalized visual intervention.

\section{Limitations}
\label{sec:limitations}
(1)~\textsc{GVoC} lacks a symbolic math solver. (2)~Re-grounding requires native pixels. (3)~Telemetry proxies are uncalibrated. (4)~Larger live trials remain future work.

\section{Conclusion}
\label{sec:conclusion}
Test-time compute should not be restricted to generating internal reasoning tokens over degraded visual inputs: when fine print, decimals, or table borders are lost during downsampling, thinking longer cannot recover missing optical evidence. In an offline 16,000-query simulation under synthetic degradation, observation scaling achieved 70.4\% accuracy with 28.1\% fewer tokens than multi-agent debate. Crucially, however, our live foundation pilot (Mistral Pixtral-12B on 100 documents) revealed that intervention methods underperformed direct zero-shot inference (82.0\% at 1,428 tokens vs.\ 72.0\% at 2,889 tokens for \textsc{GVoC} and 76.0\% at 1,676 tokens for C-\textsc{GVoC}). Forensic probes traced this discrepancy to conversational prompt token ceilings, spatial context loss from unguided cropping, and miscalibrated telemetry. Turning theoretical observation scaling into real-world gains requires format-safe prompting, context-preserving localization, and calibrated stopping rules.

\section{Ethics Statement}
\label{sec:ethics}
We evaluate on public document benchmarks and collect no private data. We make no deployment-level reliability claims.
'''

if start_sec4 != -1 and end_sec_ethics != -1:
    text = text[:start_sec4] + new_tail + text[end_sec_ethics:]
    with open('assemble_perfect_paper.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated assemble_perfect_paper.py tail successfully!')
else:
    print('Error finding sections in assemble_perfect_paper.py')
