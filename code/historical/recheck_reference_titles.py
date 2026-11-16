from pathlib import Path
import json,re,time,urllib.request,urllib.parse,unicodedata
R=Path(__file__).resolve().parents[1];p=R/'07_reports/research_policy_20261116/reference_page_checks.json';rows=json.loads(p.read_text())
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower()))
for r in rows:
    if r['verified']:continue
    title=re.split(r',\s*(?:19|20)\d{2}\.\s*',r['reference'],maxsplit=1)[1].split('. ')[0]
    url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.title':title,'rows':5})
    try:
        with urllib.request.urlopen(url,timeout=15) as response:data=json.load(response)
        r['title_query_url']=url;r['title_query_status']=200
        for item in data['message']['items']:
            matched=' '.join(item.get('title',[]));page=item.get('page','')
            if len(norm(matched))>15 and norm(matched) in norm(r['reference']) and re.sub(r'\D','',page)==r['collapsed'] and re.search(r'\d\s*[-–]\s*\d',page):
                r.update({'verified':True,'pages':page,'doi':item.get('DOI'),'matched_title':matched});break
    except Exception as e:r['title_query_error']=str(e)
    p.write_text(json.dumps(rows,indent=2,ensure_ascii=False));print(r['collapsed'],r.get('pages','UNVERIFIED'),flush=True);time.sleep(.3)
print('VERIFIED',sum(r['verified'] for r in rows),'OF',len(rows),flush=True)
