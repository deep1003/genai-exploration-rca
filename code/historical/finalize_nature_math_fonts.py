from pathlib import Path
import shutil,json,zipfile
R=Path(__file__).resolve().parents[1]
old='nature_math_20261116';new='nature_math_verified_20261116'
src=R/old;dest=R/new;D=R/'07_reports/nature_math_verified_20261116';D.mkdir(exist_ok=True)
if not dest.exists():shutil.copytree(src,dest)
text=(src/'main.tex').read_text()
before=r'\setmainfont{FreeSerif.otf}'
after=r'\setmainfont{FreeSerif.otf}[BoldFont=FreeSerifBold.otf,ItalicFont=FreeSerifItalic.otf,BoldItalicFont=FreeSerifBoldItalic.otf]'
assert text.count(before)==1
updated=text.replace(before,after).replace(old+'/media/',new+'/media/')
(dest/'main.tex').write_text(updated)
(D/'font_patch.json').write_text(json.dumps({'before':before,'after':after,'reason':'Declare actual bold/italic files for the text font family used by Unicode math alphabets; do not suppress warnings'},indent=2))
root='\\AtBeginDocument{\\setmainfont{FreeSerif.otf}[BoldFont=FreeSerifBold.otf,ItalicFont=FreeSerifItalic.otf,BoldItalicFont=FreeSerifBoldItalic.otf]}\n\\input{'+new+'/main.tex}\n'
(D/'root_main.tex').write_text(root)
build=D/'local_compile';(build/new/'media').mkdir(parents=True,exist_ok=True)
(build/'main.tex').write_text(root)
shutil.copy2(dest/'main.tex',build/new/'main.tex')
for p in (dest/'media').glob('*.png'):shutil.copy2(p,build/new/'media'/p.name)
with zipfile.ZipFile(D/'portable_overleaf_verified.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('main.tex',root)
    for p in dest.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(R))
print(build)
