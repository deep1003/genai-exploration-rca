"""Insert source-backed table values without changing manuscript prose."""
import csv
import re


def insert_tables(body, directory):
    def rows(name):
        with (directory / name).open() as f:
            return list(csv.DictReader(f))

    t3 = rows('table3_restored_from_counts.csv')
    t4 = rows('table4_restored_from_counts.csv')
    for number, records, fields in [
        (3, t3, ['US_pct', 'CN_pct', 'other_included_pct']),
        (4, t4, ['US_pct', 'CN_pct']),
    ]:
        pattern = r'\\begin\{longtable\}.*?\\label\{tab:' + str(number) + r'\}.*?\\end\{longtable\}'
        # Start at the relevant table, not at a preceding longtable.
        pattern = r'\\begin\{longtable\}(?:(?!\\end\{longtable\}).)*?\\label\{tab:' + str(number) + r'\}(?:(?!\\end\{longtable\}).)*?\\end\{longtable\}'
        match = re.search(pattern, body, re.S)
        assert match, number
        block = match[0]
        lines = block.splitlines()
        candidates = [i for i, line in enumerate(lines) if re.match(r'[1-5]\. ', line)]
        assert len(candidates) == len(records)
        for i, record in zip(candidates, records):
            cells = lines[i].removesuffix(r'\\').split('&')
            cells[-len(fields):] = [' ' + f'{float(record[field]):.1f}' + ' ' for field in fields]
            lines[i] = '&'.join(cells) + r'\\'
        block = '\n'.join(lines)
        body = body[:match.start()] + block + body[match.end():]
    notes = {
        3: ('Shares are recalculated from archived application counts in notebook cell 289. '
            'The archived population uses LLM records where available and otherwise GenAI records, '
            'with RCA above one observed at the application level. The denominator includes only '
            'the United States, China, Korea and the European Union; ``All others'' means Korea '
            'plus the European Union, not all remaining countries. Cluster labels refer to the '
            'archived partition; no crosswalk to the regenerated embedding partition is assumed.'),
        4: ('Shares are recalculated from archived keyword-occurrence counts in notebook cell 234. '
            'The denominator is U.S. plus Chinese occurrences, not unique patent applications. '
            'The source concatenates available text fields and does not explicitly restrict the '
            'population to RCA above one or to GenAI records. Repeated mentions can contribute '
            'multiple times. Cluster labels refer to the archived partition.'),
    }
    for n, note in notes.items():
        start = body.index(r'\label{tab:' + str(n) + '}')
        pos = body.index(r'\emph{Note:}', start)
        body = body[:pos] + body[pos:].replace(r'\emph{Note:}', r'\emph{Notes:} ' + note, 1)

    coeff = {(r['model'], r['term']): r for r in rows('table2_reestimated_coefficients.csv')}
    models = ['equal_cell_threeway_fe', 'corrected_threeway_fe', 'recovered_pooled']
    terms = [
        ('cpc_cluster_dist_cos_z', 'Exploration distance'),
        ('I_cpc2_z', 'Squared exploration distance'),
        ('rca_y0', 'RCA above one at year $t$'),
        ('inventor_cet_z', 'Inventor centrality'),
        ('num_inventors_z', 'Number of inventors'),
        ('num_applicants_z', 'Number of applicants'),
        ('wips_family_pub_count_z', 'Patent-family publications'),
        ('cited_by_count_z', 'Forward citations'),
        ('citations_count_z', 'Backward citations'),
        ('num_claims_z', 'Number of claims'),
        ('const', 'Constant'),
    ]
    table = [r'\begin{table}[p]', r'\centering\small',
             r'\caption{Exploration distance and subsequent comparative advantage: source-data re-estimates.}\label{tab:2}',
             r'\begin{tabular}{p{.36\linewidth}rrr}\toprule',
             r' & Equal-cell FE & Patent--CPC FE & Pooled replay \\\midrule']
    for term, label in terms:
        values, errors = [], []
        for model in models:
            row = coeff.get((model, term))
            if row is None:
                values.append(r'\textemdash'); errors.append('')
                continue
            p = float(row['pvalue'])
            stars = '***' if p < .01 else '**' if p < .05 else '*' if p < .1 else ''
            values.append(f"{float(row['coefficient']):.4f}" + ('$^{' + stars + '}$' if stars else ''))
            errors.append('(' + f"{float(row['std_error']):.4f}" + ')')
        table.extend([label + ' & ' + ' & '.join(values) + r' \\', ' & ' + ' & '.join(errors) + r' \\'])
    table.extend([
        r'\midrule Observations & 78,615 & 506,311 & 510,673 \\',
        r'Country clusters & 60 & 60 & 62 \\',
        r'Year, country and CPC effects & Yes & Yes & No \\',
        r'$R^2$ & 0.0547 & 0.2651 & 0.2113 \\\bottomrule',
        r'\end{tabular}',
        r'\par\smallskip\raggedright\footnotesize\emph{Notes:} '
        'New estimates from the recovered numeric input, not an exact reconstruction of the '
        'unavailable historical Table 2. The outcome is RCA above one in year $t+1$. '
        'The first column gives equal weight to country--CPC--year cell means; the second '
        'uses patent--CPC rows. Both absorb year, country and CPC effects and remove singleton '
        'observations. The third reproduces the recovered pooled implementation, which did '
        'not actually absorb fixed effects. Continuous regressors and the raw squared distance '
        'are standardized separately. For the cell column, means of the row-level distance '
        'and raw squared distance are aggregated first and then standardized; the latter '
        'is not the square of the cell-mean distance. Standard errors clustered by country '
        'appear in parentheses. FE inference uses a finite-sample correction and a country-cluster '
        '$t$ reference; the pooled replay retains its original normal reference. '
        '$R^2$ is within-model for FE and ordinary for pooled OLS. '
        '$^{***}p<0.01$, $^{**}p<0.05$, $^{*}p<0.10$. '
        'Opposite coefficient signs alone do not establish an interior inverted U. '
        'These re-estimates differ from the historical numerical claims retained in the prose '
        'and do not replace the plotted pooled predictions in Figures 5 and 6.',
        r'\end{table}',
    ])
    marker = body.index('The estimates support H1.')
    body = body[:marker] + '\n'.join(table) + '\n\n' + body[marker:]
    return body
