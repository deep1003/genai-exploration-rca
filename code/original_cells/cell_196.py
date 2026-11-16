# Cell 7-(2): t-SNE LLM Highlight by Period (2000–2023)
# 5개 기간(5년 단위)별로 t-SNE 좌표에 LLM 서브타입을 강조해 패널 산점도를 그립니다
# ------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# ── 5년 단위 기간 정의
periods = [
    ("2000–2004", range(2000, 2005)),
    ("2005–2009", range(2005, 2010)),
    ("2010–2014", range(2010, 2015)),
    ("2015–2019", range(2015, 2020)),
    ("2020–2024", range(2020, 2025))
]

# plot_df에 연도 정보 추가
plot_df["year"] = df_pred["year"].values

# LLM 강조 색상
llm_color = palette_map["LLM"]

# 5개의 패널(1행 5열) 생성, 축 공유
fig, axes = plt.subplots(1, len(periods), figsize=(20, 4), sharex=True, sharey=True)

for ax, (title, yrange) in zip(axes, periods):
    # 해당 기간 데이터 필터링
    sub = plot_df[plot_df["year"].isin(yrange)]
    
    # LLM 서브타입 마스크
    mask_llm = sub["Subtype"] == "LLM"
    
    # 비-LLM 점들 회색으로 표시
    ax.scatter(
        sub.loc[~mask_llm, "tSNE1"],
        sub.loc[~mask_llm, "tSNE2"],
        c="lightgray",
        alpha=0.6,
        s=30,
        edgecolor="white",
        label="Other"
    )
    
    # LLM 점들 강조 색상으로 표시
    ax.scatter(
        sub.loc[mask_llm, "tSNE1"],
        sub.loc[mask_llm, "tSNE2"],
        c=[llm_color],
        alpha=0.8,
        s=30,
        edgecolor="white",
        label="LLM"
    )
    
    ax.set_title(f"t-SNE: LLM Highlight ({title})")
    ax.set_xlabel("t-SNE 1")
    if ax is axes[0]:
        ax.set_ylabel("t-SNE 2")
        ax.legend(title="Subtype", bbox_to_anchor=(1.05, 1), loc="upper left")

plt.tight_layout()
plt.show()
