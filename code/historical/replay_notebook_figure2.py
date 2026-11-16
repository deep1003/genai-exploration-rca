"""Replay archived plotting code against resident candidate prediction caches."""
from pathlib import Path
import json,hashlib,io,csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from scipy.fft import dctn
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text());code=''.join(nb['cells'][133]['source'])
D=R/'02_figures/04_notebook_replay_600dpi';D.mkdir(exist_ok=True)
(D/'figure2_original_cell133.py').write_text(code)
def phash(im):
    a=np.asarray(im.convert('L').resize((32,32)),dtype=float)
    f=dctn(a,norm='ortho')[:8,:8];return f>np.median(f)
target=phash(Image.open(R/'02_figures/00_embedded_originals/image2.png'))
records=[];seen=set()
for p in S.rglob('df_pred_regenerated.parquet'):
    st=p.stat()
    if st.st_flags&0x40000000:continue
    df=pd.read_parquet(p,columns=['year','country_code','appl_id','genai_subtype_pred'])
    key=hashlib.sha256(pd.util.hash_pandas_object(df,index=True).values.tobytes()).hexdigest()
    if key in seen:continue
    seen.add(key)
    env={'df_pred':df}
    plt.close('all')
    exec(compile(code.replace('plt.show()',''),str(N)+'#cell133','exec'),env)
    fig=plt.gcf();preview=D/f'figure2_{key[:10]}_preview.png';fig.savefig(preview,dpi=100)
    distance=int(np.count_nonzero(phash(Image.open(preview))!=target))
    env['llm_counts_wide'].to_csv(D/f'figure2_{key[:10]}_counts.csv')
    fig.savefig(D/f'figure2_{key[:10]}_600dpi.png',dpi=600)
    fig.savefig(D/f'figure2_{key[:10]}_vector.pdf')
    plt.close(fig)
    record={'source':str(p),'cache_digest':key,'phash_distance':distance,'status':'candidate, requires original curve verification','CN_2021':int(env['cn_series'].get(2021,0)),'US_2021':int(env['us_series'].get(2021,0))}
    records.append(record);print(json.dumps(record),flush=True)
(D/'figure2_replay_candidates.json').write_text(json.dumps(records,indent=2))
