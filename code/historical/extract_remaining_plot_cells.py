from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
N=next((R/'02_figures/06_icloud_acquired').glob('*(14) (9).ipynb'))
nb=json.loads(N.read_text());D=R/'02_figures/12_complete_replot_600dpi/original_cells';D.mkdir(parents=True,exist_ok=True)
for i in [151,196,197,211,216,245,249,250,252,261,263,287,296,298,316,318]:
    c=''.join(nb['cells'][i]['source']);(D/f'cell_{i}.py').write_text(c)
    if i in [151,197,245,250,252]:print('\nCELL',i,'\n',c[:5500])
