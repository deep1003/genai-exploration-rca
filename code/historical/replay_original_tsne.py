"""Replay the original t-SNE pipeline once; never claim a match before QA."""
from pathlib import Path
import os
R=Path(__file__).resolve().parents[1]
D=R/'02_figures/10_original_tsne_replay';D.mkdir(exist_ok=True)
os.environ['HF_HOME']=str(D/'model_cache')
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['OMP_NUM_THREADS']='4'
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib_legacy_compat import install_legacy_colormap_api
from sentence_transformers import SentenceTransformer
from threadpoolctl import threadpool_limits
install_legacy_colormap_api()
S=next(p for p in R.parent.iterdir() if (p/'02_data/usb_import_20261108/X_all_embeddings.npy').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
metadata=S/'05_revision/september_exact_code_replay_20261110/september_full_cache/df_pred_regenerated.parquet'
df=pd.read_parquet(metadata,columns=['year','country_code','appl_id','embedding_row'])
labels=pd.read_parquet(R/'02_figures/08_original_array_replay/original_array_distances.parquet')
assert np.array_equal(df.embedding_row,labels.embedding_row)
df['cluster_id_k']=labels.cluster_id_k.to_numpy()
env={'df_pred':df,'X_all':np.load(S/'02_data/usb_import_20261108/X_all_embeddings.npy')}
print('LOADING_ORIGINAL_ANCHOR_MODEL',flush=True)
env['sbert']=SentenceTransformer('AI-Growth-Lab/PatentSBERTa',cache_folder=str(D/'model_cache'),device='cpu')
with threadpool_limits(limits=4):
    exec(compile(''.join(nb['cells'][142]['source']),str(N)+'#142','exec'),env)
    np.save(D/'category_embeddings_original_descriptions.npy',env['category_emb'])
    code=''.join(nb['cells'][219]['source']).replace('plt.show()','')
    print('REPLAYING_ORIGINAL_PCA_TSNE_CELL_219',flush=True)
    exec(compile(code,str(N)+'#219','exec'),env)
np.savez(D/'original_code_coordinates.npz',Y_patent=env['Y_patent'],Y_cat=env['Y_cat'])
plt.close('all')
for cell,figure in [(235,'figure1'),(233,'figure9a')]:
    code=''.join(nb['cells'][cell]['source']).replace('plt.show()','')
    (D/f'{figure}_source.py').write_text(code)
    exec(compile(code,str(N)+f'#{cell}','exec'),env)
    plt.gcf().savefig(D/f'{figure}_600dpi.png',dpi=600)
    plt.gcf().savefig(D/f'{figure}_vector.pdf')
    plt.gcf().savefig(D/f'{figure}_preview.png',dpi=100)
    plt.close('all')
(D/'status.json').write_text(json.dumps({'status':'pending comparison with original; not deployed','source_array':'original downloaded USB embedding backup','cells':[142,219,235,233]},indent=2))
print('ORIGINAL_TSNE_REPLAY_COMPLETE',flush=True)
