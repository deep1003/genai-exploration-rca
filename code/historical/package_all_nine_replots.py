"""Deliver actual 600-dpi code replots, explicitly separate from verified matches."""
from pathlib import Path
import json,csv,io,hashlib,shutil,zipfile,sys
from PIL import Image,ImageStat
from pypdf import PdfReader,PdfWriter,PageObject,Transformation
from pypdf._configuration import overwrite_configuration
from reportlab.pdfgen import canvas
import pypdfium2 as pdfium
# Trusted local scatter plots contain hundreds of thousands of vector points.
overwrite_configuration(stream_parsing_work_maximum_count=100_000_000)
R=Path(__file__).resolve().parents[1];B=R/'02_figures';F=B/'12_complete_replot_600dpi'
D=R/'07_reports/all_nine_figures_600dpi_20261115';D.mkdir(exist_ok=True)
def annotate(page,labels):
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(float(page.mediabox.width),float(page.mediabox.height)))
    c.setFont('Helvetica-Bold',12)
    for label,x,y in labels:c.drawString(x,y,label)
    c.save();buf.seek(0);page.merge_page(PdfReader(buf).pages[0])
def composite(paths,dest,vertical=False):
    readers=[PdfReader(p) for p in paths];pages=[r.pages[0] for r in readers]
    if vertical:
        width=576.;sizes=[(width,width*float(p.mediabox.height)/float(p.mediabox.width)) for p in pages]
        height=sum(h for w,h in sizes)+18*len(pages);out=PageObject.create_blank_page(width=width,height=height)
        y=height;labels=[]
        for i,(page,(w,h)) in enumerate(zip(pages,sizes)):
            y-=h+18;scale=w/float(page.mediabox.width)
            out.merge_transformed_page(page,Transformation().scale(scale).translate(ty=y))
            labels.append((f'({chr(97+i)})',2,y+h+4))
    else:
        common_h=max(float(p.mediabox.height) for p in pages)
        sizes=[(float(p.mediabox.width)*common_h/float(p.mediabox.height),common_h) for p in pages]
        factor=576./sum(w for w,h in sizes);height=common_h*factor
        out=PageObject.create_blank_page(width=576.,height=height+18);x=0;labels=[]
        for i,(page,(w,h)) in enumerate(zip(pages,sizes)):
            scale=factor*common_h/float(page.mediabox.height)
            out.merge_transformed_page(page,Transformation().scale(scale).translate(tx=x))
            labels.append((f'({chr(97+i)})',x+2,height+4));x+=w*factor
    annotate(out,labels);writer=PdfWriter();writer.add_page(out)
    with dest.open('wb') as f:writer.write(f)
def raster(pdf,png):
    doc=pdfium.PdfDocument(str(pdf));assert len(doc)==1
    doc[0].render(scale=600/72).to_pil().save(png,dpi=(600,600))
single={
1:(B/'10_original_tsne_replay/figure1_vector.pdf',B/'10_original_tsne_replay/figure1_600dpi.png'),
2:(B/'04_notebook_replay_600dpi/figure2_da3bbde622_vector.pdf',B/'04_notebook_replay_600dpi/figure2_da3bbde622_600dpi.png'),
4:(B/'08_original_array_replay/figure4_vector.pdf',B/'08_original_array_replay/figure4_600dpi.png'),
5:(F/'figure5_fresh.pdf',F/'figure5_fresh_600dpi.png'),
8:(F/'figure8_fresh.pdf',F/'figure8_fresh_600dpi.png')}
composites={
3:([B/'11_original_inputs_replay/figure3a_600dpi.pdf',B/'11_original_inputs_replay/figure3b_600dpi.pdf'],False),
6:([F/'figure6a_fresh.pdf',F/'figure6b_fresh.pdf'],False),
7:([F/'figure7a_fresh.pdf',F/'figure7b_fresh.pdf'],False),
9:([B/'10_original_tsne_replay/figure9a_vector.pdf',F/'figure9b_fresh.pdf'],True)}
rows=[];missing=[]
for i in range(1,10):
    pdf=D/f'Figure_{i:02d}_vector.pdf';png=D/f'Figure_{i:02d}_600dpi.png';tif=D/f'Figure_{i:02d}_600dpi.tiff'
    inputs=list(single[i]) if i in single else composites[i][0]
    if not all(p.exists() for p in inputs):missing.append(i);continue
    if i in single:shutil.copy2(single[i][0],pdf);shutil.copy2(single[i][1],png)
    else:composite(composites[i][0],pdf,composites[i][1]);raster(pdf,png)
    with Image.open(png) as im:
        pixels=list(im.size);dpi=list(im.info.get('dpi',()))
        assert dpi and min(dpi)>=599.9
        assert pixels[0]/(5.416667 if i==5 else 6.25)>=600
        assert max(ImageStat.Stat(im.convert('RGB')).stddev)>1
        im.convert('RGB').save(tif,dpi=(600,600),compression='tiff_lzw')
        preview=im.convert('RGB');preview.thumbnail((1400,1000));preview.save(D/f'Figure_{i:02d}_preview.jpg',quality=90)
    assert len(PdfReader(pdf).pages)==1
    rows.append({'figure':i,'png':str(png),'vector_pdf':str(pdf),'tiff':str(tif),'width_px':pixels[0],'height_px':pixels[1],'dpi_metadata':min(dpi),'effective_dpi_at_word_width':pixels[0]/(5.416667 if i==5 else 6.25),'status':'verified_source_image_precision' if i==4 else 'fresh_code_replot_not_historically_equivalent','overleaf_replaced':i==4,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'source_files':[str(p) for p in inputs]})
(D/'figure_manifest.json').write_text(json.dumps(rows,indent=2))
with (D/'figure_manifest.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(D/'generation_status.json').write_text(json.dumps({'generated_figures':[r['figure'] for r in rows],'missing':missing,'all_nine_complete':len(rows)==9,'word_modified':False,'overleaf_only_verified_figure4':True},indent=2))
print(json.dumps({'generated':[r['figure'] for r in rows],'missing':missing,'folder':str(D)},indent=2))
if missing and '--allow-partial' not in sys.argv:raise RuntimeError('Do not claim all nine complete until missing figure panels exist.')
if not missing:
    with zipfile.ZipFile(D.parent/'ALL_NINE_CODE_REPLOTS_600DPI_20261115.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in D.iterdir():
            if p.is_file():z.write(p,p.name)
        for p in (F/'original_cells').glob('*.py'):z.write(p,'original_code/'+p.name)
        for p in [F/'fresh_replot_provenance.json',F/'figure9b_provenance.json']:
            if p.exists():z.write(p,'provenance/'+p.name)
        assert z.testzip() is None
