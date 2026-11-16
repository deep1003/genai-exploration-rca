"""Restore archived count tables and independently re-estimate recovered regression data."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,io,json,re
import numpy as np,pandas as pd,pyhdfe,statsmodels.api as sm
from scipy import stats
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.sandwich_covariance import cov_cluster
from linearmodels.iv import AbsorbingLS
from threadpoolctl import threadpool_limits
R=Path(__file__).resolve().parents[1];D=R/'07_reports/research_policy_20261116/table_recovery';D.mkdir(exist_ok=True)
NB=R/'02_figures/06_icloud_acquired/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'
raw=NB.read_bytes();nb=json.loads(raw)
class TableParser(HTMLParser):
    def __init__(self):super().__init__();self.body=False;self.cell=False;self.rows=[];self.row=[];self.value=''
    def handle_starttag(self,tag,attrs):
        if tag=='tbody':self.body=True
        if self.body and tag=='tr':self.row=[]
        if self.body and tag in ['td','th']:self.cell=True;self.value=''
    def handle_data(self,data):
        if self.cell:self.value+=data
    def handle_endtag(self,tag):
        if self.body and tag in ['td','th']:self.row.append(self.value.strip());self.cell=False
        if self.body and tag=='tr':self.rows.append(self.row)
        if tag=='tbody':self.body=False
def tables(cell):
    rows=[]
    for o in nb['cells'][cell].get('outputs',[]):
        html=o.get('data',{}).get('text/html')
        if html:
            p=TableParser();p.feed(''.join(html));rows.append(p.rows)
    return rows
arch=tables(289);assert len(arch)==2
rows=[]
for a in arch[1]:
    assert len(a)==10,a
    cid=int(a[0])+1;us,cn,kr,eu=map(int,a[1:5]);n=int(a[-1]);assert us+cn+kr+eu==n
    rows.append({'cluster':cid,'US_n':us,'CN_n':cn,'KR_n':kr,'EU_n':eu,'denominator':n,'US_pct':100*us/n,'CN_pct':100*cn/n,'other_included_pct':100*(kr+eu)/n})
t3=pd.DataFrame(rows);assert t3.query('cluster==1').CN_n.iloc[0]==24357
t3.to_csv(D/'table3_restored_from_counts.csv',index=False)
all_keywords=[]
for tab in tables(234):
    for a in tab:
        assert len(a)==10,a
        idx,cid,rank,keyword,us,cn,total,usp,cnp,ratio=a
        us,cn,total=int(us),int(cn),int(total);assert us+cn==total
        all_keywords.append({'cluster':int(cid),'keyword':keyword,'US_count':us,'CN_count':cn,'denominator':total,'US_pct':100*us/total,'CN_pct':100*cn/total})
kw=pd.DataFrame(all_keywords);kw.to_csv(D/'all_archived_keyword_counts.csv',index=False)
wanted=[(1,'attention'),(1,'image recognition'),(1,'embedding'),(4,'transformer'),(4,'attention'),(4,'pre-training'),(4,'speech recognition'),(4,'embedding')]
t4=pd.concat([kw[(kw.cluster==c)&(kw.keyword.str.casefold()==k)] for c,k in wanted],ignore_index=True);assert len(t4)==8
t4.to_csv(D/'table4_restored_from_counts.csv',index=False)
assert round(t4.query("cluster==1 and keyword=='attention'").CN_pct.iloc[0],1)==97.2
(D/'historical_count_provenance.json').write_text(json.dumps({'notebook':str(NB),'notebook_sha256':hashlib.sha256(raw).hexdigest(),'table3_cell':289,'table4_cell':234,'ratios_recomputed_from_integer_counts':True,'table3_denominator':'US, CN, KR and EU only; LLM-first cohort; any observed current RCA indicator > 0; unique appl_id','table4_denominator':'US plus CN regular-expression occurrence counts, not unique matched patents','historical_cluster_numbers_retained':True},indent=2))
print('HISTORICAL_TABLES_3_4_RECOVERED_AND_ARITHMETIC_CHECKED',flush=True)

RAW=['inventor_cet','cpc_cluster_dist_cos','I_cpc2','num_inventors','num_applicants','wips_family_pub_count','cited_by_count','citations_count','num_claims']
KEYS=['year','country_code','cpc_code'];source=R/'02_figures/09_original_regression_replay/original_numeric_input.parquet'
frame=pd.read_parquet(source);frame['I_cpc2']=frame.cpc_cluster_dist_cos**2
scaler=StandardScaler();z=scaler.fit_transform(frame[RAW]);names=['rca_y0']+[v+'_z' for v in RAW]
for j,v in enumerate(RAW):frame[v+'_z']=z[:,j]
mask=np.isfinite(frame[['rca_y1']+names]).all(axis=1)&frame[KEYS].notna().all(axis=1)
frame=frame.loc[mask].copy().reset_index(drop=True);assert len(frame)==510673
all_models=[];metadata=[]
def save_result(model,fit,design,clusters,meta,df_abs=0,archived=False):
    N,K=design.shape;G=len(np.unique(clusters))
    if archived:
        cov=cov_cluster(fit,clusters,use_correction=True);p=2*stats.norm.sf(np.abs(fit.params/np.sqrt(np.diag(cov))))
    else:
        correction=G/(G-1)*(N-1)/(N-K-df_abs)
        cov=cov_cluster(fit,clusters,use_correction=False)*correction
        p=2*stats.t.sf(np.abs(fit.params/np.sqrt(np.diag(cov))),G-1)
    se=np.sqrt(np.diag(cov))
    for term,b,s,pval in zip(design.columns,fit.params,se,p):all_models.append({'model':model,'term':term,'coefficient':float(b),'std_error':float(s),'pvalue':float(pval)})
    pd.DataFrame(cov,index=design.columns,columns=design.columns).to_csv(D/(model+'_covariance.csv'))
    metadata.append({'model':model,'nobs':N,'countries':G,'r_squared':float(fit.rsquared),'absorbed_degrees':int(df_abs),**meta})
def ids(d):return np.column_stack([pd.factorize(d[k],sort=True)[0] for k in KEYS])
def estimate_fe(d,model,rescale=False):
    first=pyhdfe.create(ids(d),drop_singletons=True,compute_degrees=False)
    keep=~first.singleton_indices;d=d.loc[keep].copy().reset_index(drop=True)
    if rescale:
        sc=StandardScaler().fit(d[RAW]);zz=sc.transform(d[RAW])
        for j,v in enumerate(RAW):d[v+'_z']=zz[:,j]
    X=d[names].astype(float);G=pd.factorize(d.country_code,sort=True)[0]
    alg=pyhdfe.create(ids(d),cluster_ids=G[:,None],drop_singletons=False,degrees_method='pairwise',options={'tol':1e-10})
    residual=alg.residualize(np.column_stack([d.rca_y1,X]))
    design=pd.DataFrame(residual[:,1:],columns=names)
    assert np.linalg.matrix_rank(design)==len(names)
    fit=sm.OLS(residual[:,0],design).fit()
    independent=AbsorbingLS(d.rca_y1,X,absorb=d[KEYS].astype('category')).fit(method='hdfe',cov_type='clustered',clusters=G,debiased=False,absorb_options={'options':{'tol':1e-10}})
    error=float(np.max(np.abs(independent.params-fit.params)));assert error<1e-7,error
    meta={'unit':'country-CPC-year cell' if rescale else 'patent-CPC row','fixed_effects':KEYS,'singletons_removed':int(first.singletons),'independent_coefficient_max_error':error}
    save_result(model,fit,design,G,meta,int(alg.degrees));print('FE_ESTIMATED',model,len(d),error,flush=True)
with threadpool_limits(limits=4):
    X=sm.add_constant(frame[names]);cl=pd.factorize(frame.country_code,sort=True)[0]
    pooled=sm.OLS(frame.rca_y1,X).fit()
    assert abs(pooled.params['cpc_cluster_dist_cos_z']-.11174646404563818)<1e-9
    save_result('recovered_pooled',pooled,X,cl,{'unit':'patent-CPC row','fixed_effects':[]},archived=True)
    good=~frame.country_code.astype(str).str.upper().isin(['','NONE','NAN','UNKNOWN'])&~frame.cpc_code.astype(str).str.upper().isin(['','NONE','NAN','UNKNOWN'])
    clean=frame[good].copy().reset_index(drop=True)
    estimate_fe(clean,'corrected_threeway_fe')
    within=clean.groupby(KEYS)[['rca_y0','rca_y1']].nunique();assert within.to_numpy().max()==1
    cell=clean.groupby(KEYS).agg({**{v:'mean' for v in RAW},'rca_y0':'first','rca_y1':'first'}).reset_index()
    estimate_fe(cell,'equal_cell_threeway_fe',rescale=True)
pd.DataFrame(all_models).to_csv(D/'table2_reestimated_coefficients.csv',index=False)
(D/'table2_model_metadata.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_rows':513533,'complete_rows':len(frame),'models':metadata,'historical_equivalence':False,'inference':'Pooled column reproduces archived normal-reference clustered inference; FE columns use country-cluster CR1 and t(G-1)'},indent=2))
print('ALL_THREE_TABLES_AVAILABLE',flush=True)
