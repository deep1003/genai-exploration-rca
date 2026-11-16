# Cell 8-(2): Filter to LLM Patents

# 1) Get the list of appl_ids predicted as LLM (from your df_pred)
llm_appl_ids = df_pred.loc[
    df_pred["genai_pred"] == "GenAI",
    "appl_id"
].unique().tolist()

# 2) Keep only inventor–patent rows for those LLM appl_ids
df_network_llm = df_network[df_network["appl_id"].isin(llm_appl_ids)].copy()
print(f"Raw inventor–patent rows for LLM: {df_network_llm.shape[0]}")
