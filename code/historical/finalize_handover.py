"""Verify downloaded Overleaf artifacts and preserve an auditable handover."""
from pathlib import Path
import hashlib,json,zipfile,shutil,csv
from datetime import datetime
import pypdf

R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Path('/Users/deep1003/Downloads/조원선_박사님_01 (1).zip')
online=Path('/Users/deep1003/Downloads/조원선_박사님_01.pdf')
shutil.copy2(source,R/'00_admin/overleaf_after_upload.zip')
shutil.copy2(online,R/'05_overleaf/main_overleaf_verified.pdf')
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    names=z.namelist()
    checked=[]
    for p in (R/'original_master_review_20261115').rglob('*'):
        if p.is_file():
            name=p.relative_to(R).as_posix()
            assert z.read(name)==p.read_bytes(),name
            checked.append(name)
    assert 'original_master_review_20261115/main.tex' in z.read('main.tex').decode()
pdf=pypdf.PdfReader(online)
assert len(pdf.pages)==24
text='\n'.join(p.extract_text() or '' for p in pdf.pages)
assert 'Technological exploration distance' in text
assert 'Frontier AI Lab' in text
(R/'00_admin/online_pdf_text.txt').write_text(text)
master=R/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx'
assert sha(master)=='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a'
state={'project_url':'https://ko.overleaf.com/project/6af9976398eed2c21d6dfbe4','verified_at':datetime.now().astimezone().isoformat(),'pages':24,'ui_errors':0,'ui_warnings':0,'ui_typesetting_info':3,'verified_source_files':checked,'source_sha256':sha(source),'pdf_sha256':sha(online),'master_sha256':sha(master),'status':'review draft, unresolved evidence gaps remain'}
(R/'00_admin/overleaf_upload_verification.json').write_text(json.dumps(state,indent=2))
summary=json.loads((R/'00_admin/search_summary.json').read_text())
changes=list(csv.DictReader((R/'04_review/change_log.csv').open()))
report=f'''# Original-master review and Overleaf handover

검토 기준은 `RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx`이다. 이전 ENTRY 중심 개정본을 업로드하지 않았다. 본 버전은 증거 공백이 남아 있는 검토본이며 제출 확정본이 아니다.

## 완료

- 원본 DOCX를 `01_master/`에 보존했다. SHA-256 `{sha(master)}`.
- 원고 내 이미지 9개를 `02_figures/00_embedded_originals/`에 백업했다. 업로드 그림도 원본 바이트를 유지한다.
- 문단 변경 {len(changes)}건을 `04_review/change_log.csv`, 실제 변경추적 Word `reviewed_tracked.docx`, 교정 Word `reviewed_clean.docx`, `redline.html`에 기록했다.
- 수식을 LaTeX로 조판하고 Figure 제목과 Notes를 분리했다. 이 조판 및 일부 추가 표현 한정은 `06_scripts/format_original_overleaf.py`에 별도로 추적된다. Word와 TeX가 바이트 수준으로 동일한 문서라는 의미는 아니다.
- 표 4의 16개 수치 셀을 보관 노트북 cell 234의 저장 출력에서 복원했다. 단위는 고유 특허 수가 아니라 미국·중국 키워드 출현 횟수의 비중이다. 키워드는 중복 가능하며 RCA 필터 적용 여부는 확인되지 않았다.
- 표 3은 본문의 미국·중국 비중 4개와 100에서 두 국가 비중을 뺀 잔여 비중 2개만 채웠다. 잔여 비중은 별표로 표시했다.
- 새 Overleaf 프로젝트에 `original_master_review_20261115/`와 변경기록을 업로드했다. 기존 main.tex는 다운로드 소스 ZIP으로 보존 후 입력 wrapper로 변경했다.
- XeLaTeX, TeX Live 2026에서 온라인 24쪽 PDF를 생성했다. UI 오류 0, 경고 0, 조판 정보 3건이다. 온라인 PDF와 소스를 다시 다운로드하고 업로드한 11개 파일의 바이트 일치를 검증했다.

## 그림 검색과 남은 공백

- data3, data4, Downloads, Documents, Desktop, iCloud Drive, CloudStorage를 검색했다. 중복 실제 경로를 제외한 대상 파일 {summary['files_inventoried']:,}개를 목록화하고, resident 노트북 {summary['notebooks_considered']}개를 검사했다.
- 미다운로드 클라우드 placeholder {summary['cold_placeholders']:,}개는 본문을 읽지 않았다. PDF/SVG/EPS/ZIP은 목록화만 했으며 내부 전수 검색은 미완료이다. 따라서 모든 저장소 내용 검색 완료로 간주하면 안 된다.
- 지각 해시 후보 {summary['matches']}건에는 다른 분석 버전과 무관한 그림도 포함된다. `02_figures/01_candidates/`는 후보 보관소일 뿐 채택된 고해상도 폴더가 아니다. 후보 contact sheet를 검토했으나 완전한 동일성·버전 검증 전 대체하지 않았다.
- 원본 image3는 2004×590 픽셀로 6인치 폭에서 약 334 dpi이다. 원본 자체를 `02_verified_high_resolution/`에 보존했다. 다른 8개 그림의 출판용 고해상도 확보·충실 재생성은 미완료이다. image6, image7은 폭을 줄이면 300 dpi에 접근하지만 새 고해상도 원본 확보와 같지 않다.
- Figure 5는 별도 표준화한 제곱항과 예측곡선 구성의 불일치가 있어 단순 확대 재생성을 하지 않았다. 원본을 보존하고 Notes에 문제를 명시했다. 후보 곡선에서도 버전별 차이가 있다.

## 수치·방법·인용 검토 한계

- 표 3의 9개 수치 셀은 NR로 남아 있다. 원고 군집 번호와 보관 코드 군집 번호의 일치가 입증되지 않아 다른 군집 통계를 이식하지 않았다.
- 원고 GenAI 97,911, 보관 회귀 일치 표본 90,332, 후속 재구성 93,293은 동일 표본이 아니다. 원본 서사에 후속 결과를 무표시 대체하지 않았다.
- 기존 고정효과 구현, 제곱항 변환, 국가 귀속·분모, 사건연구 기준화 및 군집 대응을 한계와 부록에 표시했다. 가설은 보존하되 검증되지 않은 인과·일반적 최적거리 주장은 한정했다.
- 표 2에 해당하는 완전한 기술통계 원천표는 복원하지 못했다. 원고 전체의 모든 수치가 재검산 완료됐다는 의미가 아니다.
- 기존 참고문헌과 출처 대응은 보관 증거 범위에서 검토했다. 모든 참고문헌의 온라인 원문·DOI·인용 주장 전수 검증은 미완료이다. 신규 레퍼런스를 임의로 만들어 추가하지 않았다.
- 본 작업에서 회귀 재추정, 군집 재학습, 임베딩 재생성 또는 신규 데이터 생성은 하지 않았다. 부록은 보관된 민감도 근거와 한계만 포함한다.

## 위치

- 프로젝트 https://ko.overleaf.com/project/6af9976398eed2c21d6dfbe4
- 작업 루트 `{R}`
- 업로드 전후 소스 `00_admin/overleaf_before_upload.zip`, `overleaf_after_upload.zip`
- 온라인 PDF `05_overleaf/main_overleaf_verified.pdf`
- 검증 기록 `00_admin/overleaf_upload_verification.json`
- 모든 새 산출물은 iCloud/data3 아래에 있다. 이 사실만으로 iCloud 서버 동기화 완료를 보증하지는 않는다.
'''
(R/'07_reports/completion_report.md').write_text(report)
portable=R/'07_reports/OVERLEAF_original_master_review_20261115.zip'
with zipfile.ZipFile(portable,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('main.tex','\\input{original_master_review_20261115/main.tex}\n')
    z.writestr('latexmkrc',"$pdf_mode = 5;\n")
    for p in (R/'original_master_review_20261115').rglob('*'):
        if p.is_file():z.write(p,p.relative_to(R))
    z.write(R/'07_reports/completion_report.md','REVIEW_STATUS.md')
    assert z.testzip() is None
print(json.dumps(state,indent=2))
print('REPORT',R/'07_reports/completion_report.md')
print('ZIP',portable)
