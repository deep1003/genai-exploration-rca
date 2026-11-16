"""Prepare an allowlisted public release; exclude licensed row-level inputs."""
from pathlib import Path
import csv,hashlib,json,pickle,re,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1]
P=R/'09_public_release/genai-exploration-rca'
for d in ['data/tables','data/figure_series','code/historical','code/original_cells','figures','provenance']:(P/d).mkdir(parents=True,exist_ok=True)
T=R/'07_reports/research_policy_20261116/table_recovery'
for f in T.glob('*.csv'):shutil.copy2(f,P/'data/tables'/f.name)
meta=json.loads((T/'table2_model_metadata.json').read_text());meta['source']=Path(meta['source']).name
(P/'provenance/table2_model_metadata.json').write_text(json.dumps(meta,indent=2))
prov=json.loads((T/'historical_count_provenance.json').read_text());prov['notebook']=Path(prov['notebook']).name
(P/'provenance/historical_count_provenance.json').write_text(json.dumps(prov,indent=2))
for f in (R/'06_scripts').glob('*.py'):
    raw=f.read_text()
    assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})',raw),f
    shutil.copy2(f,P/'code/historical'/f.name)
for f in (R/'02_figures/12_complete_replot_600dpi/original_cells').glob('*.py'):shutil.copy2(f,P/'code/original_cells'/f.name)
for n in ['figure2','figure3a','figure3b','figure4','figure5','figure6a','figure6b','figure7a','figure7b','figure8']:
    with (R/f'02_figures/13_nature_labels_20261116/{n}_styled.pkl').open('rb') as f:fig=pickle.load(f)
    records=[]
    for a,ax in enumerate(fig.axes):
        for j,line in enumerate(ax.lines):
            x,y=np.asarray(line.get_xdata()),np.asarray(line.get_ydata())
            if len(x)!=len(y):continue
            records.extend({'axis':a,'series':j,'label':line.get_label(),'x':xx,'y':yy} for xx,yy in zip(x,y))
    if records:
        with (P/f'data/figure_series/{n}_lines.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['axis','series','label','x','y']);w.writeheader();w.writerows(records)
    plt.close(fig)
F=R/'research_policy_reconciled_20261116/figures'
for n in range(1,10):shutil.copy2(F/f'Figure_{n:02d}.pdf',P/f'figures/Figure_{n:02d}.pdf')
source=R/'02_figures/09_original_regression_replay/original_numeric_input.parquet'
withheld={'row_level_input':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'rows':513533,'public':False,'reason':'Redistribution rights for patent-provider inputs have not been confirmed.',
    'other_exclusions':['original Word manuscript','full notebook outputs','patent-level embedding coordinates','personal addresses and inventor records','authentication data','full private workspace']}
(P/'provenance/withheld_inputs.json').write_text(json.dumps(withheld,indent=2))
files=[]
for f in sorted(P.rglob('*')):
    if not f.is_file() or '.git' in f.parts or f.name=='manifest.json':continue
    files.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'provenance/manifest.json').write_text(json.dumps(files,indent=2))
print(json.dumps({'files':len(files),'bytes':sum(x['bytes'] for x in files),'row_level_inputs_public':False},indent=2))
