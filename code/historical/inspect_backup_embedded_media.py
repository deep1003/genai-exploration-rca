from pathlib import Path
import zipfile,io,hashlib,json
from PIL import Image,ImageDraw
from scipy.fft import dctn
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'02_figures/07_backup_embedded_media';D.mkdir(exist_ok=True)
def feature(im):
    f=dctn(np.asarray(im.convert('L').resize((32,32)),dtype=float),norm='ortho')[:8,:8];return f>np.median(f)
targets={p.name:(Image.open(p).size,feature(Image.open(p))) for p in (R/'02_figures/00_embedded_originals').glob('*.png')}
records=[]
def inspect(z,origin,depth=0):
    for n in z.namelist():
        suffix=Path(n).suffix.lower()
        if suffix in ['.pptx','.docx','.zip'] and depth<2:
            try:inspect(zipfile.ZipFile(io.BytesIO(z.read(n))),origin+'!'+n,depth+1)
            except Exception:pass
        elif suffix in ['.png','.jpeg','.jpg','.tiff','.svg','.emf','.wmf']:
            raw=z.read(n);h=hashlib.sha256(raw).hexdigest();p=D/(h[:16]+suffix);p.write_bytes(raw)
            rec={'source':origin+'!'+n,'file':str(p),'sha256':h,'bytes':len(raw)}
            try:
                im=Image.open(io.BytesIO(raw));w,hgt=im.size;feat=feature(im)
                rec.update(width=w,height=hgt,matches=[{'figure':fig,'distance':int(np.count_nonzero(feat!=f))} for fig,(size,f) in targets.items() if int(np.count_nonzero(feat!=f))<=14 and abs((w/hgt)/(size[0]/size[1])-1)<.25])
            except Exception:pass
            records.append(rec)
for p in (R/'02_figures/06_icloud_acquired').glob('*.zip'):
    with zipfile.ZipFile(p) as z:inspect(z,str(p))
(D/'media_inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('MEDIA',len(records))
for rec in records:
    if rec.get('matches'):print(json.dumps(rec,ensure_ascii=False))
images=[r for r in records if 'width' in r]
for j in range(0,len(images),20):
    sheet=Image.new('RGB',(1500,1200),'white')
    for k,rec in enumerate(images[j:j+20]):
        im=Image.open(rec['file']).convert('RGB');im.thumbnail((290,265));x=k%5*300;y=k//5*300
        sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x,y+270),Path(rec['file']).stem+' '+str(rec['width']),fill='black')
    sheet.save(D/f'contact_{j//20+1}.jpg')
