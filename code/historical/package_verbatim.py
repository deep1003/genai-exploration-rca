from pathlib import Path
import zipfile,json
R=Path(__file__).resolve().parents[1]
wrapper=r'\AtBeginDocument{\setmainfont{FreeSerif.otf}[BoldFont=FreeSerifBold.otf,ItalicFont=FreeSerifItalic.otf,BoldItalicFont=FreeSerifBoldItalic.otf]}'+'\n'+r'\input{word_verbatim_source_20261115/main.tex}'+'\n'
(R/'00_admin/word_verbatim_root_main.tex').write_text(wrapper)
with zipfile.ZipFile(R/'07_reports/WORD_VERBATIM_overleaf_20261115.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('main.tex',wrapper)
    for p in (R/'word_verbatim_source_20261115').rglob('*'):
        if p.is_file():z.write(p,p.relative_to(R))
    assert z.testzip() is None
status='''# 원본 복원 상태

원본 DOCX에서 직접 변환했다. 교정 레시피를 사용하지 않았고 추가 부록은 없다.
원본과 변환 AST의 비공백 문자 54,209개가 일치한다. 이 검증은 페이지 배치나 공백·줄바꿈까지 동일하다는 뜻이 아니다.
빈 표, 원본 소속, 원본 수치, 원본 캡션을 유지했다. 임의 표 채움과 교정 문구는 현재 컴파일 경로에서 제외했다.
기존 검토본은 보존하되 main.tex에서 더 이상 참조하지 않는다.

그림은 현재 원본 내장 이미지 9개이다. 600dpi 재생성 완료가 아니다.
기존 노트북 코드와 여러 실행 버전을 찾았지만, 원본 그림의 전체 정밀도 시계열·신뢰구간, t-SNE 좌표와 원래 군집 라벨, 회귀 예측에 사용한 정확한 실행 상태가 확인되지 않았다.
그림 8의 보관된 표 역시 원본에 인쇄된 비중과 달랐다. 인쇄된 반올림 비중으로 만든 별도 후보는 채택하지 않았다.
다른 표본으로 재추정하거나 좌표를 다시 학습해 원본과 동일하다고 주장하지 않는다. 추가 원천 실행 상태 확보 없이 9개 모두의 정확한 600dpi 재생성은 현재 미완료이다.
'''
(R/'07_reports/word_verbatim_status.md').write_text(status)
print(R/'07_reports/WORD_VERBATIM_overleaf_20261115.zip')
