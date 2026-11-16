from pathlib import Path
import ast,json,pickle,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
S=R/'02_figures/13_nature_labels_20261116';D=R/'02_figures/14_research_policy_20261116';D.mkdir(exist_ok=True)
p=R/'06_scripts/restyle_nature_figures_20261116.py';t=ast.parse(p.read_text())
t.body=t.body[:next(i for i,n in enumerate(t.body) if isinstance(n,ast.With))]
env={'__file__':str(p)};exec(compile(t,str(p),'exec'),env)
records=[]
for file in sorted(S.glob('*_styled.pkl')):
    name=file.name.removesuffix('_styled.pkl')
    with file.open('rb') as f:fig=pickle.load(f)
    before=env['geometry'](fig);oldtitles=[]
    for ax in fig.axes:
        if name!='figure9b':
            oldtitles.append(ax.get_title());ax.set_title('')
    after=env['geometry'](fig);assert before==after
    box='tight' if name in ['figure3a','figure3b','figure9b'] else None
    fig.savefig(D/f'{name}.pdf',bbox_inches=box)
    fig.savefig(D/f'{name}_600dpi.png',dpi=600,bbox_inches=box)
    plt.close(fig)
    records.append({'panel':name,'data_and_colors_unchanged':before==after,'geometry_sha256':after,'removed_titles':oldtitles,'reason':'Elsevier captions carry figure titles; five-year panel labels retained'})
(D/'artwork_audit.json').write_text(json.dumps(records,indent=2))
print('RP_PANELS_READY',len(records),flush=True)
