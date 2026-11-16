# Cell 9-(2): Combined stacked bar chart for US, CN, KR with country-based colors and Core-only annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Focus countries and their colors
focus_countries = ["US", "CN", "KR"]
country_colors = {
    "US": "#1f77b4",  # blue
    "CN": "#d62728",  # red
    "KR": "#2ca02c",  # green
}
periphery_color = "#CCCCCC"  # light gray for remainder

# Prepare x‐axis
periods = df_summary.index.tolist()
indices = np.arange(len(periods))
width = 0.25  # space for three bars per period

fig, ax = plt.subplots(figsize=(12, 6))

# Total core nodes per period
total_cores = df_summary["Core Size"].values

for i, country in enumerate(focus_countries):
    # Country's core node counts
    core_counts = df_summary[f"{country} Core Nodes"].values
    # Convert to percentage of total cores
    core_perc = core_counts / total_cores * 100
    # Remainder up to 100%
    rem_perc = 100 - core_perc

    # Offset for each country bar
    pos = indices + (i - 1) * width

    # Draw periphery (remainder) in gray
    ax.bar(pos, rem_perc, width,
           bottom=core_perc, color=periphery_color, edgecolor='none')
    # Draw core segment in country color
    bars = ax.bar(pos, core_perc, width,
                  color=country_colors[country], label=country, edgecolor='none')

    # Annotate only core percentages
    for bar in bars:
        h = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2
        ax.text(x, h / 2,
                f"{h:.1f}%",
                ha="center", va="center",
                fontsize=8, color="white")

# Axis labels and title
ax.set_xticks(indices)
ax.set_xticklabels(periods, rotation=0)
ax.set_xlabel("Period")
ax.set_ylabel("Percentage of Core Nodes (%)")
ax.set_title("Core Composition by Period for US, CN, KR")

# Legend showing countries
country_patches = [Patch(facecolor=country_colors[c], label=c) for c in focus_countries]
ax.legend(handles=country_patches, title="Country", loc="upper left")

plt.tight_layout()

