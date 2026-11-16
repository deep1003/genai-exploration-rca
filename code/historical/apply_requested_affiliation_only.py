from pathlib import Path
import shutil,json
R=Path(__file__).resolve().parents[1]
D=R/'word_verbatim_affiliation_b_20261115';D.mkdir(exist_ok=True)
shutil.copytree(R/'word_verbatim_source_20261115/media',D/'media',dirs_exist_ok=True)
s=(R/'word_verbatim_source_20261115/main.tex').read_text()
assert s.count('Youngsam Chunᵃ,¹')==1
s=s.replace('Youngsam Chunᵃ,¹','Youngsam Chunᵇ,¹')
anchor='Sejong 30147, Republic of Korea'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n\nᵇ Frontier AI Lab, KT, 151 Taebong-ro, Seocho-gu, Seoul 06763, Republic of Korea',1)
s=s.replace('word_verbatim_source_20261115/media/','word_verbatim_affiliation_b_20261115/media/')
(D/'main.tex').write_text(s)
(R/'00_admin/requested_affiliation_only.json').write_text(json.dumps({'author_old':'Youngsam Chunᵃ,¹','author_new':'Youngsam Chunᵇ,¹','added_affiliation':'ᵇ Frontier AI Lab, KT, 151 Taebong-ro, Seocho-gu, Seoul 06763, Republic of Korea','other_content_changes':0,'original_docx_modified':False},ensure_ascii=False,indent=2))
print(D)
