from pathlib import Path
import zipfile,json,hashlib,shutil,re
from datetime import datetime
from zoneinfo import ZoneInfo
import pdfplumber
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
D=R/'07_reports/figure_by_figure_qa_20261115'
source=Path('/Users/deep1003/Downloads/조원선_박사님_01 (2).zip')
pdf=Path('/Users/deep1003/Downloads/조원선_박사님_01 (2).pdf')
prefix='verified_figure4_600dpi_20261115'
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    wrapper=z.read('main.tex').decode()
    assert r'\input{'+prefix+'/main.tex}' in wrapper
    assert 'original_master_review_20261115/main.tex' not in wrapper
    online=z.read(prefix+'/main.tex').decode()
    assert online==(R/prefix/'main.tex').read_text()
    checked=[]
    for p in (R/prefix).rglob('*'):
        if p.is_file():
            name=p.relative_to(R).as_posix()
            assert z.read(name)==p.read_bytes(),name
            checked.append(name)
    original=(R/'word_verbatim_source_20261115/main.tex').read_text()
    back=online.replace(prefix+'/media/','word_verbatim_source_20261115/media/')
    back=back.replace('Youngsam Chunᵇ,¹','Youngsam Chunᵃ,¹')
    back=back.replace('\n\nᵇ Frontier AI Lab, KT, 151 Taebong-ro, Seocho-gu, Seoul 06763, Republic of Korea','')
    assert back==original
    assert r'\appendix' not in online
    assert 'Appendix A Evidence audit' not in online
images=[]
with pdfplumber.open(pdf) as doc:
    for i,page in enumerate(doc.pages):
        for im in page.images:
            if im.get('srcsize')==(6000,3600):
                images.append({'page':i+1,'source_pixels':list(im['srcsize']),'display_width_points':im['width'],'effective_dpi':6000/(im['width']/72)})
    count=len(doc.pages)
assert len(images)==1 and images[0]['effective_dpi']>=600
text='\n'.join(p.extract_text() or '' for p in PdfReader(pdf).pages)
assert 'Frontier AI Lab' in text
assert 'Appendix A Evidence audit' not in text
shutil.copy2(source,D/'overleaf_source_verified.zip')
shutil.copy2(pdf,D/'overleaf_pdf_verified.pdf')
rec={'verified_at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'project_url':'https://ko.overleaf.com/project/6af9976398eed2c21d6dfbe4','source_files_byte_verified':checked,'pdf_pages':count,'figure4_pdf_image':images,'other_eight_images_original_bytes':True,'body_and_captions_exactly_preserved_except_requested_affiliation':True,'invented_appendix_in_active_manuscript':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}
(D/'online_deployment_verification.json').write_text(json.dumps(rec,indent=2))
with zipfile.ZipFile(D/'OVERLEAF_verified_figure4_original_text.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('main.tex',wrapper)
    for p in (R/prefix).rglob('*'):
        if p.is_file():z.write(p,p.relative_to(R))
    assert z.testzip() is None
print(json.dumps(rec,indent=2))
import pypdfium2 as pdfium
rendered=pdfium.PdfDocument(str(pdf))
for number in [1,8,count]:
    rendered[number-1].render(scale=1.4).to_pil().save(D/f'online_page_{number:02d}.png')
report=D/'REPORT_KO.md'
text=report.read_text()
if '## 온라인 재검증' not in text:
    text+='\n## 온라인 재검증\n\nOverleaf에서 소스와 PDF를 다시 내려받았다. 활성 소스 10개 파일은 로컬 검증본과 바이트가 일치한다. 소속 변경 두 곳과 미디어 경로를 되돌리면 최초 Word 직접 변환 TeX와 완전히 동일하다. 나머지 8개 이미지는 Word 원본의 바이트를 유지한다.\n\n온라인 PDF는 18쪽이며, 8쪽의 그림 4는 실제 6000×3600픽셀로 포함돼 있다. PDF에 삽입된 폭 450.0009pt에서 실효 해상도는 약 960dpi다. 임의 부록은 활성 원고에 없다.\n'
    report.write_text(text)
