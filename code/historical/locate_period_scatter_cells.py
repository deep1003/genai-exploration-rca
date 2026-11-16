from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb').exists())
N=S/'03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
nb=json.loads(N.read_text())
for i,c in enumerate(nb['cells']):
    code=''.join(c.get('source',[]))
    if ('Y_patent' in code or 'Y_cat' in code) and re.search(r'period|2000|five.year|2024',code,re.I):
        (R/'03_evidence/600dpi_dependencies'/f'period_cell_{i}.py').write_text(code)
        print(i,code[:230].replace('\n',' '))
