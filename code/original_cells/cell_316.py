# Cell 7-(1b3)-FIX2: add threshold info into legend

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df_plot = df_pred.copy()
if df_plot["year"].dtype.kind not in ("i", "u"):
    df_plot["year"] = df_plot["year"].astype(int)

# 1) 신뢰도 기준 라벨링
labels = np.select(
    [
        df_plot["genai_confidence_raw"] >= thr_hi,
        df_plot["genai_confidence_raw"] <= thr_lo
    ],
    ["GenAI", "NonGenAI"],
    default=None
)
df_plot["genai_conf_bin"] = pd.Series(labels, dtype="object")

# 2) 결측 제거
df_plot = df_plot.dropna(subset=["genai_conf_bin", "cpc_cluster_dist_cos", "year"])

# 3) 연도 × 그룹 평균과 95% CI
dist_stats = (
    df_plot.groupby(["year", "genai_conf_bin"])["cpc_cluster_dist_cos"]
           .agg(mean="mean", std=lambda s: s.std(ddof=1), n="count")
           .reset_index()
)
dist_stats["se"] = dist_stats["std"] / np.sqrt(dist_stats["n"])
dist_stats["ci_lower"] = dist_stats["mean"] - 1.96 * dist_stats["se"]
dist_stats["ci_upper"] = dist_stats["mean"] + 1.96 * dist_stats["se"]

# # 4) 시각화
# plt.figure(figsize=(10, 6))
# colors = {"GenAI": "red", "NonGenAI": "blue"}
# labels_map = {
#     "GenAI": f"GenAI (≥ {thr_hi})",
#     "NonGenAI": f"NonGenAI (≤ {thr_lo})"
# }

# for label in ["GenAI", "NonGenAI"]:
#     sub = dist_stats[dist_stats["genai_conf_bin"] == label].sort_values("year")
#     if sub.empty:
#         continue
#     plt.plot(sub["year"], sub["mean"], label=labels_map[label], color=colors.get(label), linewidth=2)
#     plt.fill_between(sub["year"], sub["ci_lower"], sub["ci_upper"],
#                      color=colors.get(label), alpha=0.2)

# plt.title("Mean CPC Cluster Cosine Distance by Year (95% CI)\nRebinned by genai_confidence_raw")
# plt.xlabel("Year")
# plt.ylabel("Cosine Distance to CPC Cluster")
# plt.legend()
# plt.grid(True, alpha=0.4)
# plt.tight_layout()
# 

# 4) 시각화
plt.figure(figsize=(10, 6))
colors = {"GenAI": "red", "NonGenAI": "blue"}
labels_map = {
    "GenAI": f"GenAI (≥ {thr_hi})",
    "NonGenAI": f"NonGenAI (≤ {thr_lo})"
}

for label in ["GenAI", "NonGenAI"]:
    sub = dist_stats[dist_stats["genai_conf_bin"] == label].sort_values("year")
    if sub.empty:
        continue
    plt.plot(sub["year"], sub["mean"], label=labels_map[label],
             color=colors.get(label), linewidth=2)
    plt.fill_between(sub["year"], sub["ci_lower"], sub["ci_upper"],
                     color=colors.get(label), alpha=0.2)

#  2017 기준선 추가
plt.axvline(2017, color="black", linestyle="--", linewidth=1.5, label="2017 cutoff")

plt.title("Mean CPC Cluster Cosine Distance by Year (95% CI)\nRebinned by genai_confidence_raw")
plt.xlabel("Year")
plt.ylabel("Cosine Distance to CPC Cluster")
plt.legend()
plt.grid(False)   #  회색 그리드 제거
plt.tight_layout()


