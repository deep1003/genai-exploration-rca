from pathlib import Path
import shutil,zipfile,hashlib,json
R=Path(__file__).resolve().parents[1]
old='verified_figure4_600dpi_20261115';new='all_nine_600dpi_20261116'
A=R/'07_reports/overleaf_nine_release_20261116';A.mkdir(exist_ok=True)
source=Path('/Users/deep1003/Downloads/조원선_박사님_01 (4).zip')
shutil.copy2(source,A/'before_update_source.zip')
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    original=z.read(old+'/main.tex')
    assert original==(R/old/'main.tex').read_bytes()
    (A/'before_root_main.tex').write_bytes(z.read('main.tex'))
    for i in range(1,10):assert z.read(f'{old}/media/image{i}.png')==(R/old/f'media/image{i}.png').read_bytes()
D=R/new;D.mkdir(exist_ok=False);(D/'media').mkdir()
updated=original.decode().replace(old+'/media/',new+'/media/')
assert updated.replace(new+'/media/',old+'/media/').encode()==original
(D/'main.tex').write_text(updated)
manifest=[]
F=R/'07_reports/all_nine_figures_600dpi_20261115'
for i in range(1,10):
    p=F/f'Figure_{i:02d}_600dpi.png';dest=D/f'media/image{i}.png';shutil.copy2(p,dest)
    manifest.append({'figure':i,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size})
(A/'release_integrity.json').write_text(json.dumps({'body_and_captions_byte_equal_after_path_normalization':True,'old_folder_preserved':old,'new_folder':new,'figures':manifest},indent=2))
with zipfile.ZipFile(A/'portable_overleaf_nine_figures.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('main.tex','\\AtBeginDocument{\\setmainfont{FreeSerif.otf}[BoldFont=FreeSerifBold.otf,ItalicFont=FreeSerifItalic.otf,BoldItalicFont=FreeSerifBoldItalic.otf]}\n\\input{'+new+'/main.tex}\n')
    for p in D.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(R))
print(D)
