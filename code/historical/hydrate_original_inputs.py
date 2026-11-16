from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parents[1]
if len(sys.argv)>1 and sys.argv[1]=='--probe':
    with open(sys.argv[2],'rb') as f:print(repr(f.read(200)))
    sys.exit(0)
S=next(p for p in R.parent.iterdir() if (p/'02_data/usb_import_20261108/X_all_embeddings.npy').exists())
targets=[S/'02_data/usb_import_20261108/X_all_embeddings.npy',S/'02_data/df_final.csv']
records=[]
for p in targets:
    print('HYDRATING',str(p),'BYTES',p.stat().st_size,flush=True)
    subprocess.run(['brctl','download',str(p)],capture_output=True,timeout=30)
    start=time.monotonic()
    try:
        run=subprocess.run([sys.executable,__file__,'--probe',str(p)],capture_output=True,text=True,timeout=1200)
        if run.returncode:raise RuntimeError(run.stderr)
        st=p.stat()
        rec={'path':str(p),'bytes':st.st_size,'allocated_bytes':st.st_blocks*512,'dataless':bool(st.st_flags&0x40000000),'header':run.stdout,'elapsed':time.monotonic()-start,'status':'read_succeeded'}
    except Exception as e:rec={'path':str(p),'status':'failed','detail':str(e),'elapsed':time.monotonic()-start}
    records.append(rec)
    (R/'00_admin/original_inputs_hydration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(json.dumps(rec,ensure_ascii=False),flush=True)
