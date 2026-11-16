"""Fresh Figure 9(b) from the notebook's original no-anchor t-SNE pipeline."""
from pathlib import Path
import os
os.environ['OMP_NUM_THREADS']='6'
import json,ast,io,contextlib,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from threadpoolctl import threadpool_limits
R=Path(__file__).resolve().parents[1];D=R/'02_figures/12_complete_replot_600dpi'
S=next(p for p in R.parent.iterdir() if (p/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
pred=pd.read_parquet(S/'05_revision/september_exact_code_replay_20261110/september_full_cache/df_pred_regenerated.parquet',columns=['year','country_code','appl_id','embedding_row','genai_pred','genai_subtype_pred'])
assert np.array_equal(pred.embedding_row,np.arange(len(pred)))
env={'df_pred':pred,'X_all':np.load(S/'02_data/usb_import_20261108/X_all_embeddings.npy'),'np':np,'pd':pd}
checkpoint=D/'period_coordinates_without_anchors.npy'
if checkpoint.exists():
    env['X_tsne']=np.load(checkpoint)
    env['vis_df']=pd.DataFrame({'tSNE1':env['X_tsne'][:,0],'tSNE2':env['X_tsne'][:,1],'GenAI':pred.genai_pred.eq('GenAI').map({True:'GenAI',False:'Others'}).to_numpy()})
else:
    print('START_ORIGINAL_NO_ANCHOR_TSNE_1000_ITERATIONS',flush=True)
    code=''.join(nb['cells'][151]['source']).replace('plt.show()','')
    with threadpool_limits(limits=6):exec(compile(code,str(N)+'#151','exec'),env)
    np.save(checkpoint,env['X_tsne']);plt.close('all')
code=''.join(nb['cells'][189]['source'])
tree=ast.parse(code)
# Reuse only preparation/palette statements; omit the unrelated full scatter plot.
cut=next(n.lineno for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='subplots')
selected=[]
for node in tree.body:
    if isinstance(node,(ast.Import,ast.ImportFrom)):selected.append(node)
    elif node.lineno<cut and not isinstance(node,ast.If):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='K' for t in node.targets):continue
        selected.append(node)
env['df_pred']['cluster_id_k']=pd.read_parquet(R/'02_figures/08_original_array_replay/original_array_distances.parquet',columns=['cluster_id_k']).cluster_id_k.to_numpy()
tree.body=selected
exec(compile(tree,str(N)+'#189-preparation-only','exec'),env)
assert 'plot_df' in env and 'palette_map' in env
env['df_pred']=pred.loc[env['plot_df'].index].copy()
code=''.join(nb['cells'][197]['source']).replace('plt.show()','')
exec(compile(code,str(N)+'#197','exec'),env)
fig=plt.gcf();fig.savefig(D/'figure9b_fresh.pdf');fig.savefig(D/'figure9b_fresh_600dpi.png',dpi=600);fig.savefig(D/'figure9b_fresh_preview.png',dpi=100);plt.close('all')
(D/'figure9b_provenance.json').write_text(json.dumps({'status':'fresh code replot; not historical equivalence','cells':[151,189,197],'rows':len(pred),'plotted_rows':len(env['plot_df']),'iterations':1000,'random_state':42,'anchors_in_projection':False,'original_code_parameters_preserved':True},indent=2))
print('FIGURE9B_FRESH_COMPLETE',flush=True)
