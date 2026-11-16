"""Audit every Word figure; high resolution alone is not acceptance."""
from pathlib import Path
import json,csv,zipfile,hashlib,re
from lxml import etree as E
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
D=R/'07_reports/figure_by_figure_qa_20261115';D.mkdir(exist_ok=True)
master=R/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx'
with zipfile.ZipFile(master) as z:
    xml=E.fromstring(z.read('word/document.xml'))
    rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
    relmap={r.get('Id'):Path(r.get('Target')).name for r in rels}
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
widths={}
for p in xml.xpath('//wp:inline | //wp:anchor',namespaces=ns):
    blips=p.xpath('.//a:blip/@r:embed',namespaces=ns);extent=p.find('wp:extent',ns)
    if blips and extent is not None:widths[relmap[blips[0]]]=int(extent.get('cx'))/914400
base=R/'02_figures'
candidates={
1:base/'10_original_tsne_replay/figure1_600dpi.png',
2:base/'04_notebook_replay_600dpi/figure2_da3bbde622_600dpi.png',
3:base/'11_original_inputs_replay/figure3_candidate_600dpi.png',
4:base/'08_original_array_replay/figure4_600dpi.png',
5:base/'09_original_regression_replay/figure5_candidate_600dpi.png',
6:None,
7:base/'06_icloud_acquired/event_study_overlay_GenAI_vs_NonGenAI.png',
8:base/'03_regeneration_600dpi/figure8_printed_values/figure8_printed_values_600dpi.png',
9:base/'10_original_tsne_replay/figure9a_600dpi.png'}
reasons={
1:'Cluster 1/5 numbering and scatter geometry differ. Do not relabel or rotate to manufacture a match.',
2:'The original 2017 shaded band is absent from the replay; historical subtype cohort equivalence is not certified.',
3:'Early-year inventor means and family-publication curves/confidence bands visibly differ from the original.',
4:'Passed source-image-precision QA: original array and metadata identities, three 24-year series and world CI against archived SVG; finite-precision differences are explicitly recorded, not claimed to be bitwise zero.',
5:'Historical fingerprint failed: replay n=510673 versus original n=509665; coefficients differ. Candidate rejected.',
6:'Not rendered from a certified historical state: the upstream regression fingerprint failed. Original two-panel image retained.',
7:'The downloaded 600-dpi event-study overlay is a different version and is not the complete original two-panel Figure 7.',
8:'Candidate uses one-decimal labels transcribed from the image, not the recovered full-precision core counts; unsuitable for exact replacement.',
9:'Only panel (a) has a replay candidate, with changed cluster/scatter layout; original panel (b) has not been reproduced.'}
rows=[]
for i in range(1,10):
    original=base/f'00_embedded_originals/image{i}.png';candidate=candidates[i]
    with Image.open(original) as im:osize=list(im.size)
    csize=[];dpi=[];effective=None;metadata600=False
    if candidate is not None and candidate.exists():
        with Image.open(candidate) as im:
            csize=list(im.size);dpi=list(im.info.get('dpi',()))
            effective=csize[0]/widths[f'image{i}.png'];metadata600=bool(dpi and min(dpi)>=599.9)
    high=bool(effective is not None and effective>=600)
    row={'figure':i,'original_path':str(original),'candidate_path':str(candidate or ''),'original_pixels':osize,'candidate_pixels':csize,'word_width_inches':widths[f'image{i}.png'],'candidate_effective_dpi':effective,'candidate_dpi_metadata':dpi,'effective_dpi_at_least_600':high,'source_dpi_metadata_600':metadata600,'original_match':'source_image_precision_pass' if i==4 else 'not_certified','decision':'retain_verified_replacement' if i==4 else 'retain_original','reason':reasons[i]}
    rows.append(row)
    sheet=Image.new('RGB',(1880,800),'#eeeeee');draw=ImageDraw.Draw(sheet)
    draw.text((20,12),f'Figure {i} | '+row['decision'],fill='black')
    for col,p,label in [(0,original,'WORD ORIGINAL'),(1,candidate,'CANDIDATE (not automatically accepted)')]:
        draw.text((20+col*940,40),label,fill='black')
        if p is not None and p.exists():
            with Image.open(p) as im:
                im=im.convert('RGB');im.thumbnail((900,700));sheet.paste(im,(20+col*940,70))
        else:draw.text((960,100),'No certified regeneration from matching historical inputs.',fill='black')
    sheet.save(D/f'figure_{i:02d}_comparison.jpg',quality=93)
(D/'figure_validation.json').write_text(json.dumps(rows,indent=2))
with (D/'figure_validation.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
old=(R/'word_verbatim_affiliation_b_20261115/main.tex').read_text()
new=(R/'verified_figure4_600dpi_20261115/main.tex').read_text()
assert new.replace('verified_figure4_600dpi_20261115/media/','word_verbatim_affiliation_b_20261115/media/')==old
for i in range(1,10):
    expected=base/('08_original_array_replay/figure4_600dpi.png' if i==4 else f'00_embedded_originals/image{i}.png')
    assert (R/f'verified_figure4_600dpi_20261115/media/image{i}.png').read_bytes()==expected.read_bytes()
assert hashlib.sha256(master.read_bytes()).hexdigest()=='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a'
summary=['# 그림 9개 대조 결과','',
'9개 모두를 고해상도로 완전 복원했다는 의미가 아니다. 전체 9개를 대상으로 완료·불일치·미복원을 구분했다.',
'본문과 캡션은 소속 변경본과 동일하며, 이미지 경로 외에는 TeX가 동일함을 검사했다. Word 마스터 SHA-256도 불변이다.',
'', '| 그림 | 판정 | 사유 |','|---|---|---|']
ko={1:'군집 번호와 점 배치 불일치',2:'2017년 음영 누락 및 과거 하위유형 표본 미확인',3:'초기 연도 곡선·신뢰구간 불일치',4:'원본 이미지 정밀도 기준 통과, 6000×3600px, 원래 폭에서 960dpi',5:'표본 수·계수 불일치',6:'일치하는 회귀 실행 상태 미확보로 재생성 보류',7:'다른 사건연구 버전이며 원본 두 패널이 아님',8:'그림의 반올림 비중만 전사한 후보이므로 제외',9:'전체 패널 미복원 및 군집 배치 불일치'}
for r in rows:summary.append(f"| {r['figure']} | {'검증된 교체본 유지' if r['figure']==4 else '원본 유지'} | {ko[r['figure']]} |")
summary += ['', '## 그림 4의 검증 범위',
'기존 코드 셀 154·172와 다운로드한 원본 임베딩을 사용했다. 특허 ID·연도·국가·배열 순서 267,519행을 대조했다.',
'세 시계열은 보관 SVG와 최대 약 0.0000104, 24개 연도 신뢰구간은 최대 약 0.00000722 차이다. 수치의 비트 단위 동일성은 주장하지 않으며, 원본 이미지에서 구분할 수 있는 정밀도 기준의 재현이다.',
'', '## 보존', '나머지 8개는 고해상도 파일이 있더라도 불일치·불완전 복원 때문에 교체하지 않았다. 반올림·재추정·새 군집 번호로 억지로 맞추지 않았다.',
'수치·방법상의 설명과 본 보고서는 원고에 추가하지 않았다. 임의 부록은 컴파일 대상에 없다.']
(D/'REPORT_KO.md').write_text('\n'.join(summary)+'\n')
print(json.dumps({'audited':9,'accepted_replacement':1,'retained_original':8,'body_unchanged_except_requested_affiliation':True,'master_unchanged':True,'report':str(D/'REPORT_KO.md')},indent=2))
