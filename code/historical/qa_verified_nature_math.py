from pathlib import Path
import json,re,sys,hashlib
import pdfplumber,pypdfium2 as pdfium
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];D=R/'07_reports/nature_math_verified_20261116'
pdf=Path(sys.argv[1]) if len(sys.argv)>1 else D/'local_compile/main.pdf'
prefix='online' if len(sys.argv)>1 else 'local'
log=(D/'local_compile/main.log').read_text()
assert not any(t in log for t in ['LaTeX Font Warning','Missing character:','Overfull \\hbox','Overfull \\vbox'])
assert 'Output written' in log
doc=pdfium.PdfDocument(str(pdf));records=[];thumbs=[];image_count=0
with pdfplumber.open(pdf) as parsed:
    for i,page in enumerate(parsed.pages):
        text=page.extract_text() or ''
        rec={'page':i+1,'images':len(page.images),'captions':re.findall(r'Fig\.\s*([1-9])\.',text),'text_chars':len(text)}
        image_count+=len(page.images)
        if page.images:
            rec['image_details']=[]
            for im in page.images:
                w,h=im['srcsize'];dpi=w/(im['x1']-im['x0'])*72
                assert dpi>=599
                rec['image_details'].append({'pixels':[w,h],'dpi_x':dpi,'bounds':[im['x0'],im['top'],im['x1'],im['bottom']]})
        img=doc[i].render(scale=1.3).to_pil().convert('RGB')
        if page.images or i in [4,5,6]:img.save(D/f'{prefix}_page_{i+1:02d}.png')
        img.thumbnail((460,650));thumbs.append(img)
        records.append(rec)
assert image_count==9,image_count
sheet=Image.new('RGB',(4*480,680*((len(thumbs)+3)//4)),'#ddd');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*480;y=(i//4)*680;sheet.paste(im,(x,y+23));draw.text((x+10,y+4),str(i+1),fill='black')
sheet.save(D/f'{prefix}_contact.jpg',quality=90)
(D/f'{prefix}_pdf_qa.json').write_text(json.dumps({'pages':len(doc),'figures':image_count,'font_warnings':0,'records':records,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()},indent=2))
print(json.dumps(records,indent=2))
