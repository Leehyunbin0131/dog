#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Restore losslessly packed large files, validating against recorded hashes."""
import gzip, hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for rec in json.loads((root/'docs/bom/packed_files.json').read_text()):
    dest=root/rec['path']
    content=b''.join((root/p).read_bytes() for p in rec['sources'])
    if rec['encoding']=='gzip': content=gzip.decompress(content)
    assert len(content)==rec['bytes'] and hashlib.sha256(content).hexdigest()==rec['sha256'], rec['path']
    if dest.exists():
        assert dest.read_bytes()==content, f'Refusing to replace changed file: {dest}'
    else: dest.write_bytes(content)
    print('Verified/restored',rec['path'])
