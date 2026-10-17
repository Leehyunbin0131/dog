"""Lossless numerical packing of JSON mesh doubles and integer triangle indices."""
from pathlib import Path
import numpy as np,json
p=Path(__file__).resolve().parent
j=json.loads((p/'meshes.json').read_text());d={}
for k,m in j.items():
 d[k+'_v']=np.array(m['v'],dtype=np.float64)
 d[k+'_f']=np.array(m['f'],dtype=np.int32)
np.savez_compressed(p/'meshes.npz',**d)
