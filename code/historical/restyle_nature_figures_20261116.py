"""Typography-only revision of the deployed nine figures, using cached coordinates."""
from pathlib import Path
import ast,contextlib,hashlib,io,json,pickle,textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Text
from threadpoolctl import threadpool_limits
from matplotlib_legacy_compat import install_legacy_colormap_api

R=Path(__file__).resolve().parents[1]
D=R/'02_figures/13_nature_labels_20261116';D.mkdir(exist_ok=True)
N=next(R.parent.glob('*/03_code/Patent_analysis_LLM_1_Jupyter_notebook_11(en) (17)_1 (14) (9).ipynb'))
S=N.parents[1];cache=S/'05_revision/september_exact_code_replay_20261110/september_full_cache'
nb=json.loads(N.read_text());install_legacy_colormap_api()
matplotlib.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42})
records=[]

def execute(i,env,tree=None):
    code=''.join(nb['cells'][i]['source']).replace('plt.show()','').replace('%matplotlib inline','')
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(tree if tree is not None else code,str(N)+f'#{i}','exec'),env)

def geometry(fig):
    h=hashlib.sha256()
    def add(a):
        a=np.asarray(a);h.update(str(a.shape).encode());h.update(str(a.dtype).encode());h.update(a.tobytes())
    for ax in fig.axes:
        add(ax.get_xlim());add(ax.get_ylim())
        for line in ax.lines:
            add(line.get_xdata());add(line.get_ydata())
            h.update(repr((line.get_color(),line.get_linestyle(),line.get_linewidth(),line.get_marker(),line.get_markersize(),line.get_alpha())).encode())
        for c in ax.collections:
            add(c.get_offsets());add(c.get_facecolors());add(c.get_edgecolors());add(c.get_linewidths());add(c.get_sizes() if hasattr(c,'get_sizes') else [])
            for p in c.get_paths():add(p.vertices)
        for p in ax.patches:
            add(p.get_path().vertices);add(p.get_transform().get_matrix() if False else [])
            h.update(repr((p.get_facecolor(),p.get_edgecolor(),p.get_linewidth(),p.get_alpha())).encode())
            if hasattr(p,'get_x'):
                add([p.get_x(),p.get_y(),p.get_width(),p.get_height()])
    return h.hexdigest()

LEGEND={
 'US':'United States','CN':'China','KR':'South Korea',
 'Global Average':'Global mean','Global 95% CI':'95% CI',
 'World mean':'Global mean','World 95% CI':'95% CI',
 'NonGenAI (≤ 0.4)':'Non-GenAI (score ≤ 0.4)',
 'GenAI (≥ 0.6)':'GenAI (score ≥ 0.6)',
 '2017 cutoff':'Transformer introduction (2017)',
 '2017 (BASE)':'Reference year (2017)',
 'Coefficient (GenAI × DY)':'GenAI–non-GenAI difference',
 'Cluster distance effect':'Model prediction',
 'LLM (CN)':'Chinese LLM patents','Other':'Other patents',
 'Chinese Patents':'Chinese patents','US Patents':'US patents',
 'LLM Sub-category Anchors':'LLM subcategory anchors',
 'Low (−1 SD)':'Low (−1 s.d.)','High (+1 SD)':'High (+1 s.d.)','Mean (0)':'Mean',
}
TITLES={
 'figure1':'Technological structure of AI patents',
 'figure2':'Growth of LLM patenting',
 'figure3a':'Inventor team size','figure3b':'Patent-family coverage',
 'figure4':'Technological exploration over time',
 'figure5':'Exploration distance and comparative advantage',
 'figure6a':'Moderation by inventor team size',
 'figure6b':'Moderation by patent-family coverage',
 'figure7a':'Technological distance in GenAI and non-GenAI patents',
 'figure7b':'Distance differences around the Transformer introduction',
 'figure8':'National representation in the inventor-network core',
 'figure9a':'US and Chinese patents in technological space',
}
AXES={
 'figure2':('Year','LLM patent applications'),
 'figure3a':('Year','Mean inventors per patent'),
 'figure3b':('Year','Mean family publications per patent'),
 'figure4':('Year','Mean technological distance'),
 'figure5':('Standardised technological distance','Predicted RCA at year t + 1'),
 'figure6a':('Standardised technological distance','Predicted RCA at year t + 1'),
 'figure6b':('Standardised technological distance','Predicted RCA at year t + 1'),
 'figure7a':('Year','Mean technological distance'),
 'figure7b':('Years relative to 2017','Distance difference\n(GenAI − non-GenAI)'),
 'figure8':('Filing period','Share of core inventors (%)'),
}

def save(name):
    fig=plt.gcf();fig.canvas.draw();before=geometry(fig)
    with (D/f'{name}_before.pkl').open('wb') as f:pickle.dump(fig,f)
    texts_before=[x.get_text() for x in fig.findobj(Text) if x.get_text()]
    for text in fig.findobj(Text):text.set_fontfamily('Arial')
    width=fig.get_figwidth()
    final_width=3.125 if name in ['figure3a','figure3b','figure6a','figure6b'] else 6.25
    if name=='figure5':final_width=5.41667
    factor=width/final_width
    title_size=8*factor;axis_size=8*factor;tick_size=6.5*factor;legend_size=6.5*factor
    for ax in fig.axes:
        if name=='figure9b':
            old=ax.get_title()
            if old:ax.set_title(old[old.find('(')+1:old.rfind(')')],fontsize=title_size,pad=8)
            if ax.get_xlabel():ax.set_xlabel('t-SNE 1',fontsize=axis_size,labelpad=5)
            if ax.get_ylabel():ax.set_ylabel('t-SNE 2',fontsize=axis_size,labelpad=5)
        else:
            if ax.get_title():
                title=TITLES.get(name,ax.get_title())
                if name in ['figure7a','figure7b']:title=textwrap.fill(title,36)
                ax.set_title(title,fontsize=title_size,pad=9)
            if name in AXES:
                ax.set_xlabel(AXES[name][0],fontsize=axis_size,labelpad=6)
                ax.set_ylabel(AXES[name][1],fontsize=axis_size,labelpad=7)
        ax.tick_params(labelsize=tick_size)
        leg=ax.get_legend()
        if leg:
            for text in leg.get_texts():
                text.set_text(LEGEND.get(text.get_text(),text.get_text()))
                text.set_fontsize(legend_size)
            lt=leg.get_title()
            lt.set_text({'num_inventors_z':'Inventor team size','wips_family_pub_count_z':'Patent-family coverage','Subtype':'Patent category','Legend':'','Clusters':'Technological cluster'}.get(lt.get_text(),lt.get_text()))
            lt.set_fontsize(legend_size)
            leg.get_frame().set_linewidth(.5)
            if name=='figure9b':
                labels=[t.get_text() for t in leg.get_texts()]
                fig.legend(leg.legend_handles,labels,loc='upper center',bbox_to_anchor=(.5,-.08),ncol=3,frameon=False,fontsize=legend_size)
                leg.remove()
        if name=='figure8':
            for text in ax.texts:text.set_fontsize(6.5*factor)
    if name not in ['figure1','figure9a','figure9b']:
        fig.tight_layout(pad=1.2)
    fig.canvas.draw();after=geometry(fig)
    assert before==after,(name,before,after)
    texts_after=[x.get_text() for x in fig.findobj(Text) if x.get_text()]
    forbidden=['cpc_cluster_dist','rca_y1','wips_family_pub_count','num_inventors_z','genai_confidence_raw','I_cpc2_z']
    assert not any(w in t for t in texts_after for w in forbidden)
    box='tight' if name in ['figure3a','figure3b','figure9b'] else None
    fig.savefig(D/f'{name}.pdf',bbox_inches=box)
    fig.savefig(D/f'{name}_600dpi.png',dpi=600,bbox_inches=box)
    fig.savefig(D/f'{name}_preview.png',dpi=120,bbox_inches='tight')
    with (D/f'{name}_styled.pkl').open('wb') as f:pickle.dump(fig,f)
    records.append({'panel':name,'data_and_colour_sha256_before':before,'data_and_colour_sha256_after':after,'unchanged':True,'texts_before':texts_before,'texts_after':texts_after})
    (D/'text_and_geometry_audit.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
    plt.close('all');print('STYLED',name,flush=True)

with threadpool_limits(limits=4):
    cols=['year','country_code','appl_id','embedding_row','genai_pred','genai_subtype_pred','num_inventors','wips_family_pub_count','cpc_main_norm','genai_confidence_raw']
    pred=pd.read_parquet(cache/'df_pred_regenerated.parquet',columns=cols)
    env={'df_pred':pred.copy()}
    for i,name in [(133,'figure2'),(134,'figure3a'),(135,'figure3b')]:execute(i,env);save(name)
    lab=pd.read_parquet(R/'02_figures/08_original_array_replay/original_array_distances.parquet')
    execute(172,{'df_pred':lab.copy()});save('figure4')
    env={'df_final':pd.read_parquet(R/'02_figures/09_original_regression_replay/original_numeric_input.parquet'),'np':np,'pd':pd}
    for i,name in [(287,'figure5'),(298,'figure6a'),(294,'figure6b')]:execute(i,env);save(name)
    p=pred.copy();p['cpc_code']=p.cpc_main_norm
    dist=pd.read_parquet(cache/'recomputed_september_cpc_distances.parquet')
    p=p.merge(dist[['year','country_code','cpc_code','cpc_cluster_dist_cos']],on=['year','country_code','cpc_code'],how='left',validate='many_to_one').reset_index(drop=True)
    env={'df_pred':p,'np':np,'pd':pd,'thr_hi':.6,'thr_lo':.4}
    for i,name in [(316,'figure7a'),(318,'figure7b')]:execute(i,env);save(name)
    summary=pd.read_csv(R/'02_figures/12_complete_replot_600dpi/figure8_fresh_core_counts.csv',index_col=0)
    execute(263,{'df_summary':summary,'np':np,'pd':pd});save('figure8')
    pred['cluster_id_k']=lab.cluster_id_k.to_numpy()
    z=np.load(R/'02_figures/10_original_tsne_replay/original_code_coordinates.npz')
    t=ast.parse(''.join(nb['cells'][142]['source']))
    names=next(list(ast.literal_eval(n.value)) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='category_desc' for v in n.targets))
    env={'df_pred':pred.copy(),'np':np,'pd':pd,'Y_patent':z['Y_patent'],'Y_cat':z['Y_cat'],'category_names':names,'X_all':np.load(S/'02_data/usb_import_20261108/X_all_embeddings.npy',mmap_mode='r')}
    execute(235,env);save('figure1')
    t=ast.parse(''.join(nb['cells'][233]['source']).replace('plt.show()',''))
    start=next(n.lineno for n in t.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='cn_mask' for v in n.targets))
    t.body=[n for n in t.body if isinstance(n,(ast.Import,ast.ImportFrom)) or n.lineno>=start]
    execute(233,env,t);save('figure9a')
    xy=np.load(R/'02_figures/12_complete_replot_600dpi/period_coordinates_without_anchors.npy')
    env={'df_pred':pred.copy(),'np':np,'pd':pd,'X_tsne':xy,'vis_df':pd.DataFrame({'tSNE1':xy[:,0],'tSNE2':xy[:,1],'GenAI':pred.genai_pred.eq('GenAI').map({True:'GenAI',False:'Others'}).to_numpy()})}
    t=ast.parse(''.join(nb['cells'][189]['source']))
    cut=next(n.lineno for n in t.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='subplots')
    t.body=[n for n in t.body if isinstance(n,(ast.Import,ast.ImportFrom)) or (n.lineno<cut and not isinstance(n,ast.If) and not (isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='K' for v in n.targets)))]
    execute(189,env,t);env['df_pred']=pred.loc[env['plot_df'].index].copy()
    execute(197,env);save('figure9b')
print('ALL_PANELS_STYLED_WITHOUT_TSNE_OR_CLASSIFIER_RERUN',flush=True)
