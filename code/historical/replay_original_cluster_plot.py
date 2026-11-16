from pathlib import Path
import numpy as np,pandas as pd,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from threadpoolctl import threadpool_limits
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'02_data/usb_import_20261108/X_all_embeddings.npy').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
P=S/'05_revision/september_exact_code_replay_20261110/september_full_cache/df_pred_regenerated.parquet'
df=pd.read_parquet(P,columns=['year','country_code','embedding_row'])
assert np.array_equal(df.embedding_row.to_numpy(),np.arange(len(df)))
X=np.load(S/'02_data/usb_import_20261108/X_all_embeddings.npy')
D=R/'02_figures/08_original_array_replay';D.mkdir(exist_ok=True)
env={'X_all':X,'df_pred':df}
with threadpool_limits(limits=4):
    print('RUNNING_ORIGINAL_CELL_154',flush=True)
    exec(compile(''.join(nb['cells'][154]['source']),str(N)+'#154','exec'),env)
df[['embedding_row','year','country_code','cluster_id_k','dist_cluster_cos']].to_parquet(D/'original_array_distances.parquet',index=False)
code=''.join(nb['cells'][172]['source']).replace('plt.show()','')
exec(compile(code,str(N)+'#172','exec'),env)
fig=plt.gcf();fig.savefig(D/'figure4_600dpi.png',dpi=600);fig.savefig(D/'figure4_vector.pdf');fig.savefig(D/'figure4_preview.png',dpi=100);plt.close(fig)
env['world_year'].to_csv(D/'figure4_world_data.csv',index=False)
env['country_year'].to_csv(D/'figure4_country_data.csv')
(D/'status.json').write_text(json.dumps({'original_array_used':True,'original_cells':[154,172],'status':'candidate_pending_original_visual_and_numerical_comparison','overleaf_replaced':False},indent=2))
print('CLUSTER_PLOT_REPLAY_DONE',flush=True)
