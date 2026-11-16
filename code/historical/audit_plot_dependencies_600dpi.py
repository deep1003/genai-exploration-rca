from pathlib import Path
import csv,json,hashlib,re,io
import pandas as pd

R=Path(__file__).resolve().parents[1]
D=R/'02_figures/03_regeneration_600dpi';D.mkdir(exist_ok=True)
matches=list(csv.DictReader((R/'00_admin/image_matches.csv').open()))
paths=sorted({r['source'].split('#')[0] for r in matches if '#cell=' in r['source']})
seen=set();summaries=[];codes=[]
for path in paths:
    p=Path(path)
    if p.stat().st_flags & 0x40000000:continue
    raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if h in seen:continue
    seen.add(h)
    nb=json.loads(raw)
    for i,c in enumerate(nb.get('cells',[])):
        code=''.join(c.get('source',[]))
        if re.search('np.save|pickle.dump|joblib.dump|to_pickle|to_parquet|read_parquet|read_pickle|np.load|read_csv|read_feather',code):
            codes.append({'notebook':path,'cell':i,'code':code})
        for j,o in enumerate(c.get('outputs',[])):
            data=o.get('data',{})
            html=''.join(data.get('text/html',[]))
            if 'Core Size' in html and 'Core Nodes' in html:
                try:
                    df=pd.read_html(io.StringIO(html),index_col=0)[0]
                    if isinstance(df.columns,pd.MultiIndex):df.columns=df.columns.get_level_values(0)
                    f=D/f'core_summary_{h[:10]}_{i}_{j}.csv';df.to_csv(f)
                    summaries.append({'notebook':path,'cell':i,'file':str(f),'US':df['US Core Nodes'].tolist(),'Core':df['Core Size'].tolist(),'display_shares':(df['US Core Nodes']/df['Core Size']*100).round(1).tolist()})
                except Exception as e:print(type(e).__name__,str(e))
(D/'data_load_and_save_code.json').write_text(json.dumps(codes,ensure_ascii=False,indent=2))
(D/'core_summary_candidates.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2))
print('UNIQUE_NOTEBOOKS',len(seen),'SUMMARY_TABLES',len(summaries))
for s in summaries:print(Path(s['file']).name,s['display_shares'])
