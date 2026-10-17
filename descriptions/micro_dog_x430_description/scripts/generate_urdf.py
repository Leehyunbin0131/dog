#!/usr/bin/env python3
"""Generate standard URDF using only the Python standard library. Distances: m."""
import argparse, copy, json, math
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
def vec(v): return ' '.join(f'{x:.10g}' for x in v)
def sub(p,t,**kw): return E.SubElement(p,t,{k:str(v) for k,v in kw.items()})
def origin(p,xyz=(0,0,0),rpy=(0,0,0)): return sub(p,'origin',xyz=vec(xyz),rpy=vec(rpy))
def box_inertia(m,s): return [m*(s[1]**2+s[2]**2)/12,m*(s[0]**2+s[2]**2)/12,m*(s[0]**2+s[1]**2)/12]
def inertial(l,m,center,size):
 i=sub(l,'inertial');origin(i,center);sub(i,'mass',value=m);xx,yy,zz=box_inertia(m,size);sub(i,'inertia',ixx=xx,iyy=yy,izz=zz,ixy=0,ixz=0,iyz=0)
def primitive(l,kind,size,center,material=None):
 e=sub(l,kind);origin(e,center);g=sub(e,'geometry');sub(g,'box',size=vec(size))
 if material:sub(e,'material',name=material)
def mesh(l,path,xyz,material,package):
 e=sub(l,'visual');origin(e,xyz);g=sub(e,'geometry');uri='package://micro_dog_x430_description/meshes/'+path if package else '../meshes/'+path
 sub(g,'mesh',filename=uri,scale='1 1 1');sub(e,'material',name=material)
def validate_config(c):
 for key in ['body_length','body_width','body_height','body_mass','fixed_mount_mass_each']:
  if not isinstance(c[key],(int,float)) or not math.isfinite(c[key]) or c[key]<=0:raise ValueError(key+' must be finite and positive')
 for corner in ['FL','FR','RL','RR']:
  if len(c['hip_attachments'][corner])!=3 or not all(math.isfinite(v) for v in c['hip_attachments'][corner]):raise ValueError('Bad hip attachment '+corner)
 for name,p in c['dynamics'].items():
  if any(p[k]<=0 or not math.isfinite(p[k]) for k in ['mass','effort','velocity']):raise ValueError('Bad dynamics '+name)
 for name,r in c['joint_limits'].items():
  if len(r)!=2 or not all(math.isfinite(v) for v in r) or r[0]>=r[1]:raise ValueError('Bad limits '+name)
def generate(c,geo,package=False):
 validate_config(c);r=E.Element('robot',name='micro_dog_x430');r.append(E.Comment('CAD-derived visuals. Preliminary mass/inertia/limits. Knee is an equivalent serial joint, NOT motor shaft angle.'))
 for name,col in [('body','0.22 0.28 0.36 1'),('printed','0.16 0.62 0.68 1'),('motor','0.30 0.34 0.40 1'),('foot','0.43 0.40 0.62 1')]:
  mat=sub(r,'material',name=name);sub(mat,'color',rgba=col)
 b=sub(r,'link',name='base_link');dims=[c['body_length'],c['body_width'],c['body_height']];primitive(b,'visual',dims,[0,0,0],'body');primitive(b,'collision',dims,[0,0,0])
 # One base inertial represents box payload + four fixed motor/mount assemblies.
 fixed=c['fixed_mount_mass_each'];total=c['body_mass']+4*fixed
 inertia=box_inertia(c['body_mass'],dims);com=[sum(fixed*c['hip_attachments'][k][i] for k in geo['corners'])/total for i in range(3)]
 # Point-mass mounts plus conservative small cuboid inertia; shift tensor to true aggregate COM.
 I=[[0.0]*3 for _ in range(3)]
 for i in range(3):I[i][i]=inertia[i]
 for k in geo['corners']:
  p=c['hip_attachments'][k];ii=box_inertia(fixed,[.05,.05,.05])
  for i in range(3):
   for j in range(3):I[i][j]+=fixed*((sum(x*x for x in p) if i==j else 0)-p[i]*p[j])+(ii[i] if i==j else 0)
 for i in range(3):
  for j in range(3):I[i][j]-=total*((sum(x*x for x in com) if i==j else 0)-com[i]*com[j])
 ine=sub(b,'inertial');origin(ine,com);sub(ine,'mass',value=total);sub(ine,'inertia',ixx=I[0][0],iyy=I[1][1],izz=I[2][2],ixy=I[0][1],ixz=I[0][2],iyz=I[1][2])
 for corner,g in geo['corners'].items():
  hip=c['hip_attachments'][corner]
  for m in g['base_meshes']:mesh(b,m['file'],hip,m['material'],package)
  for stage in ['hip','thigh','shank','foot']:
   l=sub(r,'link',name=corner+'_'+stage);props=g['links'][stage]
   for m in props['meshes']:mesh(l,m['file'],[0,0,0],m['material'],package)
   mass=c['dynamics'][stage]['mass'];inertial(l,mass,props['center'],props['size'])
   for co in props['collisions']:primitive(l,'collision',co['size'],co['center'])
  for stage,parent,child in [('roll','base_link','hip'),('pitch','hip','thigh'),('knee','thigh','shank'),('foot','shank','foot')]:
   typ='fixed' if stage=='foot' else 'revolute';j=sub(r,'joint',name=corner+'_'+stage+'_joint',type=typ);sub(j,'parent',link=parent if parent=='base_link' else corner+'_'+parent);sub(j,'child',link=corner+'_'+child)
   origin(j,hip if stage=='roll' else g['joints'][stage]['origin'])
   if typ=='revolute':
    sub(j,'axis',xyz=vec(g['joints'][stage]['axis']));d=c['dynamics'][child];lo,hi=c['joint_limits'][stage];sub(j,'limit',lower=lo,upper=hi,effort=d['effort'],velocity=d['velocity']);sub(j,'dynamics',damping=c['joint_damping'],friction=0)
 E.indent(r,space='  ');return E.tostring(r,encoding='unicode',xml_declaration=True)
def main():
 a=argparse.ArgumentParser();a.add_argument('--config',type=Path,default=ROOT/'config/robot_parameters.json');a.add_argument('--output-dir',type=Path,default=ROOT/'urdf');args=a.parse_args();c=json.loads(args.config.read_text());geo=json.loads((ROOT/'config/cad_geometry.json').read_text());args.output_dir.mkdir(parents=True,exist_ok=True)
 for package,name in [(False,'micro_dog_x430.urdf'),(True,'micro_dog_x430_ros.urdf')]:
  p=args.output_dir/name;p.write_text(generate(c,geo,package)+'\n');print(p)
if __name__=='__main__':main()
