#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validate manufacturing exports and native archive integrity (not a physical test)."""
from pathlib import Path
import hashlib,json,struct,zipfile
r=Path(__file__).resolve().parents[1]
manifest=json.loads((r/'docs/bom/print_manifest.json').read_text())
assert len(manifest)==18 and sum(x['quantity'] for x in manifest)==84
try: import trimesh
except ImportError: trimesh=None
for item in manifest:
 p=r/'cad/stl'/item['file'];b=p.read_bytes()
 assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],p
 assert len(b)==84+50*struct.unpack('<I',b[80:84])[0],p
 if trimesh:
  m=trimesh.load(p,force='mesh');assert m.is_watertight and m.is_winding_consistent and m.volume>0,p
 print('PASS',p.name)
assert len(list((r/'cad/step').glob('*.step')))==18
for p in (r/'cad/freecad').rglob('*.FCStd'):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None and 'Document.xml' in z.namelist(),p
pdf=r/'docs/assembly/Micro_Dog_X430_Assembly_Manual_KO.pdf';assert pdf.read_bytes().startswith(b'%PDF-')
print('PASS: 18 STL hashes/lengths, 84-part BOM, 18 STEP, FreeCAD archives, PDF header')
print('STL topology:', 'PASS (watertight, winding consistent, positive volume)' if trimesh else 'SKIPPED: install trimesh')
