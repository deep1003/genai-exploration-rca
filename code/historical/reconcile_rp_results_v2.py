"""Approved result reconciliation and notes layout in a preserved new release."""
from pathlib import Path
import ast,csv,difflib,hashlib,io,json,pickle,re,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

R=Path(__file__).resolve().parents[1]
OLD='research_policy_20261116';NEW='research_policy_reconciled_20261116'
S=R/OLD;O=R/NEW;D=R/'07_reports'/NEW;D.mkdir(exist_ok=True)
if not O.exists():shutil.copytree(S,O)
changes=[]
def revise(text,old,new,reason,file):
    assert old in text,(file,old[:100])
    changes.append(dict(file=file,before=old,after=new,reason=reason))
    return text.replace(old,new)
def section_replace(text,start,end,new,reason,file):
    a=text.index(start);b=text.index(end,a)
    return revise(text,text[a:b],new+'\n\n',reason,file)

for name in ['main.tex','author_review.tex']:
    text=(S/name).read_text()
    text=revise(text,
        'First, the probability of attaining\nRCA is an inverted U-shaped function of exploration distance. Second,\nlarge inventor teams and broad international patent families weaken the\ndecline of the curve at long distance.',
        'First, the distance association depends on observation units and fixed effects. '
        'Second, recovered pooled models suggest moderation by inventor teams and patent families.',
        'Qualify abstract findings against the three re-estimated specifications',name)
    text=revise(text,'and 88.4 per cent of\nTransformer-related patents.',
        'among four sampled regions. Keyword-occurrence shares differ by technology.',
        'Do not describe keyword occurrences as patent shares in the abstract',name)
    text=revise(text,'distance and comparative advantage is inverted U-shaped and is moderated\nby inventor team size and patent family size.',
        'distance and comparative advantage depends on observation units and fixed effects. '
        'The recovered pooled models suggest moderation by inventor team size and patent family size.',
        'Align introduction with specification-dependent estimates',name)
    text=revise(text,'relation to date and extends the inverted U to the foundation-model era\nand to a country-level outcome.',
        'relation in the foundation-model era, while distinguishing cell-level and patent-level associations.',
        'Remove an unsupported general confirmation claim',name)
    method=r'''The re-estimated linear probability models distinguish equal-weight country--CPC--year
cells, patent--CPC rows with fixed effects, and the recovered pooled implementation
(Table 2). The cell specification is
\begin{equation}\label{eq:3}
\begin{aligned}
Y_{c,j,t+1}&=\alpha+\beta_1Y_{c,j,t}
+\beta_2 z(m_{1,c,j,t})+\beta_3 z(m_{2,c,j,t})\\
&\quad+\symbfit{\gamma}^{\prime}\symbfit{X}_{c,j,t}
+\delta_t+\theta_c+\phi_j+\varepsilon_{c,j,t},
\end{aligned}
\end{equation}
where $Y$ indicates RCA above one, $m_1$ is the cell mean of patent-level
exploration distance, and $m_2$ is the cell mean of its raw square.
Cell-level continuous regressors are standardized after aggregation and singleton
removal. Importantly, $m_2$ is not $m_1^2$: it also reflects within-cell dispersion.
The patent--CPC specification uses the corresponding row-level regressors.
Year, country and CPC effects are genuinely absorbed in both fixed-effects models.
Standard errors are clustered by country, with a finite-sample correction and
$t$ inference using the number of country clusters minus one degrees of freedom.
The pooled replay retains the recovered implementation's normal-reference inference;
its original \texttt{absorb} argument did not implement fixed effects.
Positive and negative coefficients on the two distance moments are therefore only
partial evidence relevant to H1, not proof of an interior inverted U in mean distance.
A turning point cannot be inferred from their standardized coefficient ratio alone.
The recovered interaction plots for H2a and H2b remain pooled-model illustrations;
Table 2 does not validate their robustness to genuine fixed effects.'''
    text=section_replace(text,'The baseline model is a linear probability model',
        'H3 is tested with a difference-in-differences',method,
        'Match equation, aggregation, standardization, fixed effects and inference to executed code',name)
    result=r'''The evidence for H1 is specification dependent (Table 2). In the equal-weight
country--CPC--year cell model, the standardized distance coefficient is 0.0465
($p=0.0155$) and the standardized mean squared-distance coefficient is
$-0.0406$ ($p=0.0336$), based on 78,615 cells and 60 country clusters.
These signs are consistent with a concave component, but do not establish an
interior inverted U in cell-mean distance because the second moment also captures
within-cell dispersion. In the patent--CPC fixed-effects model, the corresponding
coefficients are $-0.0322$ ($p=0.1234$) and 0.0204 ($p=0.2698$), based on
506,311 rows; neither supports the hypothesized curvature. The pooled replay
produces 0.1117 and $-0.1068$ (both $p<0.01$) for 510,673 rows, but does not
absorb fixed effects. Thus the recovered data do not establish an inverted U
that is robust to weighting and fixed-effects implementation.
Current RCA is positively associated with subsequent RCA in all three models:
its coefficient is 0.2793 in the cell model, 0.5325 in the row-level fixed-effects
model and 0.5253 in the pooled replay (all $p<0.01$).
Figure 5 retains the recovered pooled illustration rather than predictions from
the re-estimated cell model. Its historical turning-point interpretation is not
validated by Table 2.'''
    text=section_replace(text,'The estimates support H1.',r'\begin{figure}[htbp]',result,
        'Replace historical coefficients and turning-point claim with verified estimates and limits',name)
    control=r'''The control-variable associations also depend on specification. In the equal-cell
model, inventor team size (0.0148) and family publication count (0.0130) are
positive at the one per cent level, while inventor centrality is negative
($-0.0055$, $p=0.0414$). Forward citations are positive but do not reach the
five per cent threshold (0.0069, $p=0.0589$). In the row-level fixed-effects
model, backward citations are positive and claims are negative at the one per
cent level, whereas the distance terms are not significant. These conditional
associations do not support a general claim that scale is irrelevant or that
the forward-citation association is invariant to the observation unit.'''
    text=section_replace(text,'A second finding concerns scale.',r'\subsection{Complementary capabilities',control,
        'Correct control coefficients, significance and interpretation',name)
    text=revise(text,'The interaction estimates support H2a.',
        'The recovered pooled interaction estimates suggest H2a; their robustness to genuine fixed effects has not been established.',
        'Do not attribute pooled interaction findings to the new FE estimates',name)
    text=revise(text,'which supports H2b.',
        'which is consistent with H2b in the recovered pooled specification.',
        'Bound the H2b interpretation to the model actually plotted',name)
    text=revise(text,'The inverted U is\nrobust to the inclusion of three-way fixed effects, the full set of\ncontrols, and the interaction terms, which strengthens the generality of\nthe results of \\citet{ref31} and \\citet{ref18}, and it shows',
        'The distance association is sensitive to observation units and genuine fixed effects; '
        'it does not establish a robust inverted U extending the results of \\citet{ref31} and \\citet{ref18}. The measurement approach shows',
        'Reconcile discussion with the failed robustness claim',name)
    text=revise(text,'Third, the\nweak direct effects of scale variables support the view in the\ncomplexity literature \\citep{ref24,ref25} that comparative advantage in foundation-model AI depends on\nnetwork position and exploration calibration rather than on input\nquantity.',
        'Third, the specification-dependent control associations caution against interpreting '
        'the complexity literature \\citep{ref24,ref25} as evidence that input quantity is irrelevant '
        'to comparative advantage in foundation-model AI.',
        'Remove a scale interpretation contradicted by cell FE controls',name)
    text=revise(text,'advantage is an inverted U. The curve is moderated by inventor team size\nand international family size.',
        'advantage depends on observation units and fixed effects. '
        'The pooled moderation patterns remain suggestive, not fixed-effects-robust findings.',
        'Reconcile conclusion without changing unrelated findings',name)
    kw=r'''Keyword-occurrence shares provide a separate textual description. Among U.S. and
Chinese occurrences in Cluster 1, China accounts for 97.2 per cent of attention
mentions and 95.0 per cent of image-recognition mentions; the U.S. share of
embedding mentions is 37.8 per cent. In Cluster 4, Chinese shares are 88.4 per
cent for Transformer, 91.4 per cent for attention and 95.5 per cent for pre-training.
U.S. shares are 50.8 per cent for speech recognition and 39.6 per cent for
embedding (Table 4). These are mention counts in concatenated text fields, not
shares of distinct patents. Repeated mentions can contribute multiple counts,
and the archived keyword population is not explicitly restricted to GenAI or
RCA above one. The percentages describe textual emphasis, not patent ownership
or control over the corresponding technologies.'''
    text=section_replace(text,'Keyword-level shares\nsharpen the picture.',r'\setcounter{table}{2}',kw,
        'Correct the Table 4 measurement, denominator and substantive interpretation',name)
    text=revise(text,'The keyword-level division in Table 4 shows the\npattern of mutual dependence.',
        'The keyword-occurrence distribution in Table 4 describes differences in textual '
        'emphasis; it does not by itself establish technological control or mutual dependence.',
        'Do not infer strategic control from repeated textual mentions',name)
    text=revise(text,'These re-estimates differ from the historical numerical claims retained in the prose and do not replace the plotted pooled predictions in Figures 5 and 6.',
        'Figures 5 and 6 retain recovered pooled illustrations, not predictions from these fixed-effects models.',
        'Remove a resolved prose inconsistency from the table note',name)
    text=revise(text,'The inverted-U\nresults, however, show that advantage accrues to calibrated exploration\nrather than to volume, and the U.S. position in embedding and\ncross-modal niches, together with its still-leading share of the core\ninventor network, is calibrated positioning of exactly this kind.',
        'The re-estimates do not establish that calibrated exploration dominates volume. '
        'The different U.S. and Chinese positions remain descriptive evidence rather than '
        'a policy ranking implied by a robust inverted U.',
        'Remove a policy inference unsupported by Table 2',name)
    text=revise(text,'that co-evolution, and the inverted-U results indicate a limit to it,\nsince convergence at ever shorter exploration distance eventually crowds\nthe core.',
        'that co-evolution. Whether convergence eventually crowds the core remains '
        'a hypothesis rather than a robust implication of the re-estimates.',
        'Do not assert an unverified short-distance crowding effect',name)
    text=revise(text,'Because input quantities\nhave weak direct effects on comparative advantage, marginal spending on\nheadcount or patent volume is less productive than instruments that\nshape exploration calibration, such as support for moderate-distance and\ncross-domain recombination, and instruments that protect the\ncomplementary assets, namely large teams and international patent\nfamilies, which make distant exploration sustainable.',
        'The specification-dependent estimates do not identify an optimal exploration '
        'distance or show that spending on headcount is less productive than support for '
        'recombination. Policies addressing teams, family coverage and exploration '
        'should therefore be evaluated jointly rather than ranked from these associations.',
        'Align policy implications with significant scale controls and model dependence',name)
    text=section_replace(text,"The pattern is consistent. China's specialisation",r'\section{Discussion}',
        'Taken together, the archived application counts and keyword-occurrence distributions '
        'suggest different national profiles. Chinese shares are high in the large application '
        'cluster and in attention, pre-training and Transformer mentions; U.S. occurrence shares '
        'are relatively higher for embedding and speech recognition. These measures use '
        'different populations and counting units and should not be combined into a patent-volume '
        'or technological-control ranking. They motivate, rather than establish, an interpretation '
        'of convergence and diversification.',
        'Remove conflation of keyword frequencies, patent volumes and technological control',name)
    # Replace long provenance notes with concise measurement notes and explicit separation.
    text=re.sub(r'\\par\\smallskip\\raggedright\\footnotesize\\emph\{Notes:\} .*?(?=\n\\end\{table\})',lambda m:
        r'\par\vspace{\baselineskip}\noindent\raggedright\footnotesize\emph{Notes:} '
        r'Outcome: RCA above one at $t+1$. Cell regressors are means of distance and raw squared distance, standardized separately; $E[d^2]\ne E[d]^2$. '
        r'FE models absorb year, country and CPC effects and remove singletons; pooled OLS does not. Country-clustered SEs are in parentheses. '
        r'FE inference uses CR1 and $t_{G-1}$; pooled inference uses the normal reference. $R^2$ is within-model for FE. '
        r'$^{***}p<0.01$, $^{**}p<0.05$, $^{*}p<0.10$. Recovered-data estimates are not an exact historical replication.',text,flags=re.S)
    text=re.sub(r'\\emph\{Notes:\} Shares are recalculated from archived application counts.*?(?=\n\n)',lambda m:
        r'\par\vspace{\baselineskip}\noindent\emph{Notes:} Archived application counts with observed RCA above one; LLM records are used where available, otherwise GenAI. '
        r'The denominator is US, CN, KR and EU; the last column denotes KR plus EU. Historical cluster labels are retained.',text,flags=re.S)
    text=re.sub(r'\\emph\{Notes:\} Shares are recalculated from archived keyword-occurrence counts.*?(?=\n\n)',lambda m:
        r'\par\vspace{\baselineskip}\noindent\emph{Notes:} Shares of US plus CN keyword occurrences in concatenated text, not distinct patents. '
        r'Repeated mentions count separately. The archived population is not explicitly restricted to GenAI or RCA above one; historical cluster labels are retained.',text,flags=re.S)
    text=text.replace(r'\emph{Note: descriptive statistics are reported in the appendix.}',
        r'\par\vspace{\baselineskip}\noindent\emph{Notes:} Expected associations are theoretical predictions, not estimated effects.')
    # Preserve data descriptions, separating them from brief figure titles.
    titles={1:'Technology space of GenAI patents.',2:'Annual GenAI patent applications, 2000'+r'\textendash{}'+'2023.',
        3:'Inputs per GenAI application by year.',4:'Mean technological exploration distance of GenAI patents by year.',
        5:'Recovered pooled illustration of exploration distance and subsequent RCA.',
        6:'Moderation of the distance-RCA relation.',7:'The Transformer as a structural break.',
        8:'National shares of core inventors in the GenAI collaboration network.',9:'Technology space of the United States and China.'}
    notes={
        1:'PatentSBERTa embeddings projected with t-SNE and coloured by k-means cluster. Historical semantic labels are not a verified crosswalk to the regenerated partition.',
        2:'Global country mean, United States and China. Shading marks 2017; recent filing counts are affected by publication lags.',
        3:'(a) Mean inventors. (b) Mean international family publications. The single legend applies to both panels; shading is the global 95 per cent confidence band.',
        4:'Observation-weighted global mean with 95 per cent confidence band, United States and China. Distance is measured from each patent embedding to its cluster centroid.',
        5:'Unchanged recovered pooled curve, not a prediction from the cell fixed-effects model. Linear-model predictions can lie outside the unit interval; no interior turning point is validated here.',
        6:'Recovered pooled predictions at low, mean and high moderator values. (a) Inventor team size. (b) Family publication count. These curves are not fixed-effects re-estimates.',
        7:'(a) Annual mean distance with 95 per cent confidence bands; GenAI score at least 0.6, non-GenAI at most 0.4. (b) Recovered event-study coefficients and 95 per cent intervals around 2017; the historical reference-year implementation is not revalidated here.',
        8:'Five-year periods; core membership from a two-block Bernoulli stochastic block model. Bars show the United States, China and Korea; grey denotes the full core.',
        9:'(a) PatentSBERTa t-SNE projection with U.S. and Chinese patents and LLM anchors; Transformer and Universal Transformer patents are marked. (b) Chinese LLM patents by five-year period in the same projection.'}
    for n in range(1,10):
        pattern=r'\\caption\{.*?\}\\label\{fig:'+str(n)+r'\}'
        # Restrict to one figure environment to avoid consuming a prior caption.
        env=re.search(r'\\begin\{figure\}.*?\\label\{fig:'+str(n)+r'\}.*?\\end\{figure\}',text,re.S)
        # The first match can start at an earlier figure; target caption via tempered braces-to-label span.
        matches=list(re.finditer(r'\\caption\{(?:(?!\\caption\{).)*?\}\\label\{fig:'+str(n)+r'\}',text,re.S))
        assert len(matches)==1,(n,len(matches))
        m=matches[0];replacement='\\caption{'+titles[n]+'}\\label{fig:'+str(n)+'}\n\\figurenotes{'+notes[n]+'}'
        text=revise(text,m[0],replacement,'Separate concise caption and spaced Notes',name)
    text=revise(text,'\\caption{Keyword-level U.S. and Chinese patent shares within\nClusters 1 and 4, per cent.}',
        '\\caption{U.S. and Chinese shares of keyword occurrences in Clusters 1 and 4, per cent.}',
        'Correct Table 4 caption to the actual counting unit',name)
    text=text.replace(r'\journal{Research Policy}',r'\newcommand{\figurenotes}[1]{\par\vspace{\baselineskip}\noindent\begin{minipage}{\linewidth}\small\emph{Notes:} #1\end{minipage}}'+'\n'+r'\journal{Research Policy}')
    text=text.replace(OLD+'/figures/',NEW+'/figures/')
    abstract=text.split(r'\begin{abstract}')[1].split(r'\end{abstract}')[0]
    assert len(abstract.split())<=250,len(abstract.split())
    (O/name).write_text(text)
    (D/(name+'.diff')).write_text(''.join(difflib.unified_diff((S/name).read_text().splitlines(True),text.splitlines(True),fromfile=OLD+'/'+name,tofile=NEW+'/'+name)))

# Update separate captions to the authoritative new source.
text=(O/'main.tex').read_text()
(O/'figure_captions.tex').write_text('\n\n'.join(m[0] for m in re.finditer(r'\\caption\{(?:(?!\\caption\{).)*?\}\\label\{fig:\d+\}\n\\figurenotes\{[^\n]*\}',text,re.S)))
with (D/'changes.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['file','before','after','reason']);w.writeheader();w.writerows(changes)
(D/'changes.json').write_text(json.dumps(changes,indent=2))

# Legend-only changes from the saved styled Matplotlib objects.
p=R/'06_scripts/restyle_nature_figures_20261116.py';tree=ast.parse(p.read_text())
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='geometry']
import numpy as np
env={'hashlib':hashlib,'np':np};exec(compile(ast.Module(body=functions,type_ignores=[]),'geometry','exec'),env)
audit=[]
for panel in ['figure3b','figure4']:
    with (R/f'02_figures/13_nature_labels_20261116/{panel}_styled.pkl').open('rb') as f:fig=pickle.load(f)
    for ax in fig.axes:ax.set_title('')
    fig.canvas.draw();box=fig.get_tightbbox(fig.canvas.get_renderer()) if panel=='figure3b' else None
    before=env['geometry'](fig);positions=[ax.get_position().bounds for ax in fig.axes]
    for ax in fig.axes:
        leg=ax.get_legend()
        if panel=='figure3b':leg.remove()
        else:
            leg.set_loc('upper right');leg.set_bbox_to_anchor((1,1),transform=ax.transAxes)
            leg.set_frame_on(True);leg.get_frame().set_facecolor('white');leg.get_frame().set_alpha(.95)
    assert before==env['geometry'](fig)
    assert positions==[ax.get_position().bounds for ax in fig.axes]
    dest=O/'figures'/(panel+'.pdf');fig.savefig(dest,bbox_inches=box)
    fig.savefig(D/(panel+'_600dpi.png'),dpi=600,bbox_inches=box)
    plt.close(fig);audit.append({'panel':panel,'data_colors_limits_unchanged':True,'axes_positions_unchanged':True,'geometry_sha256':before})
shutil.copy2(O/'figures/figure4.pdf',O/'figures/Figure_04.pdf')
t=ast.parse((R/'06_scripts/package_all_nine_replots.py').read_text());t.body=[n for n in t.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) and not (isinstance(n,ast.ImportFrom) and n.module=='pypdf._configuration')]
e={};exec(compile(t,'composite','exec'),e)
pdfmetrics.registerFont(TTFont('PanelArialBold','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
def annotate(page,labels):
    b=io.BytesIO();c=canvas.Canvas(b,pagesize=(float(page.mediabox.width),float(page.mediabox.height)),initialFontName='PanelArialBold');c.setFont('PanelArialBold',12)
    for label,x,y in labels:c.drawString(x,y,label)
    c.save();b.seek(0);page.merge_page(PdfReader(b).pages[0])
e['annotate']=annotate;e['composite']([O/'figures/figure3a.pdf',O/'figures/figure3b.pdf'],O/'figures/Figure_03.pdf')
(D/'figure_legend_audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps({'release':NEW,'changes':len(changes),'abstract_words':len(abstract.split()),'figure_audit':audit},indent=2))
