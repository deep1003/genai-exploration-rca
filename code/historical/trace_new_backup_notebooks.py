from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];D=R/'02_figures/06_icloud_acquired'
rows=[]
for p in D.glob('*.ipynb'):
    nb=json.loads(p.read_text())
    for i,c in enumerate(nb.get('cells',[])):
        code=''.join(c.get('source',[]))
        if not re.search(r'savefig|np.save|to_pickle|pickle.dump|to_parquet|FIG_DIR',code):continue
        lines=[s for s in code.splitlines() if re.search(r'savefig|np.save|to_pickle|pickle.dump|to_parquet|FIG_DIR|save_dir|save_path|base_dir|out_dir|output_dir',s)]
        outputs=''.join(''.join(o.get('text',[])) for o in c.get('outputs',[]))
        rows.append({'notebook':str(p),'cell':i,'path_code':lines,'outputs':outputs[:5000]})
        if p.stat().st_size<1000000:
            print(p.name,i,'\n'.join(lines)[:2500],outputs[:300],flush=True)
(R/'02_figures/05_saved_folder_trace/new_backup_save_paths.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('SAVE_CELLS',len(rows))
