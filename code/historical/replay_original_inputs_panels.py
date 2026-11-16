from pathlib import Path
import json,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from pypdf import PdfReader,PdfWriter,PageObject,Transformation
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
P=S/'05_revision/september_exact_code_replay_20261110/september_full_cache/df_pred_regenerated.parquet'
df=pd.read_parquet(P,columns=['year','country_code','appl_id','genai_subtype_pred','num_inventors','wips_family_pub_count'])
D=R/'02_figures/11_original_inputs_replay';D.mkdir(exist_ok=True)
env={'df_pred':df}
panels=[];pdfs=[]
for i,name in [(134,'figure3a'),(135,'figure3b')]:
    code=''.join(nb['cells'][i]['source']).replace('plt.show()','')
    (D/f'{name}_original_code.py').write_text(code)
    exec(compile(code,str(N)+f'#{i}','exec'),env)
    fig=plt.gcf()
    for ext in ['png','pdf']:fig.savefig(D/f'{name}_600dpi.{ext}',dpi=600,bbox_inches='tight')
    fig.savefig(D/f'{name}_preview.png',dpi=100,bbox_inches='tight')
    plt.close(fig)
    panels.append(Image.open(D/f'{name}_600dpi.png').convert('RGB'))
    pdfs.append(PdfReader(D/f'{name}_600dpi.pdf').pages[0])
canvas=Image.new('RGB',(sum(im.width for im in panels),max(im.height for im in panels)),'white')
x=0
for im in panels:canvas.paste(im,(x,0));x+=im.width
canvas.save(D/'figure3_candidate_600dpi.png',dpi=(600,600))
canvas.thumbnail((1600,600));canvas.save(D/'figure3_preview.png')
page=PageObject.create_blank_page(width=sum(float(p.mediabox.width) for p in pdfs),height=max(float(p.mediabox.height) for p in pdfs))
x=0
for p in pdfs:page.merge_transformed_page(p,Transformation().translate(tx=x));x+=float(p.mediabox.width)
w=PdfWriter();w.add_page(page)
with (D/'figure3_candidate_vector.pdf').open('wb') as f:w.write(f)
(D/'status.json').write_text(json.dumps({'cells':[134,135],'status':'candidate pending original validation','source_prediction_cache':str(P),'overleaf_replaced':False},indent=2))
print('ORIGINAL_INPUT_PANELS_RENDERED',flush=True)
