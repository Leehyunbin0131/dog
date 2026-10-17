# Rebuild the REV 3 assembly manual

The current, reviewed 31-page manual is [Micro_Dog_X430_Assembly_Manual_KO.pdf](assembly/Micro_Dog_X430_Assembly_Manual_KO.pdf).

Reproducible inputs and commands are in [manual_v2/source/README.md](assembly/manual_v2/source/README.md). The package includes the CAD-derived frozen mesh export, renderer C++/Python sources, final PNG illustrations, font-subset generator and subset font, and the frozen previous PDF used only as a layout/text template. No source CAD geometry is modified.

The old `base_revision1.pdf` is a build input, not the current assembly guide. Do not follow its superseded illustrations.

Publication verification: the delivered PDF is the exact approved 31-page artifact, SHA-256 `f3ee08bcffafed3f60d5535f5efc6403afcbbb276325d1daff7912f2ade109fe`. Every page was rendered and individually inspected with Ghostscript and PDFium; Poppler rendered all pages. Normalized extracted text matches REV 2 except revision labels. See [font compatibility verification](assembly/manual_v2/source/VERIFY_AND_BUILD.md) and [QA report](assembly/manual_v2/source/qa_report.json).

REV 3 changes font embedding, not the CAD figures, BOM or assembly sequence. Rebuilds may differ in byte hash due to PDF creation timestamps; repeat text and rendering checks before publication.

This is a CAD-based explanatory manual, not physical validation. Small-bearing corner/fillet fit, real tools, print tolerances, cables, load, fastener torque and all-corner physical fit still require tests.

Recovered-source verification: all 31 rebuilt pages have exact extracted-text equality and pixel-identical output against the approved PDF in MuPDF (scale 1.666) and Ghostscript (120 dpi). The approved delivered PDF was not regenerated or replaced during source recovery.
