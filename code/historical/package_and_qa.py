"""Package original-master review without modifying source files."""
from pathlib import Path
import shutil, json, hashlib, zipfile
from PIL import Image, ImageOps, ImageDraw
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
payload = ROOT / 'original_master_review_20261115'
payload.mkdir(exist_ok=True)
shutil.copytree(ROOT/'05_overleaf/figures', payload/'figures', dirs_exist_ok=True)
tex = (ROOT/'05_overleaf/main.tex').read_text()
tex = tex.replace('{figures/', '{original_master_review_20261115/figures/')
(payload/'main.tex').write_text(tex)
shutil.copy2(ROOT/'05_overleaf/build/main.pdf', ROOT/'05_overleaf/main.pdf')
shutil.copy2('/Users/deep1003/Downloads/조원선_박사님_01.zip', ROOT/'00_admin/overleaf_before_upload.zip')
shutil.copy2(ROOT/'04_review/change_log.csv',payload/'change_log.csv')
shutil.copy2(ROOT/'02_figures/00_embedded_originals/image3.png', ROOT/'02_figures/02_verified_high_resolution/image3_original_2004x590.png')
pdf = pdfium.PdfDocument(str(ROOT/'05_overleaf/main.pdf'))
thumbs=[]
for i in range(len(pdf)):
    im=pdf[i].render(scale=.6).to_pil().convert('RGB')
    im.thumbnail((300,420))
    tile=Image.new('RGB',(320,450),'#dddddd')
    tile.paste(im,((320-im.width)//2,20))
    ImageDraw.Draw(tile).text((10,430),str(i+1),fill='black')
    thumbs.append(tile)
for j in range(0,len(thumbs),12):
    sheet=Image.new('RGB',(1280,1350),'white')
    for k,im in enumerate(thumbs[j:j+12]): sheet.paste(im,((k%4)*320,(k//4)*450))
    sheet.save(ROOT/'07_reports'/f'pdf_contact_{j//12+1}.jpg')
for folder in ['qa_clean_final','qa_tracked']:
    files=sorted((ROOT/'04_review'/folder).glob('page-*.png'))
    for j in range(0,len(files),12):
        sheet=Image.new('RGB',(1280,1350),'white')
        for k,p in enumerate(files[j:j+12]):
            im=Image.open(p).convert('RGB'); im.thumbnail((300,420))
            sheet.paste(im,((k%4)*320,(k//4)*450))
        sheet.save(ROOT/'07_reports'/f'{folder}_{j//12+1}.jpg')
print(json.dumps({'pages':len(pdf),'payload':str(payload)}))
