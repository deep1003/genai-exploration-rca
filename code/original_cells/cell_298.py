# Cell 11-(4): Interaction with num_inventors_z & moderation plot in one
# ────────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# 1) Interaction terms (num_inventors_z)
df_final["cpc_dist_x_inventors_z"]  = (
    df_final["cpc_cluster_dist_cos_z"] * df_final["num_inventors_z"]
)
df_final["I_cpc2_x_inventors_z"]    = (
    df_final["I_cpc2_z"]        * df_final["num_inventors_z"]
)

# 2) Three-way FE OLS model fit (including interactions)
vars_int = (
    ["rca_y0"] +
    [f"{v}_z" for v in vars_to_norm] +
    ["cpc_dist_x_inventors_z", "I_cpc2_x_inventors_z"]
)
X_int = sm.add_constant(df_final[vars_int])
y_int = df_final["rca_y1"]

res_int = sm.OLS(y_int, X_int).fit(
    absorb=["year", "country_code", "cpc_code"],
    cov_type="cluster",
    cov_kwds={"groups": df_final["country_code"]}
)

# 3) Print regression summary
print(res_int.summary())

# 4) Moderation plot: effect of num_inventors_z
params    = res_int.params
const     = params.get("const", 0.0)
rca0_mean = df_final["rca_y0"].mean()

# X axis: standardized cpc_cluster_dist_cos_z and its square
x  = np.linspace(df_final["cpc_cluster_dist_cos_z"].min(),
                 df_final["cpc_cluster_dist_cos_z"].max(), 100)
x2 = x**2

# Levels of num_inventors_z: −1SD, mean, +1SD
levels = {"Low (−1 SD)": -1, "Mean (0)": 0, "High (+1 SD)": 1}

# Prediction function (linear + quadratic + interaction)
def predict_rca(c1, c2, nz):
    return (
        const
        + params["rca_y0"]                   * rca0_mean
        + params["cpc_cluster_dist_cos_z"]       * c1
        + params["I_cpc2_z"]                 * c2
        + params["num_inventors_z"]          * nz
        + params["cpc_dist_x_inventors_z"]   * (c1 * nz)
        + params["I_cpc2_x_inventors_z"]     * (c2 * nz)
    )

# 5) Plot
plt.figure(figsize=(8, 5))
for label, nz in levels.items():
    plt.plot(x, predict_rca(x, x2, nz), label=label, linewidth=2)

plt.xlabel("Standardised CPC cluster distance (cpc_cluster_dist_cos_z)")
plt.ylabel("Predicted RCA at t+1 (rca_y1)")
plt.title("Moderation effect of inventor count\non CPC cluster distance → RCA")
plt.axhline(0, color="grey", linewidth=0.8, linestyle=":")
plt.grid(alpha=0.3)
plt.legend(title="num_inventors_z", frameon=False)
plt.tight_layout()

