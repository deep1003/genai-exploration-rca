# Cell 11-(3): Interaction model + regression summary + moderation plot
# ────────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# 0) (필요시) 변수 전처리 – z-score 표준화 등
#    df_final, vars_to_norm 등이 이미 정의되어 있다고 가정합니다.

# 1) 상호작용 항 생성
df_final["cpc_dist_x_inv_z"] = df_final["cpc_cluster_dist_cos_z"] * df_final["inventor_cet_z"]
df_final["I_cpc2_x_inv_z"]   = df_final["I_cpc2_z"]        * df_final["inventor_cet_z"]

# 2) 3-way FE OLS 모형 적합 (interaction 포함)
vars_interact = (
    ["rca_y0"] +
    [f"{v}_z" for v in vars_to_norm] +
    ["cpc_dist_x_inv_z", "I_cpc2_x_inv_z"]
)
X = sm.add_constant(df_final[vars_interact])
y = df_final["rca_y1"]
res_int = sm.OLS(y, X).fit(
    absorb=["year", "country_code", "cpc_code"],
    cov_type="cluster",
    cov_kwds={"groups": df_final["country_code"]}
)

# 3) 회귀 결과 요약 출력
print(res_int.summary())

# 4) 조절효과 시각화 준비
params = res_int.params
const = params.get("const", 0.0)

# X축 범위 및 2차항
x = np.linspace(df_final["cpc_cluster_dist_cos_z"].min(),
                df_final["cpc_cluster_dist_cos_z"].max(), 100)
x2 = x**2

# inventor_cet_z 수준
levels = {"Low (−1 SD)": -1, "Mean (0)": 0, "High (+1 SD)": 1}

# 예측 함수
def predict(c1, c2, inv):
    return (
        const
        + params["rca_y0"]            * df_final["rca_y0"].mean()
        + params["cpc_cluster_dist_cos_z"]* c1
        + params["I_cpc2_z"]          * c2
        + params["inventor_cet_z"]    * inv
        + params["cpc_dist_x_inv_z"]  * (c1 * inv)
        + params["I_cpc2_x_inv_z"]    * (c2 * inv)
    )

# 5) 그래프
plt.figure(figsize=(8,5))
for name, inv in levels.items():
    plt.plot(x, predict(x, x2, inv), label=name, linewidth=2)

plt.xlabel("Standardised CPC cluster distance (cpc_cluster_dist_cos_z)")
plt.ylabel("Predicted RCA at t+1 (rca_y1)")
plt.title("Moderation Effect of Inventor Centrality\n(Linear + Quadratic Terms)")
plt.axhline(0, color="grey", linewidth=0.8, linestyle=":")
plt.grid(alpha=0.3)
plt.legend(title="inventor_cet_z", frameon=False)
plt.tight_layout()

