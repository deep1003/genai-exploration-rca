"""Replot the 15 printed Figure 8 labels, not a new network estimate."""
from pathlib import Path
import csv,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'02_figures/03_regeneration_600dpi/figure8_printed_values'
OUT.mkdir(parents=True,exist_ok=True)
DPI=600
WIDTH_IN=12
HEIGHT_IN=6
PRINT_WIDTH_IN=160/25.4
PERIODS=['2000–2004','2005–2009','2010–2014','2015–2019','2020–2024']
# Transcribed from the preserved manuscript image, including its rounding.
SHARES={'US':[46.8,60.3,42.3,14.8,53.2],
        'CN':[2.7,2.9,43.1,85.2,44.1],
        'KR':[8.9,17.1,2.2,0.0,0.5]}
COLORS={'US':'#1f77b4','CN':'#d62728','KR':'#2ca02c'}
with (OUT/'figure8_printed_values.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['period','country','printed_percent','source','precision'])
    for i,period in enumerate(PERIODS):
        for country in SHARES:
            writer.writerow([period,country,SHARES[country][i],'master DOCX image8.png','one decimal place'])
with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,
                     'axes.labelsize':10,'xtick.labelsize':10,'ytick.labelsize':10,
                     'savefig.dpi':DPI,'figure.dpi':100,'pdf.fonttype':42,'ps.fonttype':42}):
    fig,ax=plt.subplots(figsize=(WIDTH_IN,HEIGHT_IN))
    indices=np.arange(len(PERIODS));width=.25
    for i,country in enumerate(SHARES):
        perc=np.array(SHARES[country])
        pos=indices+(i-1)*width
        ax.bar(pos,100-perc,width,bottom=perc,color='#CCCCCC',edgecolor='none')
        bars=ax.bar(pos,perc,width,color=COLORS[country],edgecolor='none')
        for bar in bars:
            h=bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2,h/2,f'{h:.1f}%',ha='center',va='center',fontsize=8,color='white')
    ax.set_xticks(indices);ax.set_xticklabels(PERIODS,rotation=0)
    ax.set_xlabel('Period');ax.set_ylabel('Percentage of Core Nodes (%)')
    ax.set_title('Core Composition by Period for US, CN, KR')
    ax.legend(handles=[Patch(facecolor=COLORS[c],label=c) for c in SHARES],title='Country',loc='upper left')
    fig.tight_layout()
    for ext in ['png','tiff','pdf']:
        kwargs={'pil_kwargs':{'compression':'tiff_lzw'}} if ext=='tiff' else {}
        fig.savefig(OUT/f'figure8_printed_values_600dpi.{ext}',dpi=DPI,**kwargs)
    fig.savefig(OUT/'figure8_preview.png',dpi=120)
    plt.close(fig)
with Image.open(OUT/'figure8_printed_values_600dpi.png') as im:
    width,height=im.size
    effective=width/PRINT_WIDTH_IN
    assert width>=int(np.ceil(DPI*PRINT_WIDTH_IN))
    assert min(im.info['dpi'])>=599.9
record={'figure':8,'status':'review candidate; rounded printed values, not exact underlying data',
        'native_render':True,'image_upscaled':False,'new_network_estimation':False,
        'dpi':DPI,'pixels':[width,height],'effective_dpi_at_160mm':effective,
        'master_image_sha256':hashlib.sha256((ROOT/'02_figures/00_embedded_originals/image8.png').read_bytes()).hexdigest(),
        'source_code':'03_evidence/notebook_2d23b9e146_cell_263.txt',
        'value_source':'15 one-decimal labels in original embedded image8.png',
        'vector_pdf':True,'overleaf_replaced':False,
        'limits':'Underlying bar heights may differ by up to 0.05 percentage point due to displayed rounding. Historical counts and sampling are not recovered.'}
(OUT/'provenance.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
