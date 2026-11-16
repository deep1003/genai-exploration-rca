from pathlib import Path
import json,ast,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib_legacy_compat import install_legacy_colormap_api
R=Path(__file__).resolve().parents[1]
D=R/'02_figures/10_original_tsne_replay'
S=next(p for p in R.parent.iterdir() if (p/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
df=pd.read_parquet(S/'05_revision/september_exact_code_replay_20261110/september_full_cache/df_pred_regenerated.parquet',columns=['year','country_code','appl_id','embedding_row'])
lab=pd.read_parquet(R/'02_figures/08_original_array_replay/original_array_distances.parquet')
assert np.array_equal(df.embedding_row,lab.embedding_row)
df['cluster_id_k']=lab.cluster_id_k.to_numpy()
z=np.load(D/'original_code_coordinates.npz')
tree=ast.parse(''.join(nb['cells'][142]['source']))
names=next(list(ast.literal_eval(n.value)) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='category_desc' for t in n.targets))
env={'df_pred':df,'np':np,'Y_patent':z['Y_patent'],'Y_cat':z['Y_cat'],'category_names':names,
     'X_all':np.load(S/'02_data/usb_import_20261108/X_all_embeddings.npy',mmap_mode='r')}
# Matplotlib removed this API; the registered tab10 colour values are unchanged.
install_legacy_colormap_api()
for cell,name in [(235,'figure1'),(233,'figure9a')]:
    code=''.join(nb['cells'][cell]['source']).replace('plt.show()','')
    if cell==233:
        tree=ast.parse(code)
        start=next(n.lineno for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cn_mask' for t in n.targets))
        tree.body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or n.lineno>=start]
        exec(compile(tree,str(N)+f'#{cell}-plotting-only','exec'),env)
    else:exec(compile(code,str(N)+f'#{cell}','exec'),env)
    plt.gcf().savefig(D/f'{name}_600dpi.png',dpi=600)
    plt.gcf().savefig(D/f'{name}_vector.pdf')
    plt.gcf().savefig(D/f'{name}_preview.png',dpi=100)
    plt.close('all')
(D/'status.json').write_text(json.dumps({'status':'candidates pending comparison; not deployed','source_cells':[142,219,235,233],'compatibility_only':'cm.get_cmap redirected to colormaps.get_cmap','tsne_rerun':False},indent=2))
print('CHECKPOINT_PLOTS_RENDERED',flush=True)
