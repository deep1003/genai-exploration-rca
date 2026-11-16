from pathlib import Path
import re,json,numpy as np,pandas as pd
from lxml import etree as E
R=Path(__file__).resolve().parents[1]
svg=R/'02_figures/06_icloud_acquired/country_trajectories_with_world_band_2025-12-26_20-58-13.svg'
root=E.parse(str(svg));ns={'s':'http://www.w3.org/2000/svg'}
def ticks(prefix,coord):
    out=[]
    for g in root.xpath(f'//s:g[starts-with(@id,"{prefix}")]',namespaces=ns):
        comments=g.xpath('.//comment()')
        vals=[c.text.strip() for c in comments if re.fullmatch(r'-?\d+(?:\.\d+)?',c.text.strip())]
        uses=g.xpath('.//s:use[@x][@y]',namespaces=ns)
        if vals and uses:out.append((float(uses[0].get(coord)),float(vals[0])))
    return np.array(out)
tx=ticks('xtick_','x');ty=ticks('ytick_','y')
assert len(tx)>1 and len(ty)>1
cx=np.polyfit(tx[:,0],tx[:,1],1);cy=np.polyfit(ty[:,0],ty[:,1],1)
country=pd.read_csv(R/'02_figures/08_original_array_replay/figure4_country_data.csv',index_col=0)
world=pd.read_csv(R/'02_figures/08_original_array_replay/figure4_world_data.csv').set_index('year')['mean']
records=[]
for g in root.xpath('//s:g[starts-with(@id,"line2d_")]',namespaces=ns):
    for p in g.xpath('./s:path[@d]',namespaces=ns):
        nums=re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',p.get('d'))
        if len(nums)<40 or len(nums)%2:continue
        a=np.array(nums,dtype=float).reshape(-1,2)
        years=np.polyval(cx,a[:,0]);values=np.polyval(cy,a[:,1])
        if np.max(abs(years-np.round(years)))>.01:continue
        years=np.round(years).astype(int)
        for name,series in [('US',country['US']),('CN',country['CN']),('World',world)]:
            if not set(years)<=set(series.index):continue
            error=values-series.reindex(years).to_numpy()
            records.append({'svg_line':g.get('id'),'series':name,'points':len(years),'max_absolute_error':float(abs(error).max()),'rmse':float(np.sqrt(np.mean(error**2)))})
records.sort(key=lambda r:r['max_absolute_error'])
(R/'00_admin/figure4_saved_svg_data_validation.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records[:9],indent=2))
ci_results=[]
world_ci=pd.read_csv(R/'02_figures/08_original_array_replay/figure4_world_data.csv').set_index('year')
for g in root.xpath('//s:g[contains(@id,"PolyCollection_")]',namespaces=ns):
    for p in g.xpath('.//s:path[@d]',namespaces=ns):
        nums=re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',p.get('d'))
        if len(nums)<80 or len(nums)%2:continue
        a=np.array(nums,dtype=float).reshape(-1,2)
        ref=g.xpath('.//s:use[@xlink:href="#'+p.get('id','')+'"]',namespaces={**ns,'xlink':'http://www.w3.org/1999/xlink'})
        if ref:a+=np.array([float(ref[0].get('x','0')),float(ref[0].get('y','0'))])
        years=np.polyval(cx,a[:,0]);vals=np.polyval(cy,a[:,1])
        if np.max(abs(years-np.round(years)))>.01:continue
        years=np.round(years).astype(int)
        if not set(years)<=set(world_ci.index):continue
        diffs=[]
        for year in sorted(set(years)):
            v=vals[years==year]
            diffs.extend([v.min()-world_ci.loc[year,'ci_lower'],v.max()-world_ci.loc[year,'ci_upper']])
        ci_results.append({'svg_polygon':g.get('id'),'years':len(set(years)),'max_absolute_error':float(np.max(np.abs(diffs)))})
ci_results.sort(key=lambda r:r['max_absolute_error'])
(R/'00_admin/figure4_saved_svg_ci_validation.json').write_text(json.dumps(ci_results,indent=2))
print('CONFIDENCE_BAND_COMPARISON',json.dumps(ci_results,indent=2))
