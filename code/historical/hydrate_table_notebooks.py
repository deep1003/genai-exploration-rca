from pathlib import Path
import json,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[1];D=R/'07_reports/research_policy_20261116/table_recovery'
data=json.loads((D/'search_hits.json').read_text());rows=[]
for name in data['cold_notebooks_not_yet_read']:
    p=Path(name);subprocess.run(['brctl','download',str(p)],capture_output=True)
    raw=p.read_bytes();json.loads(raw)
    rows.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    (D/'additional_hydration.json').write_text(json.dumps(rows,indent=2));print('HYDRATED',p.name,len(raw),flush=True)
subprocess.run([sys.executable,str(R/'06_scripts/recover_historical_tables.py')],check=True)
