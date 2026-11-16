# ================================
# DiD on convergence of CPC-level cluster distance (GenAI vs Others by confidence thresholds)
#  • Treatment: genai_conf_bin == "GenAI"  [rebinned by genai_confidence_raw: GenAI ≥ thr_hi, NonGenAI ≤ thr_lo]
#  • Uncertain (thr_lo < p < thr_hi) is dropped
#  • Outcome: mean of cpc_cluster_dist_cos (fallback: dist_cluster_cos, cpc_cluster_dist)
#  • FE: country & year, cluster-robust SE by country
# ================================
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import re

# ---------- 0) Columns, thresholds, outcome ----------
df = df_pred.copy()

# Create thresholded bin variable
labels = np.select(
    [
        df["genai_confidence_raw"] >= thr_hi,
        df["genai_confidence_raw"] <= thr_lo
    ],
    ["GenAI", "NonGenAI"],
    default=None
)
df["genai_conf_bin"] = pd.Series(labels, dtype="object")

# Choose distance column
DIST_COL = (
    "cpc_cluster_dist_cos" if "cpc_cluster_dist_cos" in df.columns else
    ("dist_cluster_cos" if "dist_cluster_cos" in df.columns else
     ("cpc_cluster_dist" if "cpc_cluster_dist" in df.columns else None))
)
assert DIST_COL is not None and DIST_COL in df.columns, f"Distance column not found: {DIST_COL}"
assert {"year", "country_code", "genai_conf_bin"}.issubset(df.columns), "Require year, country_code, genai_conf_bin."

# Drop missing and uncertain band
df = df[df[DIST_COL].notna()].copy()
df = df[df["genai_conf_bin"].notna()].copy()

# ---------- 1) Tidy vars ----------
df["year_num"] = df["year"].astype(int)
df["country_code"] = df["country_code"].astype(str)
df["GenAI"] = (df["genai_conf_bin"] == "GenAI").astype(int)

BASE = 2017
POST_CUTOFF = BASE + 1  # 2018+
df["Post"] = (df["year_num"] >= POST_CUTOFF).astype(int)

# ---------- 2) Build country×year×GenAI means ----------
grp_keys = ["country_code", "year_num", "GenAI"]
panel = (
    df.groupby(grp_keys)[DIST_COL]
      .agg(Y="mean", n="count")
      .reset_index()
)

# Attach Post
panel = panel.merge(
    df[["country_code", "year_num", "Post"]].drop_duplicates(["country_code", "year_num"]),
    on=["country_code", "year_num"], how="left"
)
assert "Post" in panel.columns and panel["Post"].notna().all(), "Post was not attached to panel properly."

print("[panel] rows:", len(panel),
      "countries:", panel["country_code"].nunique(),
      "years:", panel["year_num"].nunique())

def finite_mask(X_df, y_vec=None):
    Xv = X_df.values
    mask = np.isfinite(Xv).all(axis=1)
    if y_vec is not None:
        mask &= np.isfinite(y_vec)
    return mask

# ---------- 3) DiD, explicit design matrix ----------
need_cols = ["Y", "GenAI", "Post", "country_code", "year_num"]
df_did = panel.loc[:, need_cols].dropna().copy()
assert df_did["country_code"].nunique() >= 2, "Need at least 2 clusters for cluster-robust SE."
df_did = df_did.reset_index(drop=True)

X_base = pd.DataFrame(
    {"Intercept": np.ones(len(df_did), dtype=float),
     "GenAI": df_did["GenAI"].astype(float).values,
     "Post":  df_did["Post"].astype(float).values},
    index=df_did.index,
)
X_base["GenAI_x_Post"] = X_base["GenAI"] * X_base["Post"]

d_cty  = pd.get_dummies(df_did["country_code"], prefix="C_cty", drop_first=True, dtype=float)
d_year = pd.get_dummies(df_did["year_num"],     prefix="C_year", drop_first=True, dtype=float)

X_did = pd.concat([X_base, d_cty, d_year], axis=1)
y_did = df_did["Y"].astype(float).values
grp_did = df_did["country_code"]

mask_did = finite_mask(X_did, y_did)
if not mask_did.all():
    print(f"[DiD] Dropping {(~mask_did).sum()} rows with NaN/Inf in design matrix.")
    X_did = X_did.loc[mask_did].copy()
    y_did = y_did[mask_did]
    grp_did = grp_did.loc[mask_did]

did_res = sm.OLS(y_did, X_did).fit(cov_type="cluster", cov_kwds={"groups": grp_did})
print("\n[DiD] GenAI × Post on mean distance (country–year means, thresholded bins)")
print(did_res.summary())

# ---------- 4) Event-study around 2017 ----------
WINDOW = 6
df_es = panel[(panel["year_num"] >= BASE - WINDOW) & (panel["year_num"] <= BASE + WINDOW)].copy()
df_es["rel_year"] = df_es["year_num"] - BASE
df_es = df_es.reset_index(drop=True)

taus = sorted(t for t in df_es["rel_year"].unique())
taus = [t for t in taus if t != -1]
for tau in taus:
    nm = f"DY_{'m'+str(abs(tau)) if tau < 0 else 'p'+str(tau)}"
    df_es[nm] = (df_es["rel_year"] == tau).astype(int)

inter_cols = []
for c in [c for c in df_es.columns if c.startswith("DY_") and df_es[c].sum() > 0]:
    ic = f"GenAI_x_{c}"
    df_es[ic] = df_es["GenAI"].astype(float) * df_es[c].astype(float)
    inter_cols.append(ic)

keep_cols = ["Y", "GenAI", "country_code", "year_num"] + inter_cols
df_es = df_es.loc[:, keep_cols].dropna().copy()
assert df_es["country_code"].nunique() >= 2, "Need at least 2 clusters for cluster-robust SE in event-study."
df_es = df_es.reset_index(drop=True)

X_es_base  = pd.DataFrame({"Intercept": np.ones(len(df_es), dtype=float)}, index=df_es.index)
X_es_inter = df_es[inter_cols].astype(float)
d_cty_es   = pd.get_dummies(df_es["country_code"], prefix="C_cty", drop_first=True, dtype=float)
d_year_es  = pd.get_dummies(df_es["year_num"],     prefix="C_year", drop_first=True, dtype=float)

X_es = pd.concat([X_es_base, X_es_inter, d_cty_es, d_year_es], axis=1)
y_es = df_es["Y"].astype(float).values
grp_es = df_es["country_code"]

mask_es = finite_mask(X_es, y_es)
if not mask_es.all():
    print(f"[Event-study] Dropping {(~mask_es).sum()} rows with NaN/Inf in design matrix.")
    X_es  = X_es.loc[mask_es].copy()
    y_es  = y_es[mask_es]
    grp_es = grp_es.loc[mask_es]

es_res = sm.OLS(y_es, X_es).fit(cov_type="cluster", cov_kwds={"groups": grp_es})
print("\n[Event-study] GenAI × relative years around 2017 (τ = -1 omitted, thresholded bins)")
print(es_res.summary())

# ---------- 5) Plot coefficients with 95 % CI (error bars style) ----------
coefs = es_res.params
ses   = es_res.bse
pvals = es_res.pvalues

years, beta, lo, hi, pv = [], [], [], [], []
for name, val in coefs.items():
    if name.startswith("GenAI_x_DY_"):
        m = re.search(r"DY_(p|m)(\d+)", name)
        if not m:
            continue
        tau = int(m.group(2)) * (1 if m.group(1) == "p" else -1)
        se = ses[name]
        years.append(tau)
        beta.append(val)
        lo.append(val - 1.96 * se)
        hi.append(val + 1.96 * se)
        pv.append(pvals[name])

# 기준기 τ = -1을 0으로 추가
years.append(-1); beta.append(0.0); lo.append(0.0); hi.append(0.0); pv.append(1.0)

if len(years) > 1:
    years, beta, lo, hi, pv = zip(*sorted(zip(years, beta, lo, hi, pv)))
    years = np.array(years); beta = np.array(beta); lo = np.array(lo); hi = np.array(hi); pv = np.array(pv)

    # yerr 계산
    yerr = np.vstack((beta - lo, hi - beta))

    plt.figure(figsize=(10, 6))

    # 점추정치 + 에러바
    plt.errorbar(
        years, beta,
        yerr=yerr,
        fmt="o", color="black", ecolor="black",
        elinewidth=1.5, capsize=4, label="Coefficient (GenAI × DY)"
    )

    # 기준선
    plt.axhline(0, color="black", linestyle="--", linewidth=1)
    plt.axvline(0, color="firebrick", linewidth=2, label="2017 (BASE)")

    # 유의성 별표
    yspan = float(np.nanmax(beta) - np.nanmin(beta) + 1e-9)
    for x, y, p in zip(years, beta, pv):
        stars = "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else ""))
        if stars and x != -1:
            plt.text(x, y + 0.03 * yspan, stars, ha="center", va="bottom", fontsize=10, color="black")

    plt.xlabel("Relative year (τ)")
    plt.ylabel("Mean distance difference (GenAI vs Others, thresholded)")
    plt.title("Event-study: Convergence of cluster distance for GenAI vs Others (error bars, 95% CI)")
    plt.legend()
    plt.tight_layout()
    
else:
    print("[Plot] Not enough ES coefficients to plot.")
