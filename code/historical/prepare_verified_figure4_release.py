from pathlib import Path
import json,hashlib,shutil,numpy as np,pandas as pd
from PIL import Image
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'02_data/manuscript_reproduction_20261108/patent_inputs_267519.parquet').exists())
a=pd.read_parquet(S/'02_data/manuscript_reproduction_20261108/patent_inputs_267519.parquet',columns=['embedding_row','appl_id','year','country_code']).sort_values('embedding_row').reset_index(drop=True)
b=pd.read_parquet(S/'05_revision/september_exact_code_replay_20261110/september_full_cache/df_pred_regenerated.parquet',columns=a.columns).sort_values('embedding_row').reset_index(drop=True)
assert len(a)==len(b)==267519
for c in a.columns:
    if c=='year':assert np.array_equal(a[c].astype(float),b[c].astype(float))
    else:assert np.array_equal(a[c].fillna('').astype(str),b[c].fillna('').astype(str)),c
with Image.open(R/'02_figures/08_original_array_replay/figure4_600dpi.png') as im:
    pixels=list(im.size);effective=pixels[0]/6.25
assert effective>=600
svg=json.loads((R/'00_admin/figure4_saved_svg_data_validation.json').read_text())
matched=svg[:3]
assert {r['series'] for r in matched}=={'US','CN','World'}
assert max(r['max_absolute_error'] for r in matched)<.00002
old=R/'word_verbatim_affiliation_b_20261115'
D=R/'verified_figure4_600dpi_20261115';D.mkdir(exist_ok=True)
shutil.copytree(old/'media',D/'media',dirs_exist_ok=True)
shutil.copy2(R/'02_figures/08_original_array_replay/figure4_600dpi.png',D/'media/image4.png')
source=(old/'main.tex').read_text();target=source.replace(old.name+'/media/',D.name+'/media/')
assert target.replace(D.name+'/media/',old.name+'/media/')==source
(D/'main.tex').write_text(target)
rec={'figure':4,'status':'verified at source-image precision; finite-precision numeric differences explicitly retained in audit','original_code_cells':[154,172],'metadata_rows_verified':267519,'metadata_fields':list(a.columns),'pixels':pixels,'effective_dpi_at_original_6_25_inches':effective,'saved_svg_series_comparison':matched,'maximum_numeric_difference':max(r['max_absolute_error'] for r in matched),'body_text_changed':False,'other_images_changed':False,'old_main_sha256':hashlib.sha256(source.encode()).hexdigest(),'new_main_sha256':hashlib.sha256(target.encode()).hexdigest(),'original_image4_sha256':hashlib.sha256((old/'media/image4.png').read_bytes()).hexdigest(),'replacement_sha256':hashlib.sha256((D/'media/image4.png').read_bytes()).hexdigest()}
(R/'00_admin/figure4_release_verification.json').write_text(json.dumps(rec,indent=2))
print(json.dumps(rec,indent=2))
