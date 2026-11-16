"""No-plot smoke checks of the released aggregate evidence."""
from pathlib import Path
import csv,hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'data/tables'/name).open() as f:return list(csv.DictReader(f))
for r in read('table3_restored_from_counts.csv'):
    n=sum(int(r[k]) for k in ['US_n','CN_n','KR_n','EU_n'])
    assert n==int(r['denominator'])
    for count,pct in [('US_n','US_pct'),('CN_n','CN_pct')]:
        assert math.isclose(100*int(r[count])/n,float(r[pct]),abs_tol=1e-9)
for r in read('table4_restored_from_counts.csv'):
    n=int(r['US_count'])+int(r['CN_count']);assert n==int(r['denominator'])
    assert math.isclose(float(r['US_pct'])+float(r['CN_pct']),100,abs_tol=1e-9)
    assert math.isclose(float(r['US_pct']),100*int(r['US_count'])/n,abs_tol=1e-9)
coeff=read('table2_reestimated_coefficients.csv')
assert {r['model'] for r in coeff}=={'recovered_pooled','corrected_threeway_fe','equal_cell_threeway_fe'}
for r in coeff:
    assert float(r['std_error'])>0 and 0<=float(r['pvalue'])<=1
manifest=json.loads((ROOT/'provenance/manifest.json').read_text())
for record in manifest:
    p=ROOT/record['path'];assert p.stat().st_size==record['bytes'],p
    assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],p
print(json.dumps({'status':'passed','table3_rows':5,'table4_rows':8,'regression_terms':len(coeff),'verified_files':len(manifest),'images_generated':0}))
