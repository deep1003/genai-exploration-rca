from pathlib import Path
import json, hashlib, zipfile
from PIL import Image, ImageChops
R=Path(__file__).resolve().parents[1]
D=R/'07_reports/all_nine_figures_600dpi_20261115'
status=json.loads((D/'generation_status.json').read_text())
assert status['all_nine_complete'] and not status['missing']
rows=json.loads((D/'figure_manifest.json').read_text())
assert len(rows)==9
for r in rows:
    png=Path(r['png']);tiff=Path(r['tiff'])
    assert hashlib.sha256(png.read_bytes()).hexdigest()==r['png_sha256']
    with Image.open(png) as a,Image.open(tiff) as b:
        assert a.size==b.size
        assert min(b.info['dpi'])>=600
        assert ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
master=R/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx'
sha=hashlib.sha256(master.read_bytes()).hexdigest()
assert sha=='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a'
report={'figures_generated':9,'main_figure_files':27,'minimum_effective_dpi':min(r['effective_dpi_at_word_width'] for r in rows),'verified_historical_image_precision':[4],'fresh_not_historical_matches':[1,2,3,5,6,7,8,9],'word_original_sha256':sha,'word_original_preserved':True,'png_tiff_pixels_identical':True,'overleaf_no_additional_replacements':True}
(D/'final_validation.json').write_text(json.dumps(report,indent=2))
N=next(R.parent.glob('*/03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'))
nb=json.loads(N.read_text())
Z=D.parent/'ALL_NINE_CODE_REPLOTS_600DPI_20261115.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED) as z:
    for p in D.iterdir():
        if p.is_file():z.write(p,p.name)
    for i in [133,134,135,142,151,154,172,189,197,219,233,235,245,250,252,261,263,287,294,298,316,318]:
        z.writestr(f'original_code/cell_{i}.py',''.join(nb['cells'][i]['source']))
    for p in (R/'06_scripts').glob('*.py'):
        if p.name in ['replot_all_remaining_panels.py','replot_period_panels.py','package_all_nine_replots.py','verify_final_nine_package.py','matplotlib_legacy_compat.py','fix_family_panel.py','render_tsne_checkpoint.py']:
            z.write(p,'reproduction_scripts/'+p.name)
    for p in (R/'02_figures/12_complete_replot_600dpi').glob('*provenance.json'):z.write(p,'provenance/'+p.name)
    assert z.testzip() is None
with zipfile.ZipFile(Z) as z:
    assert sum(n.endswith(('_600dpi.png','_600dpi.tiff','_vector.pdf')) for n in z.namelist())==27
print(json.dumps(report,indent=2));print('ZIP_BYTES',Z.stat().st_size)
