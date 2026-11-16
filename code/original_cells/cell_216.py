# Cell 7-(4e): t‑SNE by 5‑Year Periods
# ── Ensure year is integer ──
vis_df_tsne["year"] = vis_df_tsne["year"].astype(int)

# ── Define the 5‑year bins ──
periods = [
    ("2000–2004", range(2000, 2005)),
    ("2005–2009", range(2005, 2010)),
    ("2010–2014", range(2010, 2015)),
    ("2015–2019", range(2015, 2020)),
    ("2020–2024", range(2020, 2025))
]
# ── Prepare subplots (3×2 grid, last for legend) ──
fig, axes = plt.subplots(3, 2, figsize=(12, 18))
axes = axes.flatten()

for i, (label, yrs) in enumerate(periods):
    ax = axes[i]
    sub = vis_df_tsne[vis_df_tsne["year"].isin(yrs)]

    # Masks
    m_llm    = sub["technology_type"] == "LLM"
    m_oth    = ~m_llm
    m_kr     = m_llm & (sub["country_code"] == "KR")
    m_us     = m_llm & (sub["country_code"] == "US")
    m_cn     = m_llm & (sub["country_code"] == "CN")
    m_etc    = m_llm & ~m_kr & ~m_us & ~m_cn

    # Plot layers
    ax.scatter(sub.loc[m_oth, "tSNE1"], sub.loc[m_oth, "tSNE2"],
               color="#EEEEEE", alpha=0.07, s=50, edgecolors="none")
    ax.scatter(sub.loc[m_etc, "tSNE1"], sub.loc[m_etc, "tSNE2"],
               color="salmon", alpha=0.8, s=50, edgecolors="white", linewidths=0.3)
    ax.scatter(sub.loc[m_kr, "tSNE1"], sub.loc[m_kr, "tSNE2"],
               facecolors="white", edgecolors="#2ca02c",
               linewidths=0.8, alpha=0.95, s=65)
    ax.scatter(sub.loc[m_us, "tSNE1"], sub.loc[m_us, "tSNE2"],
               facecolors="white", edgecolors="#1f77b4",
               linewidths=0.8, alpha=0.95, s=65)
    ax.scatter(sub.loc[m_cn, "tSNE1"], sub.loc[m_cn, "tSNE2"],
               facecolors="white", edgecolors="#d62728",
               linewidths=0.8, alpha=0.95, s=65)

    ax.set_title(label)
    ax.set_xlabel("t‑SNE 1")
    ax.set_ylabel("t‑SNE 2")

# Remove empty 6th plot
fig.delaxes(axes[-1])

# ── Legend panel ──
leg_ax = fig.add_subplot(3, 2, 6)
leg_ax.axis("off")
handles = [
    Line2D([0],[0], marker="o", linestyle="", markerfacecolor="#EEEEEE", alpha=0.07, markersize=8, label="Others"),
    Line2D([0],[0], marker="o", linestyle="", markerfacecolor="salmon", markeredgecolor="white", alpha=0.8, markersize=8, label="LLM (others)"),
    Line2D([0],[0], marker="o", linestyle="", markerfacecolor="white", markeredgecolor="#2ca02c", alpha=0.95, markersize=8, label="LLM (KR)"),
    Line2D([0],[0], marker="o", linestyle="", markerfacecolor="white", markeredgecolor="#1f77b4", alpha=0.95, markersize=8, label="LLM (US)"),
    Line2D([0],[0], marker="o", linestyle="", markerfacecolor="white", markeredgecolor="#d62728", alpha=0.95, markersize=8, label="LLM (CN)")
]
leg_ax.legend(handles=handles, title="Technology Type", loc="center")

plt.tight_layout()
plt.subplots_adjust(right=0.88)  # make space for legend panel
plt.show()