from pathlib import Path
import csv,json,collections,hashlib,re
R=Path(__file__).resolve().parents[1]
matches=list(csv.DictReader((R/'00_admin/image_matches.csv').open()))
for fig in sorted(set(r['figure'] for r in matches)):
    seen=set();rows=[]
    for r in sorted([r for r in matches if r['figure']==fig],key=lambda r:int(r['phash_distance'])):
        if r['sha256'] in seen:continue
        seen.add(r['sha256']);rows.append(r)
    print('\nFIGURE',fig)
    for r in rows[:6]:print(r['width'],r['height'],r['phash_distance'],r['source'])
notebook=next(r['source'].split('#')[0] for r in matches if '2d23' in hashlib.sha256(r['source'].split('#')[0].encode()).hexdigest()[:10])
nb=json.loads(Path(notebook).read_text())
print('NOTEBOOK',notebook)
dest=R/'03_evidence/600dpi';dest.mkdir(exist_ok=True)
for i,c in enumerate(nb['cells']):
    code=''.join(c.get('source',[]))
    if re.search('df_summary|savefig|np.save|to_csv|to_pickle|Y_patent|df_pred =|df_pred=',code):
        print('CELL',i,code[:130].replace('\n',' '))
    if i in list(range(255,265))+list(range(275,297)):
        outputs=[]
        for o in c.get('outputs',[]):
            for k,v in o.get('data',{}).items():
                if k in ['text/plain','text/html']:outputs.append({k:''.join(v)})
            if 'text' in o:outputs.append({'stream':''.join(o['text'])})
        (dest/f'cell_{i}.json').write_text(json.dumps({'code':code,'outputs':outputs},ensure_ascii=False,indent=2))
print('EXTRACTED',dest)
