from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1];D=R/'07_reports/research_policy_20261116/table_recovery';D.mkdir(exist_ok=True)
S=next(R.parent.glob('*/03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb')).parents[1]
files=list((R/'02_figures/06_icloud_acquired').glob('*.ipynb'))+list((S/'03_code').rglob('*.ipynb'))
seen=set();hits=[];cold=[]
for p in files:
    if not any(w in p.name for w in ['Patent','Cumulative','20251224']):continue
    if p.stat().st_flags&0x40000000:cold.append(str(p));continue
    raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if sha in seen:continue
    seen.add(sha);nb=json.loads(raw)
    for i,c in enumerate(nb['cells']):
        if c['cell_type']!='code':continue
        texts=[]
        for o in c.get('outputs',[]):
            for v in [o.get('text',[]),o.get('data',{}).get('text/plain',[]),o.get('data',{}).get('text/html',[])]:
                texts.append(''.join(v) if isinstance(v,list) else v)
        txt='\n'.join(texts)
        needles=[w for w in ['24357','24,357','509665','509,665','0.1267','0.5460'] if w in txt]
        if needles:
            dest=D/f'{sha[:10]}_cell_{i}.json';dest.write_text(json.dumps({'source':str(p),'notebook_sha256':sha,'cell':i,'source_code':c['source'],'outputs':c.get('outputs',[])},indent=2))
            record={'source':str(p),'sha256':sha,'cell':i,'matches':needles,'saved':str(dest)};hits.append(record)
            print(p.name,i,','.join(needles),flush=True)
(D/'search_hits.json').write_text(json.dumps({'unique_notebooks_read':len(seen),'hits':hits,'cold_notebooks_not_yet_read':cold},indent=2))
print('SEARCH_DONE',len(seen),'NOTEBOOKS',len(hits),'HITS',len(cold),'COLD',flush=True)
