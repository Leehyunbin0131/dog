import sys,json,math,os
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parents[1];(OUT/'assets').mkdir(exist_ok=True)
d=A.openDocument(str(ROOT/'cad/freecad/assemblies/RR_complete_leg_pelvis_final.FCStd'));local=d.getObject('Part').Placement.inverse()
raw={}
def shape_global(o):
 s=o.Shape.copy();s.Placement=local.multiply(o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement));return s
for n in list(range(251,264))+list(range(211,215))+list(range(277,281)):
 raw[str(n)]=shape_global(d.getObject('Part__Feature'+str(n)))
for key,names in {'pitch':['Part__Feature215','Part__Feature216','DC11_A01_CASE_CVR_DUMMY001','Part__Feature219','Part__Feature220'], 'knee':['Part__Feature','Part__Feature180','DC11_A01_CASE_CVR_DUMMY','Part__Feature183','Part__Feature184'], 'roll':['Part__Feature264','Part__Feature281']}.items():
 raw[key]=[shape_global(d.getObject(n)) for n in names]
meshes={}
for k,shapes in raw.items():
 shapes=shapes if isinstance(shapes,list) else [shapes]
 vv=[];ff=[]
 for s in shapes:
  v,f=s.tessellate(.12);i=len(vv);vv.extend([[q.x,q.y,q.z] for q in v]);ff.extend([[j+i for j in t] for t in f])
 meshes[k]={'v':vv,'f':ff}
(OUT/'source'/'meshes.json').write_text(json.dumps(meshes))
