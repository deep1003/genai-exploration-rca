from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
files=sorted((R/'02_figures/01_candidates').glob('*.png'))
for j in range(0,len(files),20):
    out=Image.new('RGB',(1500,1200),'white')
    for k,p in enumerate(files[j:j+20]):
        im=Image.open(p).convert('RGB');im.thumbnail((290,265))
        x=(k%5)*300;y=(k//5)*300
        out.paste(im,(x,y));ImageDraw.Draw(out).text((x,y+270),p.stem,fill='black')
    out.save(R/'07_reports'/f'candidates_{j//20+1}.jpg')
