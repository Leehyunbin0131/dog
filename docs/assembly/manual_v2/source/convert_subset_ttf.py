"""Convert CFF subset outlines to TrueType to avoid sparse CID/CFF viewer mapping.
Cubic to quadratic tolerance: 1 font unit (1/1000 em). Retains cmap and metrics.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
p=Path(__file__).resolve().parent
src=TTFont(p/'NotoSansKRSubset.otf');gs=src.getGlyphSet();order=src.getGlyphOrder()
fb=FontBuilder(src['head'].unitsPerEm,isTTF=True);fb.setupGlyphOrder(order)
glyphs={}
for name in order:
 pen=TTGlyphPen(gs);gs[name].draw(Cu2QuPen(pen,max_err=1.0,reverse_direction=True));glyphs[name]=pen.glyph()
fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(src['hmtx'].metrics)
fb.setupHorizontalHeader(ascent=src['hhea'].ascent,descent=src['hhea'].descent,lineGap=src['hhea'].lineGap)
fb.setupCharacterMap(src.getBestCmap())
fb.setupNameTable({'familyName':'Manual Noto KR','styleName':'Regular','uniqueFontIdentifier':'ManualNotoKR-Regular-REV3','fullName':'Manual Noto KR Regular','psName':'ManualNotoKR-Regular','version':'Version 1.000'})
fb.setupOS2(sTypoAscender=src['OS/2'].sTypoAscender,sTypoDescender=src['OS/2'].sTypoDescender,usWinAscent=src['OS/2'].usWinAscent,usWinDescent=src['OS/2'].usWinDescent)
fb.setupPost();fb.setupMaxp();fb.save(p/'ManualNotoKR.ttf')
print(p/'ManualNotoKR.ttf')
