#!/usr/bin/env python3
"""Read source CAD without saving it; bake mirrored metre STL meshes into link frames.
Requires FreeCAD Python API, no third-party Python packages. The checked-in STL
files mean FreeCAD is NOT needed for parameter changes or URDF generation.
"""
import argparse, hashlib, json, math, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def affine(m,p):return [sum(m[i][j]*p[j] for j in range(3))+m[i][3] for i in range(3)]
def det(m):return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
def stl(path,tri):
 with path.open('wb') as f:
  f.write(b'Micro Dog X430 CAD-derived METERS'.ljust(80,b' '));f.write(struct.pack('<I',len(tri)))
  for a,b,c in tri:
   u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];s=math.sqrt(sum(x*x for x in n));n=[x/s if s else 0 for x in n]
   f.write(struct.pack('<12fH',*(n+a+b+c),0))
def main():
 p=argparse.ArgumentParser();p.add_argument('--cad-dir',type=Path,required=True);p.add_argument('--freecad-lib',default='/usr/lib/freecad-python3/lib');args=p.parse_args();sys.path.append(args.freecad_lib);import FreeCAD as A
 frames=json.loads((ROOT/'config/cad_frames.json').read_text());doc=A.openDocument(str(args.cad_dir/'RR_complete_leg_pelvis_final.FCStd'));local=doc.getObject('Part').Placement.inverse();raw={}
 names={str(i):'Part__Feature'+str(i) for i in list(range(251,264))+[211,212,213,214,277,278,279,280]};names.update(knee='DC11_A01_DUMMY_ASM',pitch='DC11_A01_DUMMY_ASM001',roll='DC12_X430_DUMMY_ASSY_ASM_4_ASM')
 for key,name in names.items():
  o=doc.getObject(name)
  # The manufacturer assemblies carry detached stock screws and spacers.
  # Omit these accessory objects; add only the chosen installed spacers separately.
  objects=[o]
  if key in ['roll','pitch','knee']:
   objects=[c for c in o.Group if not any(t in (c.Name+' '+c.Label).upper() for t in ['SCREW','FHS_','WBH_','SPACER'])]
  vv=[];ff=[]
  def add(item):
   if not hasattr(item,'Shape'):
    for child in getattr(item,'Group',[]):add(child)
    return
   shape=item.Shape.copy();shape.Placement=local.multiply(item.getGlobalPlacement().multiply(item.Placement.inverse()).multiply(shape.Placement));v,f=shape.tessellate(.15);start=len(vv);vv.extend([[q.x,q.y,q.z] for q in v]);ff.extend([[i+start for i in face] for face in f])
  for item in objects:add(item)
  raw[key]=(vv,ff)
 groups={'base':'base','hip':'hip_roll','thigh':'upper_thigh','shank':'lower_shank','foot':'foot'};geo={'units':'m','corners':{},'source_sha256':{f:hashlib.sha256((args.cad_dir/f).read_bytes()).hexdigest() for f in ['RR_complete_leg_pelvis_final.FCStd','Micro_Dog_X430_four_corner_overview.FCStd']},'tessellation_mm':.15}
 for src,g in frames['corners'].items():
  corner='RL' if src=='LR' else src;joints=g['joints_robot_mm'];centers={stage:joints[j]['point'] for stage,j in [('base','roll'),('hip','roll'),('thigh','pitch'),('shank','knee'),('foot','foot_attachment')]};out={'base_meshes':[],'links':{},'joints':{}}
  for stage,group in groups.items():
   allv=[];entries=[]
   for material in ['printed','motor','foot']:
    tri=[]
    for key in frames['semantic_groups'][group]:
     mat='foot' if key=='259' else ('motor' if key in ['roll','pitch','knee','211','212','213','214','277','278','279','280'] else 'printed')
     if mat!=material:continue
     # Pitch case and carriers follow pelvis; front motor fit is a reconstruction.
     which='pelvis' if stage=='base' or key in ['260','261','pitch'] else 'leg';m=g['rr_part_local_to_robot_'+which];vertices,faces=raw[key];v=[[(x-centers[stage][i])*.001 for i,x in enumerate(affine(m,q))] for q in vertices];allv.extend(v)
     for face in faces:
      ids=list(face)
      if det(m)<0:ids[1],ids[2]=ids[2],ids[1]
      tri.append([v[i] for i in ids])
    if tri:
     filename=f'{corner}_{stage}_{material}.stl';stl(ROOT/'meshes'/filename,tri);entries.append({'file':filename,'material':material})
   if stage=='base':out['base_meshes']=entries
   else:
    lo=[min(p[i] for p in allv) for i in range(3)];hi=[max(p[i] for p in allv) for i in range(3)];center=[(lo[i]+hi[i])/2 for i in range(3)];size=[max(hi[i]-lo[i],.001) for i in range(3)]
    # Bounding boxes are conservative simplified collision shapes, not fitted CAD surfaces.
    out['links'][stage]={'meshes':entries,'center':center,'size':size,'collisions':[{'center':center,'size':size}]}
  for stage,parent,child in [('roll','roll','roll'),('pitch','roll','pitch'),('knee','pitch','knee'),('foot','knee','foot_attachment')]:out['joints'][stage]={'origin':[(joints[child]['point'][i]-joints[parent]['point'][i])*.001 for i in range(3)],'axis':joints[child]['axis']}
  geo['corners'][corner]=out
 (ROOT/'config/cad_geometry.json').write_text(json.dumps(geo,indent=2)+'\n');A.closeDocument(doc.Name);print('Exported',len(list((ROOT/'meshes').glob('*.stl'))),'metre meshes')
if __name__=='__main__':main()
