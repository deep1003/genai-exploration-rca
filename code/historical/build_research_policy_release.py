"""Publisher-template formatting and bounded proofreading; preserve original evidence."""
from pathlib import Path
import ast,csv,difflib,hashlib,json,re,shutil,zipfile
from pypdf._configuration import overwrite_configuration
overwrite_configuration(stream_parsing_work_maximum_count=100_000_000)
R=Path(__file__).resolve().parents[1];D=R/'07_reports/research_policy_20261116';D.mkdir(exist_ok=True)
name='research_policy_20261116';out=R/name;(out/'figures').mkdir(parents=True,exist_ok=True)
original=(R/'nature_math_verified_20261116/main.tex').read_text();text=original;changes=[]
def change(old,new,reason):
    global text
    assert old in text,old
    changes.append({'before':old,'after':new,'count':text.count(old),'reason':reason})
    text=text.replace(old,new)

# Dates in the prose are distinct from reference pagination and article IDs.
ref_marker=r'\section{References}\label{references}'
prose=text.split(ref_marker)[0]
for match in sorted(set(re.findall(r'(?<!\d)((?:19|20)\d{2})((?:19|20)\d{2})(?!\d)',prose))):
    a,b=match
    if 0<int(b)-int(a)<=30:change(a+b,a+r'\textendash{}'+b,'Restore a missing year-range separator; Word XML contains the same collapsed form')
for old,new in [('coreperiphery','core-periphery'),('universityindustry','university-industry'),('U.S.China','U.S.-China'),('distanceRCA','distance-RCA'),('Appendix .','Appendix.')]:
    if old in text:change(old,new,'Restore a missing connector or remove stray punctuation spacing')
for a,b in set(re.findall(r'(?<!\d)((?:19|20)\d{2})-((?:19|20)\d{2})(?!\d)',text.split(ref_marker)[0])):
    change(a+'-'+b,a+r'\textendash{}'+b,'Use a consistent en dash for an existing year range')
checks=json.loads((D/'reference_page_checks.json').read_text())
for item in checks:
    if item['verified']:
        token=item['collapsed'];pages=re.sub(r'\s*[-–]\s*',lambda m:r'\textendash{}',item['pages'])
        old=item['reference'];raw_refs=text.split(ref_marker)[1].split(r'\end{document}')[0]
        for paragraph in raw_refs.split('\n\n'):
            if re.sub(r'\s+',' ',paragraph).strip()==old:
                before=paragraph;after=re.sub(re.escape(token)+r'\.$',lambda m:pages+'.',before)
                change(before,after,'Restore pagination only where Crossref title and concatenated page digits both match')
                break

# Preserve punctuation but place it at the end of each displayed equation.
equations=[]
def equation(match):
    inner=match[1].strip();punct=match[2]
    k=len(equations)+1
    if inner.endswith(r'\end{aligned}'):
        inner=inner.removesuffix(r'\end{aligned}').rstrip()+punct+'\n'+r'\end{aligned}'
    else:inner+=punct
    result='\\begin{equation}\\label{eq:'+str(k)+'}\n'+inner+'\n\\end{equation}'
    equations.append({'before':match[0],'after':result,'count':1,'reason':'Native editable equation with consecutive numbering and in-equation punctuation'})
    return result
text=re.sub(r'\\\[(.*?)\\\]([.,]?)',equation,text,flags=re.S);changes.extend(equations)
for old,new in [(r'\mathbf{e}',r'\symbfit{e}'),(r'\mathbf{X}',r'\symbfit{X}'),(r'\boldsymbol{\mu}',r'\symbfit{\mu}'),(r'\boldsymbol{\gamma}',r'\symbfit{\gamma}')]:
    if old in text:change(old,new,'Use intrinsic OpenType bold-italic mathematical glyphs rather than an unavailable bold face')

# Extract the manuscript content, keeping the exact abstract until the user approves a reduction.
title=re.search(r'\\textbf\{(Technological exploration.*?)\}\s*\n\nOne-Sun',text,re.S)[1]
abstract=text.split(r'\section{Abstract}\label{abstract}')[1].split(r'\textbf{Keywords:}')[0].strip()
approval=D/'approved_abstract.txt'
if (D/'approved_abstract.json').exists():
    revised=abstract.replace('This study examines how','We examine how').replace('the two countries differ in the way they explore the technological\nspace.','their technological exploration differs.').replace('economy, and we test','economy, and test')
    assert len(revised.split())<=250,len(revised.split())
    approval.write_text(revised)
if approval.exists():
    revised=approval.read_text().strip();assert len(revised.split())<=250
    changes.append({'before':abstract,'after':revised,'count':1,'reason':'User-approved minimum reduction to the journal 250-word abstract limit'})
    abstract=revised
keywords=text.split(r'\textbf{Keywords:}')[1].split(r'\textbf{JEL classification:}')[0].strip()
jel=text.split(r'\textbf{JEL classification:}')[1].split(r'\section{1. Introduction}')[0].strip()
body=r'\section{1. Introduction}'+text.split(r'\section{1. Introduction}',1)[1]
ack_marker=r'\section{Acknowledgements}\label{acknowledgements}'
ack_block=body.split(ack_marker)[1].split(r'\section{Data availability}')[0]
ack=ack_block.split(r'\textbf{Funding:}')[0].strip()
funding=ack_block.split(r'\textbf{Funding:}')[1].strip()
body=body.replace(ack_marker+ack_block,'')
reftext=body.split(ref_marker)[1].split(r'\end{document}')[0].strip()
body=body.split(ref_marker)[0].strip()
refs=[p.strip() for p in reftext.split('\n\n') if p.strip()]

# Retain complete reference text, using numeric citations as shown in the live journal guide.
entries=[];aliases={}
for index,p in enumerate(refs):
    flat=re.sub(r'\s+',' ',p)
    m=re.search(r',\s*((?:19|20)\d{2})\.',flat);assert m,flat
    year=m[1];authorpart=flat[:m.start()]
    surnames=re.findall(r'(?:^|,\s+)([A-ZÀ-ÖØ-Þ][\w\-ÅåøæØÆ]+),\s*[A-Z]',authorpart)
    if 'de Wilde,' in authorpart:surnames.append('de Wilde')
    if not surnames:alias=authorpart.strip().rstrip(',')
    elif len(surnames)==1:alias=surnames[0]
    elif len(surnames)==2 and 'et al.' not in authorpart:alias=' and '.join(surnames)
    else:alias=surnames[0]+' et al.'
    key='ref'+str(index+1).zfill(2)
    entries.append({'key':key,'alias':alias,'year':year,'reference':p})
    aliases[(alias,year)]=key
used=[];citation_changes=[]
def citekey(alias,year):return aliases.get((re.sub(r'\s+',' ',alias).strip(),year))
for (alias,year),key in sorted(aliases.items(),key=lambda kv:-len(kv[0][0])):
    pattern=r'(?<![\w])'+r'\s+'.join(re.escape(w) for w in alias.split())+r"(?P<poss>'s)?\s*\("+year+r'\)'
    def narrative(m,key=key,alias=alias):
        replacement=(alias+"'s \\citep{"+key+'}') if m['poss'] else r'\citet{'+key+'}'
        citation_changes.append({'before':m[0],'after':replacement,'count':1,'reason':'Journal numeric reference formatting; original source retained'})
        used.append(key);return replacement
    body=re.sub(pattern,narrative,body)
def parenthetical(m):
    content=re.sub(r'\s+',' ',m[1]).strip();keys=[];prefix=''
    if content.startswith('see also '):prefix='see also ';content=content[len(prefix):]
    for part in content.split(';'):
        found=re.fullmatch(r'(.+?),\s*((?:(?:19|20)\d{2})(?:,\s*(?:19|20)\d{2})*)',part.strip())
        if not found:return m[0]
        for year in re.findall(r'(?:19|20)\d{2}',found[2]):
            key=citekey(found[1],year)
            if not key:return m[0]
            keys.append(key)
    if not keys:return m[0]
    replacement=r'\citep{'+','.join(keys)+'}'
    if prefix:replacement='('+prefix+replacement+')'
    citation_changes.append({'before':m[0],'after':replacement,'count':1,'reason':'Journal numeric reference formatting; all cited works preserved'})
    used.extend(keys);return replacement
body=re.sub(r'\(([^()]*\b(?:19|20)\d{2}[^()]*)\)',parenthetical,body)
unmapped=re.findall(r'\([^()]*\b(?:19|20)\d{2}[^()]*\)',body)
changes.extend(citation_changes)
# Actual order of appearance, not the order in which substitution passes ran.
used=[]
for c in re.findall(r'\\cite[pt]\{([^}]+)\}',body):
    for key in c.split(','):
        if key not in used:used.append(key)
unreferenced=[r['key'] for r in entries if r['key'] not in used]
order=used+unreferenced;bykey={r['key']:r for r in entries}
bibliography='\\begin{thebibliography}{99}\n'+''.join('\\bibitem['+bykey[k]['alias']+'('+bykey[k]['year']+')]'+'{'+k+'}\n'+bykey[k]['reference']+'\n\n' for k in order)+'\\end{thebibliography}\n'
(D/'reference_mapping.json').write_text(json.dumps({'entries':entries,'unmapped_parentheticals':unmapped,'uncited_keys':unreferenced},indent=2,ensure_ascii=False))
bibliography=bibliography.replace('\\begin{thebibliography}{99}','\\begin{thebibliography}{99}\\raggedright')

# Automatic section numbers and publisher caption commands; caption wording is retained.
body=re.sub(r'\\(subsection|section)\{\d+(?:\.\d+)*\.?(?:\s+)',lambda m:'\\'+m[1]+'{',body)
captions=[]
for i in range(1,10):
    pattern=r'\\includegraphics\[[^\n]*\]\{[^\n]*image'+str(i)+r'\.png\}\s*\n\s*\\textbf\{Fig\. '+str(i)+r'\. (.*?)\}\s*(?=\n\n)'
    match=re.search(pattern,body,re.S);assert match,('figure',i)
    caption=match[1];captions.append({'figure':i,'text':caption})
    replacement='\\begin{figure}['+('p' if i==7 else 'htbp')+']\n\\centering\n'+r'\includegraphics[width=\linewidth,height=.82\textheight,keepaspectratio]{'+name+f'/figures/Figure_{i:02d}.pdf'+'}\n\\caption{'+caption+'}\\label{fig:'+str(i)+'}\n\\end{figure}'
    body=body[:match.start()]+replacement+body[match.end():]
table_captions=[]
for n in [1,3,4]:
    pattern=r'\\textbf\{Table '+str(n)+r'\. (.*?)\}\s*(?=\n\n)'
    match=re.search(pattern,body,re.S);assert match,('table',n)
    table_captions.append((n,match[1]))
    replacement='\\setcounter{table}{'+str(n-1)+'}'
    body=body[:match.start()]+replacement+body[match.end():]
body=body.replace(r'\begin{longtable}',r'\small'+'\n'+r'\begin{longtable}')
body=body.replace(r'\def\LTcaptype{none} % do not increment counter','')
table_iter=iter(table_captions)
def insert_table_caption(m):
    n,caption=next(table_iter)
    return m[0].replace(r'\toprule','\\caption{'+caption+'}\\label{tab:'+str(n)+'}\\\\\n'+r'\toprule')
body=re.sub(r'\\begin\{longtable\}.*?\n\\toprule',insert_table_caption,body,flags=re.S)
def repeat_table_header(m):
    block=m[0]
    head=re.search(r'\\endlastfoot\s*(.*?)\\\\',block,re.S)
    assert head
    header=head[1]+r'\\'
    old=r'\toprule\noalign{}'+'\n'+r'\endhead'
    new=r'\toprule\noalign{}'+'\n'+header+'\n'+r'\midrule'+'\n'+r'\endfirsthead'+'\n'+r'\toprule'+'\n'+header+'\n'+r'\midrule'+'\n'+r'\endhead'
    block=block.replace(old,new,1)
    start=block.index(r'\endlastfoot')+len(r'\endlastfoot')
    after=block[start:];after=after.replace(header,'',1)
    return block[:start]+after
body=re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}',repeat_table_header,body,flags=re.S)

from insert_recovered_tables import insert_tables
body=insert_tables(body,D/'table_recovery')
preamble=r'''% Elsevier elsarticle standard submission template, numeric citation variant.
\documentclass[preprint,12pt,numbers,sort&compress]{elsarticle}
\usepackage{fontspec,unicode-math}
\setmainfont{texgyretermes-regular.otf}[BoldFont=texgyretermes-bold.otf,ItalicFont=texgyretermes-italic.otf,BoldItalicFont=texgyretermes-bolditalic.otf]
\setmathfont{texgyretermes-math.otf}
\usepackage[a4paper,margin=25mm]{geometry}
\usepackage{amsmath,graphicx,longtable,booktabs,array,calc,caption,etoolbox}
\usepackage{hyperref,xurl,microtype}
\hypersetup{hidelinks}
\pdfstringdefDisableCommands{\def\corref#1{}\def\fnref#1{}}
\captionsetup{font=small,labelfont=bf}
\newcounter{none}
\setlength{\emergencystretch}{3em}
\setlength{\LTcapwidth}{\linewidth}
\journal{Research Policy}
\raggedbottom
\begin{document}
'''
authors=r'''\author[inst1]{One-Sun Cho\corref{cor1}\fnref{equal}}
\ead{onesun@stepi.re.kr}
\author[inst2]{Youngsam Chun\fnref{equal}}
\affiliation[inst1]{organization={Science and Technology Policy Institute (STEPI)},addressline={370 Sicheong-daero},city={Sejong},postcode={30147},country={Republic of Korea}}
\affiliation[inst2]{organization={Frontier AI Lab, KT},addressline={151 Taebong-ro, Seocho-gu},city={Seoul},postcode={06763},country={Republic of Korea}}
\cortext[cor1]{Corresponding author.}
\fntext[equal]{These authors contributed equally to this work.}
'''
def front(include_authors):
    return '\\begin{frontmatter}\n\\title{'+title+'}\n'+(authors if include_authors else '')+'\\begin{abstract}\n'+abstract+'\n\\end{abstract}\n\\begin{keyword}\n'+keywords.replace(';',r'\sep')+'\n\\JEL '+jel+'\n\\end{keyword}\n\\end{frontmatter}\n'
main=preamble+front(False)+body+'\n'+bibliography+r'\end{document}'+'\n'
(out/'main.tex').write_text(main)
full=preamble+front(True)+body+'\n\\section*{Acknowledgements}\n'+ack+'\n\\section*{Funding}\n'+funding+'\n'+bibliography+r'\end{document}'+'\n'
(out/'author_review.tex').write_text(full)
titlepage=preamble+'\\begin{frontmatter}\n\\title{'+title+'}\n'+authors+'\\end{frontmatter}\n\\section*{Acknowledgements}\n'+ack+'\n\\section*{Funding}\n'+funding+'\n\\end{document}\n'
(out/'title_page.tex').write_text(titlepage)
(out/'figure_captions.tex').write_text(''.join('\\textbf{Fig. '+str(c['figure'])+'.} '+c['text']+'\n\n' for c in captions))
(D/'proofreading_changes.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False))
with (D/'proofreading_changes.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['before','after','count','reason']);w.writeheader();w.writerows(changes)
(D/'formatting.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),main.splitlines(True),fromfile='preserved_original',tofile=name+'/main.tex')))

# Composite comparison figures plus every native panel as separate editable vector artwork.
t=ast.parse((R/'06_scripts/package_all_nine_replots.py').read_text());t.body=[n for n in t.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
env={};exec(compile(t,'packaging','exec'),env)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader
import io
pdfmetrics.registerFont(TTFont('PanelArialBold','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
def embedded_panel_labels(page,labels):
    buffer=io.BytesIO();c=canvas.Canvas(buffer,pagesize=(float(page.mediabox.width),float(page.mediabox.height)),initialFontName='PanelArialBold')
    c.setFont('PanelArialBold',12)
    for label,x,y in labels:c.drawString(x,y,label)
    c.save();buffer.seek(0);page.merge_page(PdfReader(buffer).pages[0])
env['annotate']=embedded_panel_labels
font_marker=D/'embedded_panel_fonts.json'
P=R/'02_figures/14_research_policy_20261116'
groups={1:['figure1'],2:['figure2'],3:['figure3a','figure3b'],4:['figure4'],5:['figure5'],6:['figure6a','figure6b'],7:['figure7a','figure7b'],8:['figure8'],9:['figure9a','figure9b']}
for i,parts in groups.items():
    target=out/f'figures/Figure_{i:02d}.pdf'
    if not target.exists() or (len(parts)>1 and not font_marker.exists()):
        if len(parts)==1:shutil.copy2(P/(parts[0]+'.pdf'),target)
        else:env['composite']([P/(p+'.pdf') for p in parts],target,vertical=i in [7,9])
    for panel in parts:shutil.copy2(P/(panel+'.pdf'),out/'figures'/(panel+'.pdf'))
    print('RP_FIGURE',i,flush=True)
font_marker.write_text(json.dumps({'panel_labels':'Embedded Arial Bold TrueType; no unembedded standard Helvetica','separate_native_panels':13},indent=2))
shutil.copy2('/usr/local/texlive/2026/texmf-dist/tex/latex/elsarticle/elsarticle.cls',out/'elsarticle.cls')
shutil.copy2('/usr/local/texlive/2026/texmf-dist/doc/latex/elsarticle/elsarticle-template-num.tex',D/'official_elsarticle-template-num.tex')
shutil.copy2('/Users/deep1003/Downloads/조원선_박사님_01 (6).zip',D/'before_update_source.zip')
status={'abstract_words':len(abstract.split()),'abstract_limit':250,'references':len(entries),'citation_instances':len(citation_changes),'unmapped_citation_contexts':unmapped,'uncited_reference_keys':unreferenced,'display_equations':len(equations),'figures':9,'tables_completed':[1,2,3,4],'table2':'source-data re-estimates; not exact historical recovery','tables3_4':'archived integer counts with explicit population notes','anonymous_main':True,'separate_title_page':True}
(D/'status.json').write_text(json.dumps(status,indent=2))
print(json.dumps(status,indent=2),flush=True)
