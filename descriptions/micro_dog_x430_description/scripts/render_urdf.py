#!/usr/bin/env python3
"""Render the GENERATED URDF through independent XML parsing + FK. numpy/Pillow/g++ needed."""
import json, math, struct, subprocess, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
def xyz(s):return np.array([float(x) for x in s.split()])
def rotation(axis,q):
 a=axis/np.linalg.norm(axis);K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
 return np.eye(3)+np.sin(q)*K+(1-np.cos(q))*(K@K)
def origin(e):
 T=np.eye(4)
 if e is None:return T
 T[:3,3]=xyz(e.get('xyz','0 0 0'));r,p,y=xyz(e.get('rpy','0 0 0'));T[:3,:3]=rotation(np.array([0,0,1]),y)@rotation(np.array([0,1,0]),p)@rotation(np.array([1,0,0]),r);return T
def box(size):
 v=np.array([[x,y,z] for x in [-.5,.5] for y in [-.5,.5] for z in [-.5,.5]])*size
 return v[np.array([[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]])]
def read_stl(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,80)[0];dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);return np.frombuffer(b,dtype=dt,offset=84,count=n)['v'].astype(float)
def scene(path,angles):
 r=ET.parse(path).getroot();links={e.get('name'):e for e in r.findall('link')};joints=r.findall('joint');T={'base_link':np.eye(4)}
 while len(T)<len(links):
  before=len(T)
  for j in joints:
   p=j.find('parent').get('link');c=j.find('child').get('link')
   if p not in T or c in T:continue
   motion=np.eye(4)
   if j.get('type')!='fixed':motion[:3,:3]=rotation(xyz(j.find('axis').get('xyz')),angles.get(j.get('name'),0))
   T[c]=T[p]@origin(j.find('origin'))@motion
  if len(T)==before:raise ValueError('Disconnected graph')
 mats={m.get('name'):xyz(m.find('color').get('rgba'))[:3] for m in r.findall('material')};tris=[];cols=[]
 for name,l in links.items():
  for v in l.findall('visual'):
   g=v.find('geometry');mesh=g.find('mesh')
   if mesh is not None:tri=read_stl(path.parent/mesh.get('filename'))*xyz(mesh.get('scale','1 1 1'))
   else:tri=box(xyz(g.find('box').get('size')))
   tr=T[name]@origin(v.find('origin'));tri=tri@tr[:3,:3].T+tr[:3,3];tris.append(tri);cols.append(np.tile(mats[v.find('material').get('name')],(len(tri),1)))
 return np.concatenate(tris),np.concatenate(cols),T
def render(tri,col,dest,title,view):
 w,h=1500,1050;cam=np.array(view,dtype=float);cam/=np.linalg.norm(cam);right=np.cross([0,0,1],cam);right/=np.linalg.norm(right);up=np.cross(cam,right);B=np.array([right,-up,cam]).T;tri=tri@B
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-15);light=np.array([-.25,-.55,1]);light/=np.linalg.norm(light);col=col*(.5+.5*np.abs(normal@light))[:,None]*255
 lo=tri[:,:,:2].min((0,1));hi=tri[:,:,:2].max((0,1));scale=min((w-160)/(hi[0]-lo[0]),(h-230)/(hi[1]-lo[1]));tri[:,:,:2]=(tri[:,:,:2]-(lo+hi)/2)*scale+[w/2,h/2+30]
 arr=np.concatenate([tri.reshape(-1,9),col],axis=1).astype('float32')
 with tempfile.TemporaryDirectory() as d:
  b=Path(d)/'scene.bin';ppm=Path(d)/'scene.ppm';exe=Path(d)/'raster';subprocess.run(['g++','-O2',str(ROOT/'scripts/raster.cpp'),'-o',str(exe)],check=True)
  with b.open('wb') as f:f.write(struct.pack('<i',len(arr)));f.write(arr.tobytes())
  subprocess.run([str(exe),str(b),str(ppm),str(w),str(h)],check=True);im=Image.open(ppm).convert('RGB')
  draw=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',27);draw.text((40,25),title,font=font,fill='#19324b');draw.text((40,65),'Parsed URDF + STL + forward kinematics | meters | preliminary dynamics',font=font,fill='#4b6171');draw.text((40,h-52),'Crank/pushrod omitted. Temporary body box. No simulator or collision-free claim.',font=font,fill='#4b6171');im.save(dest)
def main():
 p=ROOT/'urdf/micro_dog_x430.urdf';poses={'neutral':{},'bent':{}}
 for c in ['FL','FR','RL','RR']:
  side=1 if c.endswith('R') else -1;poses['bent'][c+'_pitch_joint']=side*.7;poses['bent'][c+'_knee_joint']=-side*.7;poses['bent'][c+'_roll_joint']=0
 allinfo={}
 for name,q in poses.items():
  tri,col,T=scene(p,q);allinfo[name]={'joints_radians':q,'mesh_bounds_m':[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],'foot_link_origins_m':{c:T[c+'_foot'][:3,3].tolist() for c in ['FL','FR','RL','RR']},'base_height_for_lowest_visual_ground_m':float(-tri[:,:,2].min())};render(tri.copy(),col,ROOT/f'validation/{name}.png',f'Micro Dog X430: {name} pose',(.8,-1.4,.85))
 tri,col,T=scene(p,{});render(tri,col,ROOT/'validation/neutral_top.png','Micro Dog X430: neutral top-oblique',(0.05,-.05,1))
 (ROOT/'validation/poses.json').write_text(json.dumps(allinfo,indent=2)+'\n')
if __name__=='__main__':main()
