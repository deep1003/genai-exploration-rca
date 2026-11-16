"""User-authorised fresh replots; do not deploy mismatched historical results."""
from pathlib import Path
import json,io,contextlib,ast,subprocess
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from threadpoolctl import threadpool_limits
from matplotlib_legacy_compat import install_legacy_colormap_api
R=Path(__file__).resolve().parents[1]
D=R/'02_figures/12_complete_replot_600dpi';D.mkdir(exist_ok=True)
S=next(p for p in R.parent.iterdir() if (p/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
install_legacy_colormap_api()
records=[]
def execute(cell,env):
    code=''.join(nb['cells'][cell]['source']).replace('%matplotlib inline','').replace('plt.show()','')
    (D/'original_cells'/f'cell_{cell}.py').write_text(code)
    log=io.StringIO()
    with contextlib.redirect_stdout(log):exec(compile(code,str(N)+f'#{cell}','exec'),env)
    (D/f'cell_{cell}_output.txt').write_text(log.getvalue())
    print('CELL_COMPLETED',cell,flush=True)
def save(name):
    fig=plt.gcf()
    fig.savefig(D/f'{name}.pdf')
    fig.savefig(D/f'{name}_600dpi.png',dpi=600)
    fig.savefig(D/f'{name}_preview.png',dpi=100)
    plt.close('all')

with threadpool_limits(limits=4):
    df=pd.read_parquet(R/'02_figures/09_original_regression_replay/original_numeric_input.parquet')
    env={'df_final':df,'np':np,'pd':pd}
    execute(287,env);save('figure5_fresh')
    records.append({'figure':5,'input':'original_numeric_input.parquet from archived December USB export','nobs':int(env['res'].nobs),'coefficients':env['res'].params.to_dict(),'historical_equivalence':False})
    execute(298,env);save('figure6a_fresh')
    execute(294,env);save('figure6b_fresh')
    records.append({'figure':6,'cells':[298,294],'historical_equivalence':False,'reason':'same historical code, available December input state'})
    cache=S/'05_revision/september_exact_code_replay_20261110/september_full_cache'
    cols=['appl_id','year','country_code','cpc_main_norm','genai_pred','genai_subtype_pred','genai_confidence_raw']
    pred=pd.read_parquet(cache/'df_pred_regenerated.parquet',columns=cols)
    dp=cache/'recomputed_september_cpc_distances.parquet'
    subprocess.run(['brctl','download',str(dp)],capture_output=True)
    distances=pd.read_parquet(dp)
    pred['cpc_code']=pred.cpc_main_norm
    pred=pred.merge(distances[['year','country_code','cpc_code','cpc_cluster_dist_cos']],on=['year','country_code','cpc_code'],how='left',validate='many_to_one').reset_index(drop=True)
    env7={'df_pred':pred,'np':np,'pd':pd,'thr_hi':.6,'thr_lo':.4}
    execute(316,env7);save('figure7a_fresh')
    execute(318,env7);save('figure7b_fresh')
    records.append({'figure':7,'cells':[316,318],'classification_source':str(cache/'df_pred_regenerated.parquet'),'distance_source':str(dp),'historical_equivalence':False})
    npth=S/'05_revision/full_restored_regressions_20261109_run06/rebuilt_inventor_network.parquet'
    subprocess.run(['brctl','download',str(npth)],capture_output=True)
    raw_network=pd.read_parquet(npth,columns=['appl_id','inventor','inventor_nat']).drop_duplicates()
    current_metadata=pred[['appl_id','year','country_code','genai_subtype_pred']]
    network=raw_network.merge(current_metadata,on='appl_id',how='inner',validate='many_to_one')
    eu=None
    for c in nb['cells']:
        try:tree=ast.parse(''.join(c.get('source',[])))
        except SyntaxError:continue
        for node in tree.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EU_CODES' for t in node.targets):
                try:eu=ast.literal_eval(node.value)
                except (ValueError,TypeError):pass
        if eu is not None:break
    if eu is None:raise RuntimeError('EU_CODES must be recovered from the original notebook before network replay.')
    env8={'df_expl':network,'df_pred':pred,'np':np,'pd':pd,'nx':nx,'EU_CODES':eu}
    for cell in [245,250,252,261]:execute(cell,env8)
    env8['df_summary'].to_csv(D/'figure8_fresh_core_counts.csv')
    execute(263,env8);save('figure8_fresh')
    records.append({'figure':8,'cells':[245,250,252,261,263],'raw_network_source':str(npth),'inventor_rows':len(network),'matched_patents':int(network.appl_id.nunique()),'classification_source':str(cache/'df_pred_regenerated.parquet'),'historical_equivalence':False})
    (D/'fresh_replot_provenance.json').write_text(json.dumps(records,indent=2))
print('FRESH_REMAINING_PANELS_COMPLETE',flush=True)
