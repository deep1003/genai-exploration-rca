from pathlib import Path
import ast,csv,difflib,hashlib,json,re,shutil,zipfile
from PIL import Image,ImageStat
from pypdf._configuration import overwrite_configuration
overwrite_configuration(stream_parsing_work_maximum_count=100_000_000)
R=Path(__file__).resolve().parents[1];S=R/'02_figures/13_nature_labels_20261116'
D=R/'07_reports/nature_math_20261116';D.mkdir(exist_ok=True)
name='nature_math_20261116';release=R/name;(release/'media').mkdir(parents=True,exist_ok=True)
t=ast.parse((R/'06_scripts/package_all_nine_replots.py').read_text())
t.body=[n for n in t.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
env={};exec(compile(t,'packaging-functions','exec'),env)
panels={1:['figure1'],2:['figure2'],3:['figure3a','figure3b'],4:['figure4'],5:['figure5'],6:['figure6a','figure6b'],7:['figure7a','figure7b'],8:['figure8'],9:['figure9a','figure9b']}
manifest=[]
for i,parts in panels.items():
    pdf=D/f'Figure_{i:02d}_vector.pdf';png=D/f'Figure_{i:02d}_600dpi.png'
    if len(parts)==1:shutil.copy2(S/(parts[0]+'.pdf'),pdf)
    else:env['composite']([S/(p+'.pdf') for p in parts],pdf,vertical=i in [7,9])
    env['raster'](pdf,png)
    with Image.open(png) as im:
        assert min(im.info['dpi'])>=599.9 and im.width/6.25>=600
        assert max(ImageStat.Stat(im.convert('RGB')).stddev)>1
        im.convert('RGB').save(D/f'Figure_{i:02d}_600dpi.tiff',dpi=(600,600),compression='tiff_lzw')
        small=im.convert('RGB');small.thumbnail((1500,1500));small.save(D/f'Figure_{i:02d}_preview.jpg',quality=90)
        manifest.append({'figure':i,'pixels':list(im.size),'dpi':600,'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'layout':'vertical' if i in [7,9] else 'unchanged'})
    shutil.copy2(png,release/f'media/image{i}.png')
    print('PACKAGED',i,flush=True)
(D/'figure_manifest.json').write_text(json.dumps(manifest,indent=2))
oldname='all_nine_600dpi_20261116'
original=(R/oldname/'main.tex').read_text();text=original;changes=[]
def change(old,new,reason):
    global text
    assert old in text,old
    count=text.count(old);line=text[:text.find(old)].count('\n')+1
    text=text.replace(old,new)
    changes.append({'line_at_change':line,'count':count,'reason':reason,'before':old,'after':new})
change(oldname+'/media/',name+'/media/','New figure assets; prior version preserved')
change('dist\\_i = 1 −\n(e\\_i · μ\\_k(i)) / (‖e\\_i‖ ‖μ\\_k(i)‖)',r'''\[
\mathrm{dist}_{i}
=1-\frac{\mathbf{e}_{i}\cdot\boldsymbol{\mu}_{k(i)}}
{\lVert\mathbf{e}_{i}\rVert\,\lVert\boldsymbol{\mu}_{k(i)}\rVert}
\]''','Cosine-distance expression in native LaTeX')
change('RCA\\_\\{c,j,t\\} = (patent\\_\\{c,j,t\\} / Σ\\_j\npatent\\_\\{c,j,t\\}) / (Σ\\_c patent\\_\\{c,j,t\\} / Σ\\_c Σ\\_j\npatent\\_\\{c,j,t\\})',r'''\[
\mathrm{RCA}_{c,j,t}
=\frac{\displaystyle\frac{\mathrm{patent}_{c,j,t}}
{\sum_j\mathrm{patent}_{c,j,t}}}
{\displaystyle\frac{\sum_c\mathrm{patent}_{c,j,t}}
{\sum_c\sum_j\mathrm{patent}_{c,j,t}}}
\]''','RCA definition with native fractions and sums')
change('RCA\\_\\{c,j,t+1\\} = α\n+ β₁ RCA\\_\\{c,j,t\\} + β₂ dist\\_\\{c,j,t\\} + β₃ dist²\\_\\{c,j,t\\} +\nγ′X\\_\\{c,j,t\\} + δ\\_t + θ\\_c + φ\\_j + ε\\_\\{c,j,t\\}',r'''\[
\begin{aligned}
\mathrm{RCA}_{c,j,t+1}
&=\alpha+\beta_1\mathrm{RCA}_{c,j,t}
+\beta_2\mathrm{dist}_{c,j,t}
+\beta_3\mathrm{dist}^{2}_{c,j,t}\\
&\quad+\boldsymbol{\gamma}^{\prime}\mathbf{X}_{c,j,t}
+\delta_t+\theta_c+\phi_j+\varepsilon_{c,j,t}
\end{aligned}
\]''','Regression expression with aligned terms, subscripts, powers and Greek symbols')
for old,new in [
 ('rca\\_y1',r'\(\mathrm{rca}_{y1}\)'),
 ('rca\\_y01',r'\(\mathrm{rca}_{y01}\)'),
 ('RCA\\_y0',r'\(\mathrm{RCA}_{y0}\)'),
 ('δ\\_t',r'\(\delta_t\)'),('θ\\_c',r'\(\theta_c\)'),('φ\\_j',r'\(\phi_j\)'),
 ('−β₂/(2β₃)',r'\(-\beta_2/(2\beta_3)\)'),
 ('β₂',r'\(\beta_2\)'),('β₃',r'\(\beta_3\)'),
 ('where dist is',r'where \(\mathrm{dist}\) is'),
 ('of dist.',r'of \(\mathrm{dist}\).'),
 ('cell, X is',r'cell, \(\mathbf{X}\) is'),
 ('patent i is',r'patent \(i\) is'),
 ('country c, CPC code j, and year t',r'country \(c\), CPC code \(j\), and year \(t\)'),
 ('year t (',r'year \(t\) ('),
 ('year t+1',r'year \(t+1\)'),
 ('both t\nand t+1',r'both \(t\)'+'\n'+r'and \(t+1\)'),
 ('year t\nraises',r'year \(t\)'+'\nraises'),
 ]:
    if old in text:change(old,new,'Inline mathematical notation; definition unchanged')
# Negative coefficients are mathematical quantities, not punctuation.
for token in sorted(set(re.findall(r'−\d+\.\d+',text))):
    change(token,r'\(-'+token[1:]+r'\)','Typeset negative numeric coefficient')
# A vertically stacked Figure 7 must not inherit the old wide, shallow frame.
lines=text.splitlines()
for j,line in enumerate(lines):
    if line.startswith('\\includegraphics') and '/media/image7.png}' in line:
        replacement=re.sub(r',height=[^,\]]+',',keepaspectratio',line)
        change(line,replacement,'Figure 7 panels stacked at full manuscript width')
        break
for token in ['\\_','β','γ','δ','θ','φ','ε','Σ','‖']:
    assert token not in text,token
restored=text
for item in reversed(changes):restored=restored.replace(item['after'],item['before'])
assert restored==original,'Unlogged prose change'
(release/'main.tex').write_text(text)
(D/'changes.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False))
(D/'manuscript.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=oldname+'/main.tex',tofile=name+'/main.tex')))
with (D/'changes.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=changes[0].keys());w.writeheader();w.writerows(changes)
shutil.copy2(S/'text_and_geometry_audit.json',D/'text_and_geometry_audit.json')
wrapper='\\AtBeginDocument{\\setmainfont{FreeSerif.otf}[BoldFont=FreeSerifBold.otf,ItalicFont=FreeSerifItalic.otf,BoldItalicFont=FreeSerifBoldItalic.otf]}\n\\input{'+name+'/main.tex}\n'
(D/'root_main.tex').write_text(wrapper)
with zipfile.ZipFile(D/'portable_overleaf_nature_math.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('main.tex',wrapper)
    for p in release.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(R))
    assert z.testzip() is None
(D/'preservation_check.json').write_text(json.dumps({'all_nonmath_prose_preserved_by_reversible_patch':True,'prior_source_preserved':True,'figure7_vertical':True,'native_display_equations':text.count('\\['),'logged_changes':len(changes)},indent=2))
print('NATURE_MATH_RELEASE_READY',flush=True)
