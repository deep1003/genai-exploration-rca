from pathlib import Path
import json
import pypdfium2 as pdfium
import pdfplumber
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];D=R/'07_reports/overleaf_nine_release_20261116'
pdf=D/'overleaf_all_nine.pdf';doc=pdfium.PdfDocument(str(pdf));records=[];thumbs=[]
with pdfplumber.open(pdf) as parsed:
    for n,page in enumerate(parsed.pages):
        images=page.images
        if n==0 or images:
            im=doc[n].render(scale=1.25).to_pil().convert('RGB')
            im.save(D/f'qa_page_{n+1:02d}.png')
            im.thumbnail((600,850));thumbs.append((n+1,im.copy()))
        for image in images:
            w,h=image['srcsize'];width=image['x1']-image['x0'];height=image['bottom']-image['top']
            records.append({'page':n+1,'pixels':[w,h],'effective_dpi_x':w/width*72,'effective_dpi_y':h/height*72})
assert len(records)==9,len(records)
assert min(r['effective_dpi_x'] for r in records)>=600
(D/'embedded_images_qa.json').write_text(json.dumps(records,indent=2))
sheet=Image.new('RGB',(1800,900*((len(thumbs)+2)//3)),'#dddddd');draw=ImageDraw.Draw(sheet)
for i,(page,im) in enumerate(thumbs):
    x=(i%3)*600;y=(i//3)*900;sheet.paste(im,(x,y+25));draw.text((x+10,y+5),f'Page {page}',fill='black')
sheet.save(D/'qa_contact_sheet.jpg',quality=90)
print(json.dumps(records,indent=2))
