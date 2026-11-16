"""Replay historical plotting cells only when their coefficient fingerprint matches."""
from pathlib import Path
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'02_data/df_final.csv').exists())
p=S/'02_data/df_final.csv'
if p.stat().st_flags&0x40000000:raise RuntimeError('Original CSV not yet downloaded; do not substitute another cohort.')
header=pd.read_csv(p,nrows=0).columns
if 'cpc_cluster_dist_cos' not in header:
    (R/'00_admin/legacy_csv_schema_mismatch.json').write_text(json.dumps({'path':str(p),'missing':'cpc_cluster_dist_cos','present':'cpc_cluster_dist','action':'do not reinterpret a differently named distance; inspect archived later USB export'},indent=2))
    p=Path('/Volumes/Untitled/df_final.csv')
    assert 'cpc_cluster_dist_cos' in pd.read_csv(p,nrows=0).columns
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text());D=R/'02_figures/09_original_regression_replay';D.mkdir(exist_ok=True)
cols=['rca_y1','rca_y0','inventor_cet','cpc_cluster_dist_cos','num_inventors','num_applicants','wips_family_pub_count','cited_by_count','citations_count','num_claims','year','country_code','cpc_code']
print('READING_ORIGINAL_NUMERIC_COLUMNS',flush=True)
cache=D/'original_numeric_input.parquet'
if cache.exists():df=pd.read_parquet(cache)
else:
    df=pd.read_csv(p,usecols=cols,low_memory=False)
    df.to_parquet(cache,index=False)
print('ORIGINAL_ROWS',len(df),flush=True)
env={'df_final':df,'np':np}
code=''.join(nb['cells'][287]['source']).replace('plt.show()','')
exec(compile(code,str(N)+'#287','exec'),env)
res=env['res'];expected={'const':.1859,'rca_y0':.5460,'cpc_cluster_dist_cos_z':.1267,'I_cpc2_z':-.1191}
matched=int(res.nobs)==509665 and all(round(float(res.params[k]),4)==v for k,v in expected.items())
rec={'rows':len(df),'nobs':int(res.nobs),'coefficients':res.params.to_dict(),'fingerprint_matches':matched,'original_csv':str(p),'overleaf_replaced':False}
(D/'fingerprint.json').write_text(json.dumps(rec,indent=2))
plt.gcf().savefig(D/'figure5_candidate_600dpi.png',dpi=600)
plt.gcf().savefig(D/'figure5_candidate_vector.pdf')
plt.gcf().savefig(D/'figure5_preview.png',dpi=100)
plt.close('all')
if not matched:raise RuntimeError('Historical coefficient fingerprint differs. Candidate must not replace original.')
for i,name in [(294,'figure6a'),(296,'figure6b')]:
    code=''.join(nb['cells'][i]['source']).replace('plt.show()','')
    (D/f'{name}_original_code.py').write_text(code)
    exec(compile(code,str(N)+f'#{i}','exec'),env)
    plt.gcf().savefig(D/f'{name}_600dpi.png',dpi=600)
    plt.gcf().savefig(D/f'{name}_vector.pdf')
    plt.gcf().savefig(D/f'{name}_preview.png',dpi=100)
    plt.close('all')
print('HISTORICAL_FINGERPRINT_MATCHED_AND_PLOTS_RENDERED',flush=True)
