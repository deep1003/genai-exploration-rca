from pathlib import Path
import ast,pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
p=R/'06_scripts/restyle_nature_figures_20261116.py'
t=ast.parse(p.read_text());t.body=t.body[:next(i for i,n in enumerate(t.body) if isinstance(n,ast.With))]
env={'__file__':str(p)};exec(compile(t,str(p),'exec'),env)
D=env['D'];rows=__import__('json').loads((D/'text_and_geometry_audit.json').read_text())
env['records']=[r for r in rows if r['panel'] not in ['figure7a','figure7b','figure9b']]
for name in ['figure7a','figure7b','figure9b']:
    with (D/f'{name}_before.pkl').open('rb') as f:fig=pickle.load(f)
    plt.figure(fig);env['save'](name)
