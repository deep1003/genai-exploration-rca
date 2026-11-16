# Cell 7-(4d): Prepare embeddings and t‑SNE coordinates
# 1) Assemble DataFrame for plotting
vis_df_tsne = pd.DataFrame({
    "tSNE1":           X_tsne[:, 0],
    "tSNE2":           X_tsne[:, 1],
    "technology_type": df_pred["seed_genai_type_label"].values, # seed_genai_type_label <- genai_subtype_pred
    "country_code":    df_pred["country_code"].astype(str).values,
    "year":            df_pred["year"].values              # if you have a 'year' column
    })
print("Prerequisites ready: vis_df_tsne shape =", vis_df_tsne.shape)