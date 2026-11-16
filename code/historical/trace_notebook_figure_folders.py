"""Trace saved-image destinations from existing notebook code and outputs."""
from pathlib import Path
import json,csv,re,hashlib
R=Path(__file__).resolve().parents[1]
matches=list(csv.DictReader((R/'00_admin/image_matches.csv').open()))
paths={r['source'].split('#')[0] for r in matches if '#cell=' in r['source'] and ('Patent_analysis' in r['source'] or 'GenAI.ipynb' in r['source'])}
records=[];seen=set();names=set()
for path in sorted(paths):
    p=Path(path)
    if p.stat().st_flags&0x40000000:continue
    raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if h in seen:continue
    seen.add(h)
    for i,c in enumerate(json.loads(raw).get('cells',[])):
        code=''.join(c.get('source',[]))
        if not re.search(r'savefig|FIG_DIR|save_path|fig_dir|figure_dir',code):continue
        lines=[line for line in code.splitlines() if re.search(r'savefig|FIG_DIR|save_path|fig_dir|figure_dir|base_dir|Downloads|out_dir|output_dir',line)]
        streams=''.join(''.join(o.get('text',[])) for o in c.get('outputs',[]))
        records.append({'notebook':path,'cell':i,'path_code':lines,'saved_output':streams[:5000]})
        for name in re.findall(r'[\w.-]+\.(?:png|pdf|svg|eps|tiff?|jpg)',code):names.add(name)
D=R/'02_figures/05_saved_folder_trace';D.mkdir(exist_ok=True)
(D/'notebook_save_destinations.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
assets=list(csv.DictReader((R/'00_admin/asset_inventory.csv').open()))
found=[a for a in assets if Path(a['path']).name in names or re.search(r'genai.*(?:distance|trajectory)|event_study_overlay|distance.*genai',Path(a['path']).name,re.I)]
with (D/'saved_filename_matches.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','cold_placeholder','suffix']);w.writeheader();w.writerows(found)
print('NOTEBOOKS',len(seen),'SAVE_CELLS',len(records),'MATCHED_FILES',len(found))
for rec in records:
    if '(14) (9)' in rec['notebook'] and '/03_code/' in rec['notebook']:
        print('CELL',rec['cell']);print('\n'.join(rec['path_code']));print('OUTPUT',rec['saved_output'][:1000])
print('NAMES',sorted(names))
for a in found[:25]:print('FOUND',a['path'],a['bytes'],a['cold_placeholder'])
