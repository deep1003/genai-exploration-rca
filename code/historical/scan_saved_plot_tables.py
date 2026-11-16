from pathlib import Path
import json,csv,hashlib,re
R=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((R/'00_admin/image_matches.csv').open()))
paths={r['source'].split('#')[0] for r in rows if '#cell=' in r['source'] and 'Patent_analysis' in r['source']}
seen=set();saved=[]
for path in sorted(paths):
    p=Path(path)
    if p.stat().st_flags&0x40000000:continue
    raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if h in seen:continue
    seen.add(h);nb=json.loads(raw)
    for i,c in enumerate(nb['cells']):
        code=''.join(c.get('source',[]))
        for j,o in enumerate(c.get('outputs',[])):
            data=o.get('data',{})
            if 'image/svg+xml' in data or 'application/pdf' in data:print('VECTOR',path,i,list(data))
            text=''.join(data.get('text/plain',[]))
            html=''.join(data.get('text/html',[]))
            if html and any(k in html for k in ['Core Size','ci_lower','global_avg','mean_dist','LLM']):
                saved.append({'notebook':path,'cell':i,'code':code,'html':html,'text':text})
                print('TABLE',h[:8],i,code[:70].replace('\n',' '),text[:90].replace('\n',' '))
    if '(14) (9)' in p.name and '/03_code/' in str(p):
        for i in list(range(125,140))+list(range(300,321)):
            c=nb['cells'][i];print('CELL',i,''.join(c.get('source',[]))[:100].replace('\n',' '),[(list(o.get('data',{})),len(''.join(o.get('text',[])))) for o in c.get('outputs',[])])
(R/'02_figures/03_regeneration_600dpi/saved_plot_tables.json').write_text(json.dumps(saved,ensure_ascii=False,indent=2))
