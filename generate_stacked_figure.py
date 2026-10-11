import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

def create_stacked_results_figure():
    # Enlarge canvas to 5.0 x 2.6 inches for high legibility while fitting page budget
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.0, 2.6), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    # ==================== Panel A: Live Model Pilot ====================
    ax1.grid(True, linestyle='--', alpha=0.55, color='#CBD5E1')
    ax1.set_facecolor('#F8FAFC')

    methods_live = ['Direct Zero-Shot', 'C-GVoC (Conservative)', 'Original GVoC']
    acc_live = [82.0, 76.0, 72.0]
    tok_live = [1428, 1676, 2889]
    colors_live = ['#1D4ED8', '#D97706', '#DC2626']

    for i in range(len(methods_live)):
        ax1.scatter(tok_live[i], acc_live[i], color=colors_live[i], s=200, zorder=6,
                    edgecolors='#0F172A', linewidth=1.5)
        if i == 0:
            ax1.annotate("Direct Zero-Shot\n82.0% (1,428 tok)", (tok_live[i], acc_live[i]),
                         xytext=(tok_live[i] + 45, acc_live[i] - 1.2), fontsize=9.5, fontweight='bold', color=colors_live[i])
        elif i == 1:
            ax1.annotate("C-GVoC\n76.0% (1,676 tok)", (tok_live[i], acc_live[i]),
                         xytext=(tok_live[i] + 45, acc_live[i] - 3.2), fontsize=9.5, fontweight='bold', color=colors_live[i])
        elif i == 2:
            ax1.annotate("Original GVoC\n72.0% (2,889 tok)", (tok_live[i], acc_live[i]),
                         xytext=(tok_live[i] - 560, acc_live[i] + 1.2), fontsize=9.5, fontweight='bold', color=colors_live[i])

    ax1.set_xlim(1150, 3150)
    ax1.set_ylim(67, 86)
    ax1.set_xlabel('Tokens / Query (Prompt + Output)', fontsize=10, fontweight='bold', color='#1E293B')
    ax1.set_ylabel('Accuracy (%)', fontsize=10, fontweight='bold', color='#1E293B')
    ax1.set_title('(A) Live Foundation Pilot (N=100, Pixtral-12B): Direct Inference Wins',
                  fontsize=10.5, fontweight='bold', color='#0F172A', pad=5)
    ax1.tick_params(axis='both', which='major', labelsize=9)

    ax1.axhspan(67, 81.5, facecolor='#FEE2E2', alpha=0.35, zorder=1)
    ax1.text(2380, 68.3, "Degradation Zone (-10.0 pts acc, +101% tok)",
             fontsize=8.5, color='#991B1B', fontweight='bold', ha='center',
             bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFFF', edgecolor='#F87171', alpha=0.95))

    # ==================== Panel B: Offline Policy Simulation ====================
    ax2.grid(True, linestyle='--', alpha=0.55, color='#CBD5E1')
    ax2.set_facecolor('#F8FAFC')

    methods_sim = ['Zero-Shot', 'MACT Debate', 'GVoC (Point)', 'C-GVoC (LCB)', 'Oracle Bound']
    acc_sim = [12.5, 64.4, 70.2, 70.4, 90.3]
    tok_sim = [250, 359, 274, 258, 344]
    colors_sim = ['#64748B', '#DC2626', '#059669', '#047857', '#7C3AED']

    for i in range(len(methods_sim)):
        marker = '*' if 'GVoC' in methods_sim[i] else ('D' if 'Oracle' in methods_sim[i] else 'o')
        size = 240 if marker == '*' else (170 if marker == 'D' else 140)
        ax2.scatter(tok_sim[i], acc_sim[i], color=colors_sim[i], marker=marker, s=size,
                    zorder=6, edgecolors='#0F172A', linewidth=1.4)

        if i == 0:
            ax2.annotate("Zero-Shot\n(12.5%)", (tok_sim[i], acc_sim[i]),
                         xytext=(tok_sim[i] + 8, acc_sim[i] - 3), fontsize=9, color=colors_sim[i], fontweight='bold')
        elif i == 1:
            ax2.annotate("MACT Debate\n64.4% (359 tok)", (tok_sim[i], acc_sim[i]),
                         xytext=(tok_sim[i] - 110, acc_sim[i] - 12), fontsize=9, color=colors_sim[i], fontweight='bold')
        elif i == 2:
            ax2.annotate("GVoC\n(70.2%)", (tok_sim[i], acc_sim[i]),
                         xytext=(tok_sim[i] + 8, acc_sim[i] - 7), fontsize=9, color=colors_sim[i], fontweight='bold')
        elif i == 3:
            ax2.annotate("C-GVoC (Ours)\n70.4% (258 tok)", (tok_sim[i], acc_sim[i]),
                         xytext=(tok_sim[i] - 65, acc_sim[i] + 7), fontsize=9, color=colors_sim[i], fontweight='bold')
        elif i == 4:
            ax2.annotate("Oracle Ceiling\n90.3% (344 tok)", (tok_sim[i], acc_sim[i]),
                         xytext=(tok_sim[i] - 110, acc_sim[i] + 3), fontsize=9, color=colors_sim[i], fontweight='bold')

    ax2.set_xlim(200, 420)
    ax2.set_ylim(0, 108)
    ax2.set_xlabel('Simulated Tokens / Query', fontsize=10, fontweight='bold', color='#1E293B')
    ax2.set_ylabel('Accuracy (%)', fontsize=10, fontweight='bold', color='#1E293B')
    ax2.set_title('(B) Offline Policy Simulation (N=16,000): Observation Beats Debate',
                  fontsize=10.5, fontweight='bold', color='#0F172A', pad=5)
    ax2.tick_params(axis='both', which='major', labelsize=9)

    ax2.axvspan(235, 295, ymin=0.55, ymax=0.76, facecolor='#D1FAE5', alpha=0.45, zorder=1)
    ax2.text(265, 33, "Observation Scaling Gains (+5.8% acc, -28% tok)",
             fontsize=8.5, color='#065F46', fontweight='bold', ha='center',
             bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFFF', edgecolor='#34D399', alpha=0.95))

    plt.tight_layout()
    plt.savefig('naacl/figures/fig3_pareto_frontier.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created enlarged, readable fig3_pareto_frontier.png successfully.")

if __name__ == '__main__':
    create_stacked_results_figure()
