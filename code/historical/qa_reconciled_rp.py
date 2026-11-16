"""No recalculation: verify manuscript text, render pages and inspect release assets."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];N='research_policy_reconciled_20261116';D=R/'07_reports'/N
pdf=Path(sys.argv[1]) if len(sys.argv)>1 else D/'build_main/main.pdf'
prefix='online' if len(sys.argv)>1 else 'local'
doc=pdfium.PdfDocument(str(pdf));texts=[];thumbs=[];records=[]
for i,page in enumerate(doc):
    text=page.get_textpage().get_text_range();texts.append(text)
    img=page.render(scale=1.6).to_pil().convert('RGB');img.save(D/f'{prefix}_page_{i+1:02d}.png')
    img.thumbnail((360,510));thumbs.append(img)
    records.append({'page':i+1,'notes':text.count('Notes:'),'tables':re.findall(r'Table\s+(\d+):',text),'figures':re.findall(r'Figure\s+(\d+):',text)})
full='\n'.join(texts)
assert full.count('Notes:')==13,full.count('Notes:')
for value in ['0.0465','0.0155','0.0336','0.1234','78,615','keyword occurrences','e0301091','genai-exploration-rca']:
    assert value in full,value
assert '0.127' not in full and '0.119' not in full and '0.546' not in full
assert all(any(str(n) in rec['tables'] for rec in records) for n in range(1,5))
assert all(any(str(n) in rec['figures'] for rec in records) for n in range(1,10))
assert 'Frontier AI Lab' not in full
fonts=subprocess.check_output(['/opt/homebrew/bin/pdffonts',str(pdf)],text=True)
assert all('yes' in row for row in fonts.splitlines()[2:])
(D/f'{prefix}_fonts.txt').write_text(fonts)
sheet=Image.new('RGB',(4*380,540*((len(thumbs)+3)//4)),'#ddd');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=i%4*380;y=i//4*540;sheet.paste(im,(x,y+22));draw.text((x+8,y+3),str(i+1),fill='black')
sheet.save(D/f'{prefix}_contact.jpg',quality=90)
master=R/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx'
assert hashlib.sha256(master.read_bytes()).hexdigest()=='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a'
for n in [3,4]:
    f=pdfium.PdfDocument(str(R/N/f'figures/Figure_{n:02d}.pdf'))
    t=f[0].get_textpage().get_text_range()
    assert t.count('Global mean')==1,(n,t)
    f[0].render(scale=2).to_pil().save(D/f'figure{n}_legend_preview.png')
result={'pages':len(doc),'notes_blocks':13,'tables':4,'figures':9,'word_master_unchanged':True,'records':records,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}
(D/f'{prefix}_qa.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
