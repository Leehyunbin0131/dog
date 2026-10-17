import json,math,ctypes,os
import numpy as np
from PIL import Image, ImageDraw,ImageFont
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
if (OUT/'source'/'meshes.npz').exists():
 packed=np.load(OUT/'source'/'meshes.npz');raw={k[:-2]:{'v':packed[k].tolist(),'f':packed[k[:-2]+'_f'].tolist()} for k in packed.files if k.endswith('_v')}
else:
 import gzip
 path=OUT/'source'/'meshes.json'
 raw=json.loads(path.read_text() if path.exists() else gzip.decompress((OUT/'source'/'meshes.json.gz').read_bytes()))
COL={'old':(.71,.76,.80),'new':(.98,.57,.13),'motor':(.25,.30,.36),'bearing':(.12,.64,.67),'bolt':(.15,.37,.82),'nut':(.75,.55,.15),'foot':(.45,.34,.66)}
lib=ctypes.CDLL(str(OUT/'source'/'raster.so'));lib.raster.argtypes=[ctypes.c_int]*3+[ctypes.c_void_p]*4
renders=json.loads((OUT/"source"/"render_manifest.json").read_text()) if os.environ.get("ONLY") and (OUT/"source"/"render_manifest.json").exists() else {}
def render(name,keys,new=[],offsets={},extra=[],view=(1,.65,.45),size=(1500,1100),labels=[],arrows=[],focus=None):
 if os.environ.get("ONLY") and name not in os.environ["ONLY"].split(","):return
 tris=[];colors=[]
 for k in keys:
  v=np.array(raw[k]['v'])+offsets.get(k,[0,0,0]);f=np.array(raw[k]['f']);tris.append(v[f]);co=COL['bearing'] if k.startswith('bearing') else COL['new'] if k in new else COL['motor'] if k in ['pitch','knee','roll'] else COL['foot'] if k=='259' else COL['bearing'] if k.startswith('bearing') else COL['old'];colors.extend([co]*len(f))
 for mesh,co in extra:
  tris.append(np.array(mesh['v'])[np.array(mesh['f'])]);colors.extend([COL.get(co,co)]*len(mesh['f']))
 t=np.concatenate(tris);c=np.array(colors);forward=np.array(view,dtype=float);forward/=np.linalg.norm(forward);right=np.cross([0,0,1],forward);right/=np.linalg.norm(right);up=np.cross(forward,right);basis=np.array([right,up,forward]);v=t@basis.T
 lo=v.min(axis=(0,1));hi=v.max(axis=(0,1));
 if focus is not None:
  bounds=np.array(focus)@basis.T;lo=bounds.min(axis=0);hi=bounds.max(axis=0)
 w,h=size;scale=min((w-100)/(hi[0]-lo[0]),(h-100)/(hi[1]-lo[1]));center=(lo+hi)/2
 normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9);light=(forward+.6*up-.4*right);light/=np.linalg.norm(light);intensity=.55+.45*np.abs(normals@light);c=np.uint8(np.clip(c*intensity[:,None]*255,0,255))
 v[:,:,0]=(v[:,:,0]-center[0])*scale+w/2;v[:,:,1]=h/2-(v[:,:,1]-center[1])*scale
 img=np.full((h,w,3),255,dtype=np.uint8);depth=np.full((h,w),-1e20);v=np.ascontiguousarray(v);c=np.ascontiguousarray(c)
 lib.raster(w,h,len(v),v.ctypes.data,c.ctypes.data,img.ctypes.data,depth.ctypes.data)
 im=Image.fromarray(img);draw=ImageDraw.Draw(im)
 def project(p):
  p=np.array(p)@basis.T;return ((p[0]-center[0])*scale+w/2,h/2-(p[1]-center[1])*scale)
 for p,q in arrows:
  a=np.array(project(p));b=np.array(project(q));delta=b-a;length=np.linalg.norm(delta)
  if length<5:continue
  u=delta/length
  for z in range(0,int(length)-10,16):draw.line([tuple(a+u*z),tuple(a+u*min(z+9,length-10))],fill='#234f90',width=4)
  side=np.array([-u[1],u[0]]);draw.polygon([tuple(b),tuple(b-u*15+side*6),tuple(b-u*15-side*6)],fill='#234f90')
 for text,p in labels:
  x,y=project(p);draw.line([(x,y),(x+38,y-38)],fill='#25445a',width=2);x+=38;y-=38;draw.ellipse((x-23,y-23,x+23,y+23),fill='white',outline='#25445a',width=2);draw.text((x,y),str(text),anchor='mm',fill='#25445a',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30))
 im.save(OUT/'assets'/f'{name}.png');renders[name]={'keys':keys,'new':new,'offsets':offsets,'view':view,'labels':labels}
 return project
if __name__=='__main__':render('test',[str(i) for i in range(251,264)]+['pitch','knee','roll'])
