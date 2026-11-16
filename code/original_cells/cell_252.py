# Cell 8-(3) Build Co‑Authorship Graphs for 5‑Year Periods

# 1) Define the 5‑year bins
periods = [
    ("2000–2004", range(2000, 2005)),
    ("2005–2009", range(2005, 2010)),
    ("2010–2014", range(2010, 2015)),
    ("2015–2019", range(2015, 2020)),
    ("2020–2024", range(2020, 2025)),
]

# 2) For each period, build and prune the subgraph
G_periods = {}
no_nodes = 1000

for label, yrs in periods:
    inv_lists = (
        df_network_llm[df_network_llm["year"].isin(yrs)]
            .groupby("appl_id")["inventor"]
            .agg(lambda x: x.unique().tolist())
    )
    Gp = nx.Graph()
    for invs in inv_lists:
        if len(invs) < 2:
            continue
        for i, a in enumerate(invs):
            for b in invs[i+1:]:
                if Gp.has_edge(a, b):
                    Gp[a][b]["weight"] += 1
                else:
                    Gp.add_edge(a, b, weight=1)
    degs = dict(Gp.degree())
    top = sorted(degs, key=degs.get, reverse=True)[:no_nodes]
    G_periods[label] = Gp.subgraph(top).copy()
    print(f"{label}: nodes={G_periods[label].number_of_nodes()}, "
          f"edges={G_periods[label].number_of_edges()}")
