"""Reapply traceable original-manuscript proofreading in a new, isolated project."""
from pathlib import Path
import hashlib,json,shutil

OUT=Path(__file__).resolve().parents[1]
OLD=OUT.parent/'cho_chun_overleaf_review_20261115'
for name in ['review','overleaf','source_snapshot','audit','evidence']:
    (OUT/name).mkdir(exist_ok=True)
for p in (OLD/'audit').iterdir():
    if p.suffix in {'.txt','.json','.csv'} and p.stat().st_size<10_000_000:
        shutil.copy2(p,OUT/'audit'/p.name)
shutil.copy2(OUT/'01_master/RP_Manuscript_full_Cho_Chun_appendix_X_v00_original.docx',OUT/'source_snapshot/original.docx')
for p in (OUT/'02_figures/00_embedded_originals').iterdir():
    (OUT/'overleaf/figures').mkdir(exist_ok=True)
    shutil.copy2(p,OUT/'overleaf/figures'/p.name)
code=(OLD/'scripts/build_review.py').read_text()
code=code.replace("OUT=Path(__file__).resolve().parents[1]",'OUT=Path('+repr(str(OUT))+')')
code=code.replace("'A corrected fixed-effects estimate and a logit sensitivity analysis require a separately approved analysis run.'", "'The historical output is not certification of a corrected fixed-effects result.'")
code=code.replace('A corrected fixed-effects estimate and a logit sensitivity analysis require a separately approved analysis run.',
    'Separate reconstructed analyses are not silently substituted for the historical estimates in this original-manuscript review.')
code=code.replace('keyword-matched records','keyword occurrences').replace('keyword-matched patents','keyword occurrences')
code=code.replace('keyword-matched records','keyword occurrences')
insertion='''
replace(1,"One-Sun Choᵃ,¹,* and Youngsam Chunᵇ,¹","Retain author order and equal contribution; distinguish the requested KT affiliation.")
replace(2,"ᵃ Science and Technology Policy Institute (STEPI), 370 Sicheong-daero, Sejong 30147, Republic of Korea; ᵇ Frontier AI Lab, KT, 151 Taebong-ro, Seocho-gu, Seoul 06763, Republic of Korea","Apply the user-specified affiliation without changing the preserved Word master.")
replace(7,"This study asks how generative artificial intelligence innovation is organised around the United States and China, and how technological exploration relates to national comparative advantage. Combining technological search theory with weaponised interdependence, it examines a corpus of 267,519 AI algorithm and model patent records using semantic embeddings, comparative-advantage indicators and inventor networks. Archived regressions report a concave distance association and inventor-team interactions, while evidence for family-size moderation is weaker. The retained figures suggest architectural convergence and changing national network positions. These patterns motivate a Data-Human-Computing-Politics framework linking productive complementarities to potential strategic vulnerabilities. However, classification versions, the implementation of fixed effects, polynomial prediction scaling and cluster correspondence limit the interpretation of the original estimates. The contribution is a positional account of innovation and strategic interdependence rather than a demonstrated causal effect or a universal optimal exploration distance.","Preserve the original research question and theoretical structure; qualify claims against available historical evidence without importing the later ENTRY paper.")
replace(18,"The analysis combines three types of evidence: archived distance-RCA regressions, descriptive convergence trajectories, and inventor-network and technology-space illustrations. These sources address the original hypotheses but do not jointly establish a robust inverted U, causal moderation or a uniquely identified Transformer break. The paper contributes a semantic-embedding approach to technological positioning, a distinction between patent scale and relative specialisation, and the DHCP framework for interpreting potential strategic vulnerabilities. Section 2 develops the framework and hypotheses, Section 3 describes the data and methods, Section 4 reports the original evidence with its limitations, and Sections 5 and 6 discuss implications and conclusions.","Remove contradiction between qualified abstract and categorical introduction; retain original scope and section sequence.")
replace(74,"In the archived OLS results, several input-count and network coefficients are small or statistically inconclusive. A positive forward-citation association is reported, whereas backward citations are less conclusive. These conditional associations do not identify a knowledge-diffusion mechanism, establish that scale is unimportant, or compare returns to policy spending. Their interpretation depends on the observation unit, model implementation and timing of patent attributes.","Distinguish association from mechanism and avoid interpreting non-significance as proof of no effect.")
replace(97,"The retained keyword evidence is consistent with differences in the composition of the two national patent portfolios. Chinese occurrences are relatively concentrated in attention and pre-training terms, while U.S. shares are comparatively larger for embedding and speech-recognition terms. These are overlapping keyword-occurrence distributions within source clusters, not independently validated national comparative-advantage totals. They motivate a diversification-versus-convergence interpretation but do not by themselves establish economic complementarity or geopolitical fragmentation.","Align synthesis with keyword occurrence denominator and unverified historical cluster crosswalk.")
replace(101,"The convergence figures add a temporal dimension to the dominant-design argument. They are consistent with increasing commonality around the Transformer period, but one architectural event is not separately identified from contemporaneous changes. The U.S.-China comparison suggests different portfolio trajectories, which can be discussed as diversification and convergence without treating them as observed optimal strategies or proven causes of durable national advantage.","Keep dominant-design interpretation observational.")
replace(103,"Read through the DHCP framework, concentrated data, specialised talent and computing may create productive complementarities and strategic dependencies. Path dependence, network effects and infrastructure costs provide possible reinforcing mechanisms (Arthur, 1994). The proposed Leontief analogy is a theoretical simplification, not an estimated production technology. Patent positions do not directly establish ownership or control of these bottleneck inputs.","Separate middle-range theory from direct empirical measurement.")
replace(106,"The national patterns can be related to diffusion-based accounts of technological leadership (Ding, 2024), the co-evolution of corporate and national innovation systems (Lundvall and Rikap, 2022), and the political mobilisation of innovation effort (Taylor, 2016). These literatures provide interpretations rather than identified mechanisms in the present patent analysis. Testing rivalry-induced innovation, dominant-design crowding or mutually binding chokepoints would require direct measures and an additional identification design.","Avoid claiming that descriptive correlations prove geopolitical or crowding mechanisms.")
replace(113,"The DHCP framework adds political conditions to the data, talent and computing account of AI production. It proposes that input complementarities can produce both efficiency gains and strategic exposure. The empirical patent patterns motivate that argument, but do not establish that the same observed dependencies became operational chokepoints or quantify the political effects of strategic competition. These remain theoretical implications to be examined with direct evidence.","Keep conclusion consistent with measured outcomes and theoretical status.")
'''
code=code.replace('def text_run(text,deleted=False):',insertion+'\ndef text_run(text,deleted=False):')
code=code.replace("Youngsam Chun$^{a,1}$", "Youngsam Chun$^{b,1}$")
code=code.replace("esc(BLOCKS[2]['text'].lstrip('ᵃ '))", "esc(changes[2]['new'])")
code=code.replace('This appendix transcribes already saved outputs and gives algebraic checks.',
    'This appendix transcribes already saved historical outputs and gives algebraic checks. It is not the later transition-based manuscript.')
code=code.replace('A corrected prediction plot and endpoint tests remain pending.',
    'Corrected reconstructed analyses exist separately, but are not adopted as exact reproductions of this historical curve.')
code=code.replace('require author resolution or an approved rerun.',
    'require author resolution before any claim of exact historical reproduction.')
exec(compile(code,str(OUT/'06_scripts/reused_proofread_recipe.py'),'exec'),{'__file__':str(__file__),'__name__':'__main__'})
shutil.copytree(OUT/'review',OUT/'04_review',dirs_exist_ok=True)
shutil.copytree(OUT/'overleaf',OUT/'05_overleaf',dirs_exist_ok=True)
assert hashlib.sha256((OUT/'source_snapshot/original.docx').read_bytes()).hexdigest()=='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a'
(OUT/'00_admin/proofread_lineage.json').write_text(json.dumps(dict(master_sha256='2a4c4099935e2bb84a88b32ce0f4dc8ae7d60375215c4aaae556f1fa8f443e3a',
    recipe_source=str(OLD/'scripts/build_review.py'),original_structure_retained=True,entry_manuscript_imported=False,
    new_regressions=False,table3_unrecovered_cells=9,table4_numeric_cells_recovered=16),indent=2)+'\n')
print('MASTER_PROOFREAD_COMPLETE',OUT,flush=True)
