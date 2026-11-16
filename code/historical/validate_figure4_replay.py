from pathlib import Path
import json,numpy as np,pandas as pd
from PIL import Image
R=Path(__file__).resolve().parents[1]
S=next(p for p in R.parent.iterdir() if (p/'02_data/manuscript_reproduction_20261108/patent_inputs_267519.parquet').exists())
p=S/'02_data/manuscript_reproduction_20261108/patent_inputs_267519.parquet'
import subprocess
subprocess.run(['brctl','download',str(p)],capture_output=True)
df=pd.read_parquet(p)
print('ORIGINAL_INPUT_COLUMNS',df.columns.tolist(),flush=True)
original=R/'02_figures/07_backup_embedded_media/9b674132fcc0bdc8.png'
replayed=R/'02_figures/08_original_array_replay/figure4_preview.png'
def rect(a):
    dark=np.max(a,axis=2)<.35
    best=[]
    for y,row in enumerate(dark):
        starts=np.flatnonzero(np.diff(np.r_[False,row,False].astype(int))==1)
        ends=np.flatnonzero(np.diff(np.r_[False,row,False].astype(int))==-1)
        if len(starts):
            k=np.argmax(ends-starts);best.append((int(ends[k]-starts[k]),y,int(starts[k]),int(ends[k]-1)))
    longest=max(r[0] for r in best)
    lines=[r for r in best if r[0]>=longest*.98]
    top=min(lines,key=lambda r:r[1]);bottom=max(lines,key=lambda r:r[1])
    return [top[2],top[1],top[3],bottom[1]]
def curves(path):
    a=np.asarray(Image.open(path).convert('RGB'),dtype=float)/255
    x0,y0,x1,y1=rect(a);a=a[y0+2:y1-1,x0+2:x1-1]
    red=(a[:,:,0]>.65)&(a[:,:,1]<.5)&(a[:,:,2]<.5)
    blue=(a[:,:,2]>a[:,:,0]*1.2)&(a[:,:,2]>a[:,:,1]*1.05)&(a[:,:,0]<.7)
    out={}
    for name,mask in [('CN',red),('US',blue)]:
        xs=[];ys=[]
        for x in range(mask.shape[1]):
            iy=np.flatnonzero(mask[:,x])
            if len(iy):xs.append(x/(mask.shape[1]-1));ys.append(np.median(iy)/(mask.shape[0]-1))
        out[name]=(np.array(xs),np.array(ys))
    return [x0,y0,x1,y1],out
a,ca=curves(original);b,cb=curves(replayed)
rec={'original':str(original),'replayed':str(replayed),'original_axes':a,'replay_axes':b,'series':{}}
for c in ca:
    x=np.linspace(max(ca[c][0].min(),cb[c][0].min()),min(ca[c][0].max(),cb[c][0].max()),1000)
    error=np.interp(x,*ca[c])-np.interp(x,*cb[c])
    rec['series'][c]={'rmse_plot_height_fraction':float(np.sqrt(np.mean(error**2))),'max_error_plot_height_fraction':float(np.max(abs(error)))}
(R/'00_admin/figure4_curve_validation.json').write_text(json.dumps(rec,indent=2))
print(json.dumps(rec,indent=2))
