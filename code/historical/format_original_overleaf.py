"""Keep the original article structure while separating captions and notes."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'05_overleaf/main.tex'
s=p.read_text().replace('ᵃ',r'$^a$').replace('ᵇ',r'$^b$')
def caption(match):
    body=match.group(1)
    first,sep,rest=body.partition('. ')
    if not sep:return match.group(0)
    return r'\caption{'+first+'.}'+ '\n'+r'\caption*{\footnotesize\textit{Notes:} '+rest+'}'
s=re.sub(r'\\caption\{([^\n]+)\}',caption,s)
s=s.replace('Note: ',r'\textit{Notes:} ')
s=s.replace('Its construction does not correctly transform the separately standardised squared-distance regressor; it should be replaced only after a corrected prediction calculation is approved.',
    'Its construction does not correctly transform the separately standardised squared-distance regressor. A different reconstructed estimate cannot be adopted as an exact historical reproduction.')
s=s.replace('Each hub holds chokepoints over the other, and both hold chokepoints over third countries.',
    'The framework suggests potential reciprocal leverage, but the patent analysis does not directly measure such chokepoints.')
s=s.replace('The movement toward parallel ecosystems with limited cross-fertilisation is the network-level expression of this mutual exposure.',
    'Whether parallel ecosystems emerge from this exposure requires direct evidence beyond these patent patterns.')
p.write_text(s)
if '\\begin{minipage}' not in s:
    s=s.replace('Table 3. Reported',r'\FloatBarrier'+'\n'+r'\begin{minipage}{\linewidth}'+'\n'+'Table 3. Reported')
    s=s.replace('Table 4. Archived',r'\end{minipage}'+'\n\n'+r'\bigskip\begin{minipage}{\linewidth}'+'\n'+'Table 4. Archived')
    s=s.replace('The retained keyword evidence is consistent',r'\end{minipage}'+'\n\n'+'The retained keyword evidence is consistent')
    p.write_text(s)
print('FORMATTED_MASTER_OVERLEAF')
