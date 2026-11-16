from pathlib import Path
import json, contextlib, io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from threadpoolctl import threadpool_limits
R=Path(__file__).resolve().parents[1]
D=R/'02_figures/12_complete_replot_600dpi'
N=next(R.parent.glob('*/03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'))
nb=json.loads(N.read_text())
env={'df_final':pd.read_parquet(R/'02_figures/09_original_regression_replay/original_numeric_input.parquet'),'np':np,'pd':pd}
with threadpool_limits(limits=3):
    for i in [287,294]:
        code=''.join(nb['cells'][i]['source']).replace('plt.show()','')
        (D/'original_cells'/f'cell_{i}.py').write_text(code)
        out=io.StringIO()
        with contextlib.redirect_stdout(out):exec(compile(code,str(N)+f'#{i}','exec'),env)
        (D/f'cell_{i}_output.txt').write_text(out.getvalue())
        if i==287:plt.close('all')
    fig=plt.gcf()
    for ext,dpi in [('pdf',600),('png',600)]:
        fig.savefig(D/('figure6b_fresh.pdf' if ext=='pdf' else 'figure6b_fresh_600dpi.png'),dpi=dpi)
    fig.savefig(D/'figure6b_fresh_preview.png',dpi=100)
    plt.close('all')
p=D/'fresh_replot_provenance.json';rows=json.loads(p.read_text())
for r in rows:
    if r['figure']==6:r['cells']=[298,294]
p.write_text(json.dumps(rows,indent=2))
print('FAMILY_PANEL_CORRECTED')
