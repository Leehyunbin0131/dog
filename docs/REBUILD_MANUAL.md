# Assembly manual revision and source status

The current reviewed 31-page PDF is [Micro_Dog_X430_Assembly_Manual_KO.pdf](assembly/Micro_Dog_X430_Assembly_Manual_KO.pdf), REV 3, SHA-256 `f3ee08bcffafed3f60d5535f5efc6403afcbbb276325d1daff7912f2ade109fe`.

REV 3 fixes Korean-caption rendering compatibility using ReportLab TrueType subset embedding. All 31 pages were rendered and individually inspected with Ghostscript and PDFium; Poppler also rendered all pages. Normalized text matches REV 2 except revision labels. CAD, figures, BOM and assembly sequence are unchanged.

The existing [source directory](assembly/manual_v2/source/README.md) currently retains the REV 2 pipeline, frozen geometry and illustrations. It does not yet reproduce the corrected REV 3 embedding. Recovery of the REV 3 font/build sources is pending after a workspace restart. Use the delivered PDF for assembly; do not substitute a PDF regenerated from the old pipeline.

The retained base_revision1.pdf is a legacy build input, not the current assembly guide. Physical fit, tool access, print tolerance, cables, load and torque still require testing.
