import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load Data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, 'data', 'experiment_results.csv')
output_img_path = os.path.join(BASE_DIR, 'data', 'visualize_results.png')

df = pd.read_csv(csv_path)

# Set Visual Style
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.suptitle('32-Scenario Insider Threat Evaluation Summary', fontsize=16, fontweight='bold', y=1.02)

# Color Palette Definitions
risk_order = ['Low', 'Medium', 'High']
colors_risk = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}

# ---------------------------------------------------------
# CHART 1: Deterministic vs LLM Risk Level Comparison
# ---------------------------------------------------------
det_counts = df['Deterministic_Risk'].value_counts().reindex(risk_order, fill_value=0)
llm_counts = df['LLM_Risk'].value_counts().reindex(risk_order, fill_value=0)

comp_df = pd.DataFrame({
    'Deterministic (Layer 1)': det_counts,
    'LLM Contextual (Layer 2)': llm_counts
})

comp_df.plot(kind='bar', ax=axes[0], color=['#3498db', '#e74c3c'], width=0.7)
axes[0].set_title('1. Risk Distribution Shift', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Risk Level')
axes[0].set_ylabel('Number of Scenarios')
axes[0].set_xticklabels(risk_order, rotation=0)
axes[0].legend(title='Engine Layer')

# Add numbers on top of bars
for p in axes[0].patches:
    if p.get_height() > 0:
        axes[0].annotate(f"{int(p.get_height())}", 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha='center', va='center', xytext=(0, 5), textcoords='offset points')

# ---------------------------------------------------------
# CHART 2: LLM Decision Impact (Pie Chart)
# ---------------------------------------------------------
override_counts = df['Override_Status'].value_counts()
pie_colors = ['#2ecc71' if 'Maintained' in x else '#e67e22' for x in override_counts.index]

wedges, texts, autotexts = axes[1].pie(
    override_counts, 
    labels=override_counts.index, 
    autopct='%1.1f%%',
    startangle=140,
    colors=pie_colors,
    explode=[0.05 if 'Overridden' in x else 0 for x in override_counts.index],
    textprops=dict(color="black", fontweight='bold')
)
axes[1].set_title('2. LLM Contextual Decision Impact', fontsize=12, fontweight='bold')

# ---------------------------------------------------------
# CHART 3: Final LLM Risk Breakdown by Role
# ---------------------------------------------------------
role_risk_df = pd.crosstab(df['Role'], df['LLM_Risk']).reindex(columns=risk_order, fill_value=0)
role_risk_df.plot(kind='bar', stacked=True, ax=axes[2], color=[colors_risk[r] for r in risk_order], width=0.5)

axes[2].set_title('3. Final Risk Level by Organizational Role', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Role')
axes[2].set_ylabel('Number of Scenarios')
axes[2].set_xticklabels(role_risk_df.index, rotation=0)
axes[2].legend(title='Final LLM Risk')

# Save Visualization
plt.tight_layout()
plt.savefig(output_img_path, dpi=300, bbox_inches='tight')
print(f"[SUCCESS] Visualization saved successfully to: '{output_img_path}'")