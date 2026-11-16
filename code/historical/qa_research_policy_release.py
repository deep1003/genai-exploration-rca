"""Render all submission pages and verify tables, figures, fonts and preservation."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import pypdfium2 as pdfium
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1]
D=R/'07_reports/research_policy_20261116'
pdf=Path(sys.argv[1]) if len(sys.argv)>1 else D/'build_main/main.pdf'
prefix='online' if len(sys.argv)>1 else 'local'
doc=pdfium.PdfDocument(str(pdf));thumbs=[];records=[]
for i,page in enumerate(doc):
    text=page.get_textpage().get_text_range()
    img=page.render(scale=1.6).to_pil().convert('RGB')
    img.save(D/f'{prefix}_page_{i+1:02d}.png')
    img.thumbnail((360,510));thumbs.append(img)
    records.append({'page':i+1,'chars':len(text),'tables':re.findall(r'Table\s+(\d+):',text),'figures':re.findall(r'Figure\s+(\d+):',text)})
full='\n'.join(p.get_textpage().get_text_range() for p in doc)
for value in ['78,615','506,311','510,673','0.0465','83.8','97.2']:
    assert value in full,value
assert '20052009' not in full
assert '2005–2009' in full
assert all(any(str(n) in r['tables'] for r in records) for n in range(1,5)),records
assert all(any(str(n) in r['figures'] for r in records) for n in range(1,10)),records
assert 'Frontier AI Lab' not in full
fonts=subprocess.check_output(['/opt/homebrew/bin/pdffonts',str(pdf)],text=True)
assert all('yes' in line for line in fonts.splitlines()[2:])
(D/f'{prefix}_pdffonts.txt').write_text(fonts)
sheet=Image.new('RGB',(4*380,540*((len(thumbs)+3)//4)),'#ddd');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=i%4*380;y=i//4*540;sheet.paste(im,(x,y+22));draw.text((x+8,y+3),str(i+1),fill='black')
sheet.save(D/f'{prefix}_contact.jpg',quality=90)
master=R/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx'
assert hashlib.sha256(master.read_bytes()).hexdigest()=='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a'
result={'pages':len(doc),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'records':records,'original_word_unchanged':True,'tables_1_to_4_present':True,'figures_1_to_9_present':True}
(D/f'{prefix}_pdf_qa.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
