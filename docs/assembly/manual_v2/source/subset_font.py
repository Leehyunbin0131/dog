"""Build only the Korean/Latin glyphs required by the PDF authoring source."""
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
p=Path(__file__).resolve().parent
font=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',fontNumber=1)
sub=subset.Subsetter(options=subset.Options());sub.populate(text=(p/'rebuild_pdf.py').read_text());sub.subset(font);font.save(p/'NotoSansKRSubset.otf')
