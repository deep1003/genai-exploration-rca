# GenAI Exploration and Revealed Comparative Advantage

Research materials for **Technological exploration distance, revealed comparative
advantage, and the U.S.-China dual-core reconfiguration of generative AI innovation**.
One-Sun Cho and Youngsam Chun. Working manuscript, 2026.

## Scope

This public release contains aggregate tables, regression coefficients and
covariances, plot-series exports, nine vector figures, analysis and figure code,
and provenance. The manuscript is under revision. No journal acceptance or
complete historical replication is claimed.

| Re-estimated specification | Observations | Distance | Second moment |
| --- | ---: | ---: | ---: |
| Equal-weight country-CPC-year cells with FE | 78,615 | 0.0465 | -0.0406 |
| Patent-CPC rows with FE | 506,311 | -0.0322 | 0.0204 |
| Recovered pooled OLS | 510,673 | 0.1117 | -0.1068 |

The equal-cell coefficients meet the 5% threshold; the row-level FE distance
terms do not. Mean squared distance is not the square of mean distance.
Opposite coefficient signs alone do not establish an interior inverted U.
The originally recovered `OLS.fit(absorb=...)` did not implement fixed effects.
The genuine FE coefficients were checked with two independent implementations.

Table 3 uses archived application counts in four sampled regions. Table 4
uses US plus CN keyword occurrences, not distinct patent counts. Cluster
labels in those archived tables are not a validated crosswalk to regenerated
embedding clusters. Figures 5 and 6 retain historical pooled illustrations,
not new fixed-effects predictions. Figure 7's historical event-study reference
implementation has not been revalidated.

## Contents

- `data/tables/`: integer counts, recomputed percentages, coefficients, covariances.
- `data/figure_series/`: non-identifying aggregate line-series exports.
- `figures/`: vector figure outputs; 3 shares one legend; 4 has an internal legend.
- `code/historical/`: preserved local analysis and restoration scripts.
- `code/original_cells/`: original plotting-cell source, without notebook outputs.
- `provenance/`: source hashes, sample metadata, exclusions and file checksums.
- `code/verify_release.py`: portable, no-plot smoke and arithmetic checks.

Run `python3 code/verify_release.py` from this directory. It uses only the
Python standard library and writes no images. Historical scripts retain their
original workspace assumptions and are archival source, not a one-command
full replication environment. Full model and embedding regeneration requires
the non-public source inputs and their applicable dependencies.

## Data Access

Row-level patent-provider data, full notebook outputs, personal records and
patent-level embedding coordinates are not included. Redistribution rights
for PATSTAT/WIPS-derived inputs have not been confirmed. Obtain source data
under the relevant providers' terms; hashes identify the particular recovered
input, but alternative provider releases may not reproduce the same cohort.
The present release permits inspection of aggregate calculations and code;
it is not a public release of every underlying observation.

No blanket licence is asserted over third-party patent-provider data or
publisher materials. Rights and data-access restrictions remain applicable.
