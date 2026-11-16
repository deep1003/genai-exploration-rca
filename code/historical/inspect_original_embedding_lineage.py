from pathlib import Path
import json,numpy as np,hashlib
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'02_data/usb_import_20261108/X_all_embeddings.npy').exists())
A=S/'02_data/usb_import_20261108/X_all_embeddings.npy'
B=S/'05_revision/september_exact_code_replay_20261110/september_full_cache/reconstructed_september_X_all.npy'
a=np.load(A,mmap_mode='r');b=np.load(B,mmap_mode='r')
same=a.shape==b.shape;diff=0.
if same:
    for start in range(0,len(a),10000):diff=max(diff,float(np.max(np.abs(a[start:start+10000]-b[start:start+10000]))))
rec={'original':str(A),'reconstruction':str(B),'shape':list(a.shape),'max_absolute_difference':diff,'exact_array_equal':same and diff==0}
(R/'00_admin/embedding_lineage_newly_downloaded.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
nb=json.loads((S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').read_text())
D=R/'03_evidence/600dpi_dependencies';D.mkdir(exist_ok=True)
for i,c in enumerate(nb['cells']):
    code=''.join(c.get('source',[]))
    if ('cluster_id_k' in code or 'category_emb' in code or 'category_names' in code) and i<220:
        (D/f'cell_{i}.py').write_text(code)
        print('DEPENDENCY_CELL',i,code[:110].replace('\n',' '))
