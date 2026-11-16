# Cell 7-(2a): t-SNE LLM Highlight by Period (2000–2016 vs 2017–2023)
#  5개 기간별로 t-SNE 산점도에서 LLM 서브타입을 강조하고, 중국(CN) LLM만 별도 표시합니다
# ---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

# 1) 5년 단위 기간 정의
periods = [
    ("2000–2004", range(2000, 2005)),
    ("2005–2009", range(2005, 2010)),
    ("2010–2014", range(2010, 2015)),
    ("2015–2019", range(2015, 2020)),
    ("2020–2024", range(2020, 2025))
]

# 2) 연도 및 국가 정보 vis_df에 추가
plot_df["year"]         = df_pred["year"].values          # ── 출원 연도
plot_df["country_code"] = df_pred["country_code"].values  # ── 국가 코드

# 3) LLM 강조 색상
llm_color = palette_map["LLM"]

# 4) Figure & Axes 설정 (1행 5열, 축 공유)
fig, axes = plt.subplots(1, len(periods), figsize=(20, 4), sharex=True, sharey=True)

# 5) 각 기간별 산점도 그리기
for ax, (title, yrange) in zip(axes, periods):
    sub      = plot_df[plot_df["year"].isin(yrange)]      # ── 해당 기간 데이터
    mask_llm = sub["Subtype"] == "LLM"                    # ── LLM 점 마스크
    mask_cn  = mask_llm & (sub["country_code"] == "CN")   # ── 중국 LLM만

    # 5.1 Other 서브타입 점들 회색으로 표시
    ax.scatter(
        sub.loc[~mask_llm, "tSNE1"],
        sub.loc[~mask_llm, "tSNE2"],
        c="lightgray", alpha=0.6, s=30,
        edgecolor="white", label="Other"
    )

    # 5.2 모든 LLM 점들 강조 색상으로 표시
    ax.scatter(
        sub.loc[mask_llm, "tSNE1"],
        sub.loc[mask_llm, "tSNE2"],
        c=[llm_color], alpha=0.6, s=30,
        edgecolor="white", label="LLM"
    )

    # 5.3 중국(CN) LLM 점만 흰 배경+빨간 테두리로 강조
    ax.scatter(
        sub.loc[mask_cn, "tSNE1"],
        sub.loc[mask_cn, "tSNE2"],
        facecolors="white", edgecolors="#d62728",
        linewidths=0.8, alpha=0.95, s=65,
        label="LLM (CN)"
    )

    # 5.4 축 제목 및 라벨 설정
    ax.set_title(f"t-SNE: LLM Highlight ({title})")
    ax.set_xlabel("t-SNE 1")
    if ax is axes[0]:
        ax.set_ylabel("t-SNE 2")
        ax.legend(title="Subtype", bbox_to_anchor=(1.05, 1), loc="upper left")

# 6) 레이아웃 정리 및 출력
plt.tight_layout()
plt.show()
