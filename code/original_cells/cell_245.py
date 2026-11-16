# Cell 8-(1): Initialize Network DataFrame and Analysis Period

# 1) Copy the source DataFrame for network construction
df_network = df_expl.copy()

# 2) Define analysis period
year_sel = list(range(2000, 2024)) # 2000 - 2023