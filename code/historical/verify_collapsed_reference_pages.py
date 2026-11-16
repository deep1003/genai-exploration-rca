from pathlib import Path
import json,re,time,unicodedata,urllib.request,urllib.parse
R=Path(__file__).resolve().parents[1];D=R/'07_reports/research_policy_20261116';D.mkdir(exist_ok=True)
text=(R/'all_nine_600dpi_20261116/main.tex').read_text()
refs=text.split(r'\section{References}\label{references}')[1].split(r'\end{document}')[0]
paragraphs=[re.sub(r'\s+',' ',p).strip() for p in refs.split('\n\n') if p.strip()]
article_ids={'123536','104765','121559','104395'}
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower()))
out=[]
for p in paragraphs:
    match=re.search(r'(\d{4,10})\.$',p)
    if not match or match[1] in article_ids:continue
    token=match[1]
    if token.startswith('2203') or ':' in p[p.rfind(' '):]:continue
    url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':p,'rows':5})
    record={'reference':p,'collapsed':token,'verified':False,'retrieved_url':url}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Manuscript-reference-format-audit/1.0'}),timeout=20) as response:
            data=json.load(response);record['http_status']=response.status
        for item in data['message']['items']:
            title=' '.join(item.get('title',[]));page=item.get('page','')
            if len(norm(title))>15 and norm(title) in norm(p) and re.sub(r'\D','',page)==token and re.search(r'\d\s*[-–]\s*\d',page):
                record.update({'verified':True,'pages':page,'doi':item.get('DOI'),'matched_title':title});break
    except Exception as e:record['error']=str(e)
    out.append(record);(D/'reference_page_checks.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
    print(token,record.get('pages','UNVERIFIED'),flush=True);time.sleep(.25)
print('VERIFIED',sum(r['verified'] for r in out),'OF',len(out),flush=True)
