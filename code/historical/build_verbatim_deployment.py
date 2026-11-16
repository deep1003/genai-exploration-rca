"""Deploy only the direct DOCX conversion, with no editorial recipe."""
from pathlib import Path
import json,zipfile,hashlib,re,shutil
from lxml import etree
R=Path(__file__).resolve().parents[1]
D=R/'word_verbatim_source_20261115';D.mkdir(exist_ok=True)
shutil.copytree(R/'word_original_exact_20261115/media',D/'media',dirs_exist_ok=True)
s=(R/'word_original_exact_20261115.tex').read_text()
s=s.replace(r'\usepackage{lmodern}',r'\usepackage{lmodern}'+'\n'+r'\setmainfont{FreeSerif.otf}'+'\n'+r'\usepackage[a4paper,margin=25mm]{geometry}')
s=s.replace('word_original_exact_20261115/media/','word_verbatim_source_20261115/media/')
(D/'main.tex').write_text(s)
ast=json.loads((R/'00_admin/original_pandoc_ast.json').read_text())
def text(node):
    if isinstance(node,list):return ''.join(text(n) for n in node)
    if not isinstance(node,dict):return ''
    t=node.get('t');c=node.get('c',[])
    if t=='Str':return c
    if t in ['Space','SoftBreak','LineBreak']:return ' '
    if t=='Image':return ''
    if t=='Header':return text(c[2])
    if t in ['Link','Span']:return text(c[1])
    return text(c)
doc=R/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx'
with zipfile.ZipFile(doc) as z:
    root=etree.fromstring(z.read('word/document.xml'))
    originals=root.xpath('//w:body//w:p',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
    original=' '.join(''.join(p.xpath('.//w:t/text()',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})) for p in originals)
normal=lambda x:re.sub(r'\s+','',x)
actual=text(ast['blocks'])
same=normal(original)==normal(actual)
import difflib
diff='\n'.join(difflib.unified_diff(original.split(),actual.split(),fromfile='DOCX',tofile='Pandoc AST'))
(R/'00_admin/verbatim_character_diff.txt').write_text(diff)
record={'master_sha256':hashlib.sha256(doc.read_bytes()).hexdigest(),'direct_docx_conversion':True,'editorial_recipe_used':False,'appended_sections':0,'characters_equal_excluding_whitespace':same,'original_nonspace_chars':len(normal(original)),'converted_nonspace_chars':len(normal(actual)),'images':len(list((D/'media').iterdir())),'600dpi_regeneration_complete':False}
(R/'00_admin/verbatim_conversion_check.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
print(diff[:2000])
