## **11-(2): Interaction model estimation & moderation plot in one**
# ────────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# 0) Interaction terms 생성 (z-score 변수 곱)
df_final["cpc_dist_x_wips_z"] = (
    df_final["cpc_cluster_dist_cos_z"] * df_final["wips_family_pub_count_z"]
)
df_final["I_cpc2_x_wips_z"]   = (
    df_final["I_cpc2_z"] * df_final["wips_family_pub_count_z"]
)

# 1) 3-way FE OLS 모형 적합 (interaction 포함)
vars_int = (
    ["rca_y0"]                                   # lagged RCA
    + [f"{v}_z" for v in vars_to_norm]           # 표준화된 연속형 통제변수
    + ["cpc_dist_x_wips_z", "I_cpc2_x_wips_z"]    # interaction terms
)
X_int = sm.add_constant(df_final[vars_int])
y_int = df_final["rca_y1"]

res_int = sm.OLS(y_int, X_int).fit(
    absorb=["year", "country_code", "cpc_code"], 
    cov_type="cluster",
    cov_kwds={"groups": df_final["country_code"]}
)

# 회귀 결과 요약 출력
print(res_int.summary())

# 2) moderation plot: wips_family_pub_count_z에 따른 조절효과
params = res_int.params
const  = params.get("const", 0.0)

# X축 범위 설정 및 2차항 계산
x = np.linspace(
    df_final["cpc_cluster_dist_cos_z"].min(),
    df_final["cpc_cluster_dist_cos_z"].max(),
    100
)
x2 = x ** 2

# wips_family_pub_count_z 수준 정의 (−1 SD, 0, +1 SD)
levels = {
    "Low (−1 SD)": -1,
    "Mean (0)":     0,
    "High (+1 SD)": 1
}

# 예측 함수 정의 (1차, 2차, interaction 포함)
def predict_rca(c1, c2, w):
    return (
        const
        + params["rca_y0"]                       * df_final["rca_y0"].mean()
        + params["cpc_cluster_dist_cos_z"]           * c1
        + params["I_cpc2_z"]                     * c2
        + params["wips_family_pub_count_z"]      * w
        + params["cpc_dist_x_wips_z"]            * (c1 * w)
        + params["I_cpc2_x_wips_z"]              * (c2 * w)
    )

# 그래프 그리기
plt.figure(figsize=(8, 5))
for label, w in levels.items():
    plt.plot(x, predict_rca(x, x2, w), linewidth=2, label=label)

plt.xlabel("Standardised CPC cluster distance (cpc_cluster_dist_cos_z)")
plt.ylabel("Predicted RCA at t+1 (rca_y1)")
plt.title("Moderation effect of family publications\non CPC cluster distance → RCA relationship")
plt.axhline(0, color="grey", linewidth=0.8, linestyle=":")
plt.grid(alpha=0.3)
plt.legend(title="wips_family_pub_count_z", frameon=False)
plt.tight_layout()

