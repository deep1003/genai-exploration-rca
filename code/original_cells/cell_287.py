## **11-(1): Panel Regression with Fixed Effects
# 1) Create squared term
df_final["I_cpc2"] = df_final["cpc_cluster_dist_cos"] ** 2

# 2) Standardise (z-score) the continuous variables
from sklearn.preprocessing import StandardScaler

vars_to_norm = [
    "inventor_cet",
    "cpc_cluster_dist_cos",
    "I_cpc2",
    "num_inventors",
    "num_applicants",
    "wips_family_pub_count",
    "cited_by_count",
    "citations_count",
    "num_claims"
]

scaler = StandardScaler()
df_final[[f"{v}_z" for v in vars_to_norm]] = scaler.fit_transform(
    df_final[vars_to_norm]
)

# 3) Drop rows with infinite or missing values in y, X or FE keys
df_final.replace([np.inf, -np.inf], np.nan, inplace=True)
mask = (
    df_final["rca_y1"].notna()
    & df_final["rca_y0"].notna()
    & df_final[[f"{v}_z" for v in vars_to_norm]].notna().all(axis=1)
    & df_final["year"].notna()
    & df_final["country_code"].notna()
    & df_final["cpc_code"].notna()
)
df_final = df_final.loc[mask].copy()

# 4) Panel regression (three-way FE, clustered SE)
import statsmodels.api as sm

y = df_final["rca_y1"]
X = sm.add_constant(df_final[["rca_y0"] + [f"{v}_z" for v in vars_to_norm]])

res = sm.OLS(y, X).fit(
    absorb=["year", "country_code", "cpc_code"],
    cov_type="cluster",
    cov_kwds={"groups": df_final["country_code"]}
)

print(res.summary())

# 5) Combined CPC distance effect plot (orange line + legend)
import numpy as np
import matplotlib.pyplot as plt

params     = res.params
beta_const = params["const"]
beta_rca0  = params["rca_y0"]
beta1      = params["cpc_cluster_dist_cos_z"]
beta2      = params["I_cpc2_z"]

rca0_mean = df_final["rca_y0"].mean()

x    = np.linspace(
    df_final["cpc_cluster_dist_cos_z"].min(),
    df_final["cpc_cluster_dist_cos_z"].max(),
    100
)
x_sq = x ** 2

y_pred = beta_const + beta_rca0 * rca0_mean + beta1 * x + beta2 * x_sq

plt.figure(figsize=(8, 5))
plt.plot(
    x, y_pred,
    color="orange",
    linewidth=2,
    label="Cluster distance effect"
)
plt.xlabel(
    "Combined standardised CPC distance\n"
    "(β₁·cpc_cluster_dist_cos_z + β₂·I_cpc2_z)"
)
plt.ylabel("Predicted RCA at t+1")
plt.title("Effect of combined CPC cluster distance on predicted RCA")
plt.axhline(0, color="grey", linestyle=":")
plt.grid(alpha=0.3)
plt.legend(frameon=False)
plt.tight_layout()

