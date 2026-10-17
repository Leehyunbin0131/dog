"""Render original CAD meshes using documented per-group CAD overview frames.
No source CAD changes; no pose changes or arbitrary mirror/rotation.
Run: python docs/assembly/manual_v2/source/render_four_corner.py
"""
from pathlib import Path
import sys,json,hashlib,ctypes
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
from render_cad import raw,lib,COL
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
FRAME=ROOT/'descriptions/micro_dog_x430_description/config/cad_frames.json'
frames=json.loads(FRAME.read_text())
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
scene=[]
for corner,g in frames['corners'].items():
 for k in [str(i) for i in range(251,264)]+['pitch','knee','roll']+[str(i) for i in list(range(211,215))+list(range(277,281))]:
  group='pelvis' if k in ['260','261','262','263','pitch','roll','277','278','279','280'] else 'leg'
  m=np.array(g['rr_part_local_to_robot_'+group]);v=np.array(raw[k]['v'])@m[:3,:3].T+m[:3,3];f=np.array(raw[k]['f'])
  if np.linalg.det(m[:3,:3])<0:f=f[:,[0,2,1]]
  color=COL['new'] if k in ['260','261'] else COL['motor'] if k in ['pitch','knee','roll'] else COL['foot'] if k=='259' else COL['old']
  scene.append({'corner':corner,'part':k,'group':group,'tri':v[f],'color':color})
def render(name,view,size,parts=None):
 chosen=[s for s in scene if parts is None or s['part'] in parts]
 t=np.concatenate([s['tri'] for s in chosen]);c=np.concatenate([np.tile(s['color'],(len(s['tri']),1)) for s in chosen]);w,h=size
 forward=np.array(view,float);forward/=np.linalg.norm(forward)
 if abs(forward[2])>.999:right=np.array([1.,0,0]);up=np.array([0.,1,0])
 else:right=np.cross([0,0,1],forward);right/=np.linalg.norm(right);up=np.cross(forward,right)
 basis=np.array([right,up,forward]);v=t@basis.T;lo=v.min((0,1));hi=v.max((0,1));center=(lo+hi)/2;scale=min((w-230)/(hi[0]-lo[0]),(h-270)/(hi[1]-lo[1]))
 def project(p):
  p=np.array(p)@basis.T;return np.array([(p[0]-center[0])*scale+w/2,h/2+15-(p[1]-center[1])*scale])
 v[:,:,0]=(v[:,:,0]-center[0])*scale+w/2;v[:,:,1]=h/2+15-(v[:,:,1]-center[1])*scale
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-9);light=forward+.6*up-.4*right;light/=np.linalg.norm(light);c=np.uint8(np.clip(c*(.55+.45*np.abs(n@light))[:,None]*255,0,255))
 img=np.full((h,w,3),255,np.uint8);depth=np.full((h,w),-1e20);v=np.ascontiguousarray(v);c=np.ascontiguousarray(c);lib.raster(w,h,len(v),v.ctypes.data,c.ctypes.data,img.ctypes.data,depth.ctypes.data)
 im=Image.fromarray(img);draw=ImageDraw.Draw(im)
 def arrow(a,b,color,width=5):
  a,b=np.array(a),np.array(b);draw.line([tuple(a),tuple(b)],fill=color,width=width);d=(b-a)/np.linalg.norm(b-a);r=np.array([-d[1],d[0]]);draw.polygon([tuple(b),tuple(b-18*d+8*r),tuple(b-18*d-8*r)],fill=color)
 # Fixed visible +X reference; screen arrow follows the actual camera projection.
 a=np.array([w-310,65]);direction=project([80,0,0])-project([0,0,0]);direction/=np.linalg.norm(direction);b=a+130*direction;arrow(a,b,'#193e53',7);draw.text(tuple(a+[-15,-35]),'FRONT (+X)',font=ImageFont.truetype(font,27),fill='#193e53')
 for corner,g in frames['corners'].items():
  p=project(g['joints_robot_mm']['roll']['point']);side=1 if corner in ['LR','FL'] else -1
  if parts is not None:label=project([g['joints_robot_mm']['roll']['point'][0],side*75,10])
  else:label=p+np.array([-45 if corner in ['RR','LR'] else 50,-90 if side==1 else 80])
  draw.line([tuple(label),tuple(p)],fill='#476476',width=3);box=(label[0]-39,label[1]-24,label[0]+39,label[1]+24);draw.rounded_rectangle(box,radius=9,fill='white',outline='#193e53',width=3);draw.text(tuple(label),corner,anchor='mm',font=ImageFont.truetype(font,30),fill='#193e53')
 draw.rectangle((45,h-80,75,h-50),fill=tuple(int(x*255) for x in COL['new']));draw.text((90,h-80),'Pitch case / carrier',font=ImageFont.truetype(font,26),fill='#193e53')
 draw.rectangle((480,h-80,510,h-50),fill=tuple(int(x*255) for x in COL['motor']));draw.text((525,h-80),'Motor bodies',font=ImageFont.truetype(font,26),fill='#193e53')
 im.save(OUT/'assets'/f'{name}.png')
 return {'view':list(view),'size':list(size),'triangles':len(t),'parts':parts,'bounds_robot_mm':[t.min((0,1)).tolist(),t.max((0,1)).tolist()]}
report={'sources':{'frames':str(FRAME.relative_to(ROOT)),'frames_sha256':hashlib.sha256(FRAME.read_bytes()).hexdigest()},'method':'RR exact tessellated CAD geometry, transformed by documented leg/pelvis affine matrices. Determinant-negative transforms reverse winding. All four corners retain original CAD pose; no schematic pose symmetry.','warnings':frames['warnings'][:2], 'renders':{}}
report['renders']['four_corner_motors']=render('four_corner_motors',(.35,-1,1.35),(1700,1050))
report['renders']['four_corner_pitch_top']=render('four_corner_pitch_top',(0,0,1),(1800,1000),['260','261','262','263','pitch','roll','277','278','279','280'])
report['transform_checks']={c:{g:float(np.linalg.det(np.array(v['rr_part_local_to_robot_'+g])[:3,:3])) for g in ['pelvis','leg']} for c,v in frames['corners'].items()}
report['roll_motor_aabb_max_error_mm']={c:float(np.abs(np.array([next(s['tri'] for s in scene if s['corner']==c and s['part']=='roll').min((0,1)),next(s['tri'] for s in scene if s['corner']==c and s['part']=='roll').max((0,1))])-np.array(v['roll_motor_aabb_robot_mm'])).max()) for c,v in frames['corners'].items()}
report['motor_instances']=sum(s['part'] in ['roll','pitch','knee'] for s in scene)
report['corner_labels']=list(frames['corners'])
(OUT/'source/four_corner_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'motor_instances':report['motor_instances'],'renders':report['renders']},indent=2))
