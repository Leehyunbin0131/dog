# REV 3 font compatibility and verification

Approved canonical PDF SHA256: `f3ee08bcffafed3f60d5535f5efc6403afcbbb276325d1daff7912f2ade109fe` (4,502,371 bytes, 31 pages).

REV 2 rendered revised captions correctly in Poppler but showed fragmented/substituted glyphs in Ghostscript, reproducing the reported page 9 screenshot. Original TrueType body text remained intact. Converting CFF outlines to TrueType alone while retaining PyMuPDF CID text insertion did not fix it. Using ReportLab TrueType subset embedding did. This is a demonstrated embedding/viewer compatibility defect; no precise internal viewer bug is asserted.

## Rebuild

From repository root, using committed assets and font:

    python docs/assembly/manual_v2/source/rebuild_pdf.py

This writes `docs/assembly/manual_v2/Micro_Dog_X430_Assembly_Manual_KO_v3.pdf`, never the canonical PDF. The legacy directory name `manual_v2` is retained for stable paths; its current scripts produce REV 3. The frozen input is `base_revision1.pdf`, not the current PDF.

Font regeneration, when changing text:

    python docs/assembly/manual_v2/source/subset_font.py
    python docs/assembly/manual_v2/source/convert_subset_ttf.py
    python docs/assembly/manual_v2/source/rebuild_pdf.py

Dependencies: PyMuPDF, ReportLab, fontTools. Font regeneration additionally needs installed Noto Sans CJK. Cubic-to-quadratic tolerance is 1/1000 em. Font license: `licenses/NOTO-OFL.txt`. Keep the committed font for reproducing the approved layout. Font and PDF timestamps can change binary hashes without changing rendered content.

## Exact-final-file verification

    pdftoppm -scale-to 1400 -png FINAL.pdf poppler/page
    gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -r120 -sOutputFile=ghostscript/page-%02d.png FINAL.pdf

PDFium: `pypdfium2.PdfDocument(FINAL)` and each page's `render(scale=1.666).to_pil()`.

Before approval, all 31 exact final pages were individually visually reviewed in Ghostscript and PDFium, with no fragmented/missing glyphs or clipped content. Poppler rendered all 31 as additional evidence; no claim is made that every Poppler page was visually inspected. Normalized extracted text matched REV 2 exactly except revision labels. CAD, figure assets, BOM and assembly sequence were unchanged.

After workspace recovery, the reconstruction was compared against the immutable approved PDF: all 31 pages had exact extracted-text equality and pixel equality in MuPDF at scale 1.666 and Ghostscript at 120 dpi. This checks recovered source fidelity without replacing the approved artifact. No optimization or font modification should be applied after final-file review and hashing.
