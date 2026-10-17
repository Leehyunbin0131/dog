# Rebuild the REV 2 assembly manual

The current, reviewed 31-page manual is [Micro_Dog_X430_Assembly_Manual_KO.pdf](assembly/Micro_Dog_X430_Assembly_Manual_KO.pdf).

Reproducible inputs and commands are in [manual_v2/source/README.md](assembly/manual_v2/source/README.md). The package includes the CAD-derived frozen mesh export, renderer C++/Python sources, final PNG illustrations, font-subset generator and subset font, and the frozen previous PDF used only as a layout/text template. No source CAD geometry is modified.

The old `base_revision1.pdf` is a build input, not the current assembly guide. Do not follow its superseded illustrations.

Publication verification: rebuilding the PDF from the relocated source/assets and frozen template produced pixel-identical output on all 31 pages at 72 dpi. The delivered PDF is the exact separately approved revision, SHA-256 `95d5a4e7eca46312946c1a699aa11fdd93f82e8862afd268c6134025ec167164`.

This is a CAD-based explanatory manual, not physical validation. Small-bearing corner/fillet fit, real tools, print tolerances, cables, load, fastener torque and all-corner physical fit still require tests.
