# CAD-based manual revision 3

Input geometry: repository `cad/freecad/assemblies/RR_complete_leg_pelvis_final.FCStd`, read-only. The original PDF is retained as a layout/text source, with full illustration-panel redactions before inserting replacement figures and captions. Non-assembly part trays and validated text-only pages are retained.

Rebuild from repository root using the included frozen CAD mesh data:

```sh
g++ -O3 -shared -fPIC docs/assembly/manual_v2/source/raster.cpp -o docs/assembly/manual_v2/source/raster.so
python docs/assembly/manual_v2/source/build_figures.py
python docs/assembly/manual_v2/source/build_jointmap.py
python docs/assembly/manual_v2/source/render_four_corner.py
python docs/assembly/manual_v2/source/rebuild_pdf.py
mkdir -p docs/assembly/manual_v2/review
pdftoppm -scale-to 1400 -png docs/assembly/manual_v2/Micro_Dog_X430_Assembly_Manual_KO_v3.pdf docs/assembly/manual_v2/review/page
```

Optional fresh extraction (requires FreeCAD), before the commands above:

```sh
/usr/bin/python3 docs/assembly/manual_v2/source/extract_cad.py
python docs/assembly/manual_v2/source/pack_meshes.py
```

The committed `ManualNotoKR.ttf` is sufficient to rebuild the existing text. If changing Korean text, run `subset_font.py`, then `convert_subset_ttf.py` (fontTools and installed Noto Sans CJK required). ReportLab TrueType subset embedding is required for viewer compatibility. See `VERIFY_AND_BUILD.md` for exact-final-file checks and recovery verification.

Runtime dependencies: numpy, Pillow, PyMuPDF, ReportLab, fontTools, FreeCAD for extraction only, a C++ compiler. No graphical server, GPU, OpenGL or VTK is required. `raster.cpp` is a deterministic orthographic depth-buffer renderer; the shared binary can be rebuilt on the target machine. Reproducing existing geometry does not require re-extraction: `meshes.npz` is the frozen source mesh export.

Sources and verification:
- `fastener_axes.json`: exact centers/axes for all 36 screws, live CAD surface references, nut pocket polygon rotations, bearing placement basis and limitations.
- `render_manifest.json`: figure keys, new-part selections, view vectors and exploded offsets.
- `four_corner_report.json`: reconstruction transforms and caveats.
- Hardware is an explanatory dimensional mesh, without thread helices. Bearings are explanatory annular meshes; small-bearing fit requires physical trial.
- Stock detached manufacturer screws/spacers are not rendered as part of motor bodies. The motor bodies, horns and reference covers/connectors are retained.

No CAD file is modified by these commands. No control configuration, motor electrical zero or validated torque is implied.

## Publication inputs

`../base_revision1.pdf` is a frozen legacy layout/text input, not the current assembly guide. Read the canonical current PDF at `../../Micro_Dog_X430_Assembly_Manual_KO.pdf`. The retained template avoids recursive editing of the current PDF.

`meshes.npz` stores the exact frozen float64 vertices/int32 faces. `render_cad.py` loads it without requiring FreeCAD. To re-extract from the unchanged assembly, run extract_cad.py then pack_meshes.py. The uncompressed JSON and compiled raster.so are generated locally and ignored.

`subset_font.py` generates NotoSansKRSubset.otf from installed Noto Sans CJK and the manual text. See ../../../../licenses/NOTO-OFL.txt for font notices. Scripts are GPL-3.0-or-later; mechanical geometry/documents CC BY-NC-SA 4.0, except manufacturer reference geometry as documented in the root notices.

The historical directory name `manual_v2` is retained for stable paths; current sources produce REV 3. Rebuilding writes a separate generated PDF and never replaces the canonical approved PDF.
