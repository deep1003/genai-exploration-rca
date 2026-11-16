"""Hydrate real iCloud backup files before inspecting their contents."""
from pathlib import Path
import subprocess,sys,shutil,hashlib,json,time
R=Path(__file__).resolve().parents[1]
if len(sys.argv)>1 and sys.argv[1]=='--copy':
    shutil.copy2(sys.argv[2],sys.argv[3]);sys.exit(0)
cloud=R.parents[0]
backup=next(p for p in (cloud.parent/'data4').iterdir() if p.name.startswith('06.26 AI '))
source_project=next(p for p in cloud.iterdir() if (p/'02_data/usb_import_20261108/event_study_overlay_GenAI_vs_NonGenAI.png').exists())
targets=sorted((backup/'figures').glob('*'))+[source_project/'02_data/usb_import_20261108/event_study_overlay_GenAI_vs_NonGenAI.png']
targets += [p for p in backup.iterdir() if p.suffix.lower() in ['.zip','.ipynb'] and p.stat().st_size<50_000_000]
D=R/'02_figures/06_icloud_acquired';D.mkdir(exist_ok=True)
records=[]
for p in targets:
    dest=D/p.name
    if dest.exists() and dest.stat().st_size==p.stat().st_size:
        print('ALREADY_ACQUIRED',p.name,flush=True);continue
    print('REQUEST',p,flush=True)
    subprocess.run(['brctl','download',str(p)],capture_output=True,timeout=30)
    start=time.monotonic()
    try:
        run=subprocess.run([sys.executable,__file__,'--copy',str(p),str(dest)],capture_output=True,text=True,timeout=300)
        if run.returncode:raise RuntimeError(run.stderr)
        raw=dest.read_bytes();assert len(raw)==p.stat().st_size
        record={'source':str(p),'saved':str(dest),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':'downloaded_and_read_verified','seconds':time.monotonic()-start}
    except Exception as e:
        record={'source':str(p),'status':'download_failed_or_timed_out','detail':str(e),'seconds':time.monotonic()-start}
    records.append(record)
    (D/'acquisition_log.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(json.dumps(record,ensure_ascii=False),flush=True)
