from pathlib import Path
import json,zipfile,shutil,hashlib
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];A=R/'07_reports/overleaf_nine_release_20261116'
new='all_nine_600dpi_20261116';old='verified_figure4_600dpi_20261115'
downloads=Path('/Users/deep1003/Downloads')
zs=sorted(downloads.glob('조원선_박사님_01*.zip'),key=lambda p:p.stat().st_mtime)
source=zs[-1]
assert source.name!='조원선_박사님_01 (4).zip'
with zipfile.ZipFile(source) as z,zipfile.ZipFile(A/'before_update_source.zip') as prior:
    assert z.testzip() is None
    root=z.read('main.tex').decode();assert '\\input{'+new+'/main.tex}' in root
    assert z.read(new+'/main.tex')==(R/new/'main.tex').read_bytes()
    assert z.read(new+'/main.tex').decode().replace(new+'/media/',old+'/media/')==prior.read(old+'/main.tex').decode()
    for name in prior.namelist():
        if name!='main.tex' and not name.endswith('/'):assert z.read(name)==prior.read(name),name
    for i in range(1,10):assert z.read(f'{new}/media/image{i}.png')==(R/new/f'media/image{i}.png').read_bytes()
shutil.copy2(source,A/'after_update_source.zip')
pdf=max(downloads.glob('조원선_박사님_01*.pdf'),key=lambda p:p.stat().st_mtime)
assert pdf.stat().st_mtime>source.stat().st_mtime-600
shutil.copy2(pdf,A/'overleaf_all_nine.pdf')
reader=PdfReader(pdf);text='\n'.join(p.extract_text() or '' for p in reader.pages)
assert 'Frontier AI Lab' in text
for i in range(1,10):assert f'Fig. {i}.' in text
report={'online_source_matches_local_release':True,'all_nine_images_byte_verified':True,'all_prior_nonroot_files_preserved_byte_for_byte':True,'body_and_captions_unchanged_after_image_path_normalization':True,'pages':len(reader.pages),'pdf_bytes':pdf.stat().st_size,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'source_zip_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
(A/'online_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
