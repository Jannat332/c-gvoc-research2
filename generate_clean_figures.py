import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set publication style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

def create_simplified_architecture_figure():
    fig, ax = plt.subplots(figsize=(7.4, 3.2), dpi=300)
    ax.set_xlim(0, 7.4)
    ax.set_ylim(0, 3.2)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Palette
    c_blue_bg = '#EFF6FF'
    c_blue_border = '#3B82F6'
    c_green_bg = '#ECFDF5'
    c_green_border = '#10B981'
    c_amber_bg = '#FFFBEB'
    c_amber_border = '#F59E0B'

    # Stage 1: Diagnostic Signals
    rect1 = patches.FancyBboxPatch((0.15, 0.25), 2.1, 2.7, boxstyle="round,pad=0.08,rounding_size=0.12",
                                   linewidth=2.0, edgecolor=c_blue_border, facecolor=c_blue_bg)
    ax.add_patch(rect1)
    ax.text(1.2, 2.68, "Stage 1", fontsize=12, fontweight='bold', color='#1D4ED8', ha='center')
    ax.text(1.2, 2.38, "Diagnostic Signals", fontsize=11, fontweight='bold', color='#1E293B', ha='center')

    b1_1 = patches.FancyBboxPatch((0.3, 1.45), 1.8, 0.7, boxstyle="round,pad=0.04,rounding_size=0.06",
                                  linewidth=1.2, edgecolor='#93C5FD', facecolor='#FFFFFF')
    ax.add_patch(b1_1)
    ax.text(1.2, 1.9, "Document & Query", fontsize=9.5, fontweight='bold', color='#1E293B', ha='center')
    ax.text(1.2, 1.62, "Compressed Image + Text", fontsize=8.5, color='#475569', ha='center')

    b1_2 = patches.FancyBboxPatch((0.3, 0.45), 1.8, 0.85, boxstyle="round,pad=0.04,rounding_size=0.06",
                                  linewidth=1.2, edgecolor='#93C5FD', facecolor='#FFFFFF')
    ax.add_patch(b1_2)
    ax.text(1.2, 1.05, "State Telemetry", fontsize=9.5, fontweight='bold', color='#1E293B', ha='center')
    ax.text(1.2, 0.75, r"- Feature variance" + "\n" + r"- Dispersion $\hat{\sigma}$", fontsize=8.5, color='#334155', ha='center')

    # Arrow 1 -> 2
    ax.annotate('', xy=(2.55, 1.6), xytext=(2.30, 1.6),
                arrowprops=dict(facecolor='#475569', edgecolor='#475569', width=2.0, headwidth=7))

    # Stage 2: Value-of-Compute Gate
    rect2 = patches.FancyBboxPatch((2.60, 0.25), 2.2, 2.7, boxstyle="round,pad=0.08,rounding_size=0.12",
                                   linewidth=2.0, edgecolor=c_green_border, facecolor=c_green_bg)
    ax.add_patch(rect2)
    ax.text(3.7, 2.68, "Stage 2", fontsize=12, fontweight='bold', color='#047857', ha='center')
    ax.text(3.7, 2.38, "Value-of-Compute Gate", fontsize=11, fontweight='bold', color='#1E293B', ha='center')

    b2_1 = patches.FancyBboxPatch((2.75, 1.45), 1.9, 0.7, boxstyle="round,pad=0.04,rounding_size=0.06",
                                  linewidth=1.2, edgecolor='#6EE7B7', facecolor='#FFFFFF')
    ax.add_patch(b2_1)
    ax.text(3.7, 1.90, r"$\mathcal{V}_{\mathrm{LCB}} = \frac{\Delta \hat{P}_a - \kappa \hat{\sigma}_a}{\mathrm{Cost}(a)}$",
            fontsize=10.5, fontweight='bold', color='#065F46', ha='center')
    ax.text(3.7, 1.60, "Conservative Gain / Cost", fontsize=8.0, color='#047857', ha='center')

    b2_2 = patches.FancyBboxPatch((2.75, 0.45), 1.9, 0.85, boxstyle="round,pad=0.04,rounding_size=0.06",
                                  linewidth=1.2, edgecolor='#6EE7B7', facecolor='#FFFFFF')
    ax.add_patch(b2_2)
    ax.text(3.7, 1.05, "Candidate Actions", fontsize=9.5, fontweight='bold', color='#1E293B', ha='center')
    ax.text(3.7, 0.75, "Stop | Crop | Table | Abstain", fontsize=8.5, fontweight='bold', color='#065F46', ha='center')

    # Arrow 2 -> 3
    ax.annotate('', xy=(5.05, 1.6), xytext=(4.85, 1.6),
                arrowprops=dict(facecolor='#475569', edgecolor='#475569', width=2.0, headwidth=7))

    # Stage 3: Targeted Execution
    rect3 = patches.FancyBboxPatch((5.10, 0.25), 2.15, 2.7, boxstyle="round,pad=0.08,rounding_size=0.12",
                                   linewidth=2.0, edgecolor=c_amber_border, facecolor=c_amber_bg)
    ax.add_patch(rect3)
    ax.text(6.17, 2.68, "Stage 3", fontsize=12, fontweight='bold', color='#B45309', ha='center')
    ax.text(6.17, 2.38, "Targeted Execution", fontsize=11, fontweight='bold', color='#1E293B', ha='center')

    b3_1 = patches.FancyBboxPatch((5.25, 1.85), 1.85, 0.42, boxstyle="round,pad=0.03,rounding_size=0.05",
                                  linewidth=1.0, edgecolor='#FCD34D', facecolor='#FFFFFF')
    ax.add_patch(b3_1)
    ax.text(6.17, 2.05, "Stop: Emit Answer", fontsize=8.5, fontweight='bold', color='#1E293B', ha='center')

    b3_2 = patches.FancyBboxPatch((5.25, 1.38), 1.85, 0.42, boxstyle="round,pad=0.03,rounding_size=0.05",
                                  linewidth=1.0, edgecolor='#FCD34D', facecolor='#FFFFFF')
    ax.add_patch(b3_2)
    ax.text(6.17, 1.58, "Crop: High-Res Visual", fontsize=8.5, fontweight='bold', color='#B45309', ha='center')

    b3_3 = patches.FancyBboxPatch((5.25, 0.91), 1.85, 0.42, boxstyle="round,pad=0.03,rounding_size=0.05",
                                  linewidth=1.0, edgecolor='#FCD34D', facecolor='#FFFFFF')
    ax.add_patch(b3_3)
    ax.text(6.17, 1.11, "Table: Re-Parse Grid", fontsize=8.5, fontweight='bold', color='#B45309', ha='center')

    b3_4 = patches.FancyBboxPatch((5.25, 0.44), 1.85, 0.42, boxstyle="round,pad=0.03,rounding_size=0.05",
                                  linewidth=1.0, edgecolor='#FCD34D', facecolor='#FFFFFF')
    ax.add_patch(b3_4)
    ax.text(6.17, 0.64, "Abstain: Safe Fallback", fontsize=8.5, fontweight='bold', color='#64748B', ha='center')

    plt.tight_layout()
    plt.savefig('naacl/figures/fig2_gvoc_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Regenerated clean, high-contrast fig2_gvoc_architecture.png successfully.")

if __name__ == '__main__':
    create_simplified_architecture_figure()
