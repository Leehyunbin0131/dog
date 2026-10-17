from render_cad import *
from PIL import ImageChops
axes=json.loads((OUT/'source'/'fastener_axes.json').read_text())['fasteners'];byid={x['id']:x for x in axes}
def ring(center,axis,outer,inner,length,sides=48):
 a=np.array(axis,dtype=float);a/=np.linalg.norm(a);b=np.cross(a,[0,0,1] if abs(a[2])<.9 else [0,1,0]);b/=np.linalg.norm(b);c=np.cross(a,b);vs=[];fs=[]
 for z,r in [(0,outer),(length,outer),(0,inner),(length,inner)]:
  for i in range(sides):vs.append((np.array(center)+a*z+r*(b*np.cos(2*np.pi*i/sides)+c*np.sin(2*np.pi*i/sides))).tolist())
 for k,l in [(0,1),(2,3),(0,2),(1,3)]:
  for i in range(sides):
   j=(i+1)%sides;fs.extend([[k*sides+i,l*sides+i,l*sides+j],[k*sides+i,l*sides+j,k*sides+j]])
 return {'v':vs,'f':fs}
def bolt(f,offset=0):
 a=np.array(f['insertion_axis_L']);p=np.array(f['head_center_L'])-a*offset;d=float(f['spec'].split('x')[0][1:]);height=f.get('head_height_mm',1.5);dia=f.get('head_diameter_mm',4.7)
 if f['head_reference']=='top_of_countersunk_head' or 'head_top' in f['head_reference']:
  head=ring(p,a,dia/2,d*.20,height)
  vv=np.array(head['v']);end=48
  for i in range(end,2*end):
   rel=vv[i]-p-a*height;vv[i]=p+a*height+rel*(d/dia)
  head['v']=vv.tolist()
  return [(ring(p+a*height,a,d/2,0,f['length_mm']-height),'bolt'),(head,'bolt')]
 return [(ring(p,a,d/2,0,f['length_mm']),'bolt'),(ring(p-a*height,a,dia/2,d*.22,height),'bolt')]
def fast(ids,offset=0):return sum([bolt(byid[x],offset) for x in ids],[])
def family(f):return [x['id'] for x in axes if x['family']==f]
def nuts(ids,offset=0):
 out=[]
 for x in ids:
  f=byid[x];a=np.array(f['insertion_axis_L']);p=np.array(f['nut_seat_center_L'])+a*offset;af=5.5 if f['spec'].startswith('M3') else 5
  mesh=ring(p,a,af/math.sqrt(3),1.5 if af==5.5 else 1.25,f['nut_thickness_mm'],6)
  if 'nut_polygon_vectors_L' in f:
   for i,q in enumerate(f['nut_polygon_vectors_L']):
    mesh['v'][i]=(p+q).tolist();mesh['v'][i+6]=(p+q+a*f['nut_thickness_mm']).tolist()
  out.append((mesh,'nut'))
 return out
def ar(ids,offset):return [(np.array(byid[x]['head_center_L'])-np.array(byid[x]['insertion_axis_L'])*offset,byid[x]['head_center_L']) for x in ids]
# Actual bearing geometry, final positions from cap and shaft seats.
raw['bearing_small1']=ring([52.9375,0,-57],[1,0,0],5,3,2.5)
raw['bearing_small2']=ring([52.8125,-142.5,-57],[1,0,0],5,3,2.5)
raw['bearing_large']=ring([38.875,-142.5,-85.5],[1,0,0],6.5,3.5,4)
raw['bearing_roll']=ring([-11.5,-12.75,-85.5],[0,-1,0],6.5,3.5,4)
core=['258','pitch','knee']
link=['253','254','256','257','bearing_small1','bearing_small2']
leg=core+['251','252','255','259','bearing_large']+link
allparts=leg+['260','261','262','263','roll','bearing_roll']
render('overview',allparts,extra=fast([x['id'] for x in axes])+nuts([x['id'] for x in axes if 'nut_seat_center_L' in x]))
render('cables',['258','pitch','knee'],['258'],view=(-1,.7,.5))
# Nut pockets are shown in separate physical components, not a falsely complete shank.
render('nuts_leg',['251','252','256','257'],offsets={'251':[-25,0,0],'252':[10,0,0],'256':[35,0,0],'257':[55,0,0]},view=(-1,.6,.3))
render('nuts_yoke',['263'],extra=nuts(family('fixed_support'),12),view=(.4,-1,.7))
for prefix,ids,parts,new,offs in [
 ('crank',['m3_motor_link'],['253','254','256','bearing_small1'],['254','256'],{'254':[18,0,0],'bearing_small1':[18,0,0],'256':[42,0,0]}),
 ('distal',['m3_distal_link'],['252','253','254','256','257','bearing_small1','bearing_small2'],['252','257'],{'252':[-20,0,0],'257':[28,0,0]}),
 ('pitch',family('pitch_horn'),['258','pitch'],['258'],{'pitch':[-30,0,0]}),
 ('knee',family('xl_rear'),core+['211','212','213','214'],['knee','211','212','213','214'],{'knee':[75,0,0],**{k:[35,0,0] for k in ['211','212','213','214']}}),
 ('large',[],core+['251','255','bearing_large'],['251','255'],{'251':[-85,0,0],'255':[55,0,0]}),
 ('shank',['m3_large_joint','m3_shank_upper','m3_shank_lower'],[k for k in leg if k!='259'],['252'],{'252':[35,0,0]}),
 ('foot',['m3_foot'],leg,['259'],{'259':[0,0,-30]}),
 ('crank_horn',family('crank_horn'),leg,['253'],{}),
 ('xm',family('xm_front'),['roll','263','277','278','279','280'],['263','277','278','279','280'],{'263':[0,-65,0],**{k:[0,-30,0] for k in ['277','278','279','280']}}),
 ('roll',family('roll_horn'),['roll','263','260'],['260'],{'260':[0,-30,0]}),
 ('carriers',family('pitch_case_carrier'),leg+['roll','263','260','261'],['261'],{'261':[0,-30,0]}),
 ('support',family('fixed_support'),allparts,['262','bearing_roll'],{'262':[0,-30,0],'bearing_roll':[0,-15,0]}),
]:
 view=(-1,.65,.4) if prefix in ['knee','large'] else (1,.65,.45)
 if prefix in ['xm','roll','support']:view=(.7,-1,.65)
 if prefix=='knee':view=(.4,1,.35)
 if prefix=='distal':view=(-1,.5,.35)
 if prefix=='large':view=(.25,1,.3)
 if prefix=='carriers':view=(1,-.65,.45)
 ex=fast(ids,25);arr=ar(ids,25)
 if prefix=='knee':ex=fast(ids);arr=[]
 if prefix=='xm':ex=fast(ids,90);arr=ar(ids,90);view=(1,-.35,.6)
 if prefix=='roll':
  ex=fast(ids,55)
  for x in ids:
   f=byid[x];p=np.array(f['washer_center_L'])+[0,-43,0];ex.append((ring(p,[0,1,0],2.5,1.1,.3),'bearing'))
  arr=ar(ids,55)
 if prefix in ['crank','distal']:
  nutid=ids[0];cap='256' if prefix=='crank' else '257';mesh=nuts(ids)[0][0];mesh['v']=(np.array(mesh['v'])+offs[cap]).tolist();ex.append((mesh,'nut'))
 if prefix=='carriers':offs={};ex=fast(ids,18);arr=ar(ids,18)
 if prefix=='support':ex=fast(ids,55);arr=ar(ids,55)
 labs=[]
 for ix,k in enumerate(new):
  vs=np.array(raw[k]['v']);p=(vs.min(axis=0)+vs.max(axis=0))/2+offs.get(k,[0,0,0]);labs.append((ix+1,p.tolist()))
  if k in offs:arr.append((p.tolist(),(p-np.array(offs[k])).tolist()))
 detailparts=['258','251','255','bearing_large'] if prefix=='large' else ['pitch','roll','263','260','261'] if prefix=='carriers' else ['pitch','roll','263','260','261','262','bearing_roll'] if prefix=='support' else parts
 render(prefix+'_e',detailparts,new,offs,ex,view=view,arrows=arr,labels=labs)
 render(prefix+'_a',parts,new,extra=fast(ids),view=view)
# Preloaded screws shown seated, never floating.
render('preload',['258'],['258'],extra=fast(family('xl_rear')),view=(-1,.7,.4))
(OUT/'source'/'render_manifest.json').write_text(json.dumps(renders,indent=2))
# Separate views expose every nut pocket; no imaginary shared insertion direction.
render('nuts_inner',['251'],extra=nuts(['m3_shank_upper','m3_shank_lower','m3_foot']),view=(-1,.4,.25),labels=[('1',byid[x]['nut_center_L']) for x in ['m3_shank_upper','m3_shank_lower','m3_foot']])
render('nuts_comp',['252'],extra=nuts(['m3_large_joint']),view=(1,.5,.3),labels=[('2',byid['m3_large_joint']['nut_center_L'])])
render('nuts_cap',['256'],extra=nuts(['m3_motor_link']),view=(1,.4,.3),labels=[('3',byid['m3_motor_link']['nut_center_L'])])
canvas=Image.new('RGB',(1500,1100),'white')
for name,box in [('nuts_inner',(0,0,580,1100)),('nuts_comp',(550,0,1130,1100)),('nuts_cap',(1100,350,1490,750))]:
 im=Image.open(OUT/'assets'/f'{name}.png');bbox=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox();im=im.crop(bbox);im.thumbnail((box[2]-box[0],box[3]-box[1]));canvas.paste(im,(box[0],box[1]+((box[3]-box[1]-im.height)//2)))
draw=ImageDraw.Draw(canvas);draw.line([(1300,310),(1310,480)],fill='#25445a',width=3);draw.ellipse((1270,280,1330,340),fill='white',outline='#25445a',width=3);draw.text((1300,310),'3',anchor='mm',fill='#25445a',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',42));canvas.save(OUT/'assets'/'nuts_leg.png')
ex=[];arr=[]
for x in family('fixed_support'):
 f=byid[x];mesh=nuts([x])[0][0];mesh['v']=(np.array(mesh['v'])+[15,0,0]).tolist();ex.append((mesh,'nut'));arr.append((np.array(f['nut_center_L'])+[15,0,0],f['nut_center_L']))
render('nuts_yoke',['263'],extra=ex,view=(1,-.65,.7),arrows=arr)
# Enlarged single fastener stack for roll washers: exploded parts share their true axis.
f=byid['roll_horn_1'];ex=bolt(f,20);ex.append((ring(np.array(f['washer_center_L'])+[0,-10,0],[0,1,0],2.5,1.1,.3),'bearing'))
render('washer_stack',['260'],extra=ex,view=(.8,-1,.3))
(OUT/'source'/'render_manifest.json').write_text(json.dumps(renders,indent=2))
# Pitch access: keep horn fixed and rotate only geometry behind the X=1 case plane.
def clipmesh(mesh,less):
 vertices=[];faces=[]
 for ids in mesh['f']:
  poly=[np.array(mesh['v'][i]) for i in ids];out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=a[0]<=1.00001 if less else a[0]>=1.00001;ib=b[0]<=1.00001 if less else b[0]>=1.00001
   if ia:out.append(a)
   if ia!=ib:out.append(a+(b-a)*((1.00001-a[0])/(b[0]-a[0])))
  if len(out)>=3:
   idx=len(vertices);vertices.extend([q.tolist() for q in out]);faces.extend([[idx,idx+i,idx+i+1] for i in range(1,len(out)-1)])
 return {'v':vertices,'f':faces}
case=clipmesh(raw['pitch'],True);raw['pitch_horn_fixed']=clipmesh(raw['pitch'],False)
focus=[[x,y,z] for x in [-45,70] for y in [-38,38] for z in [-115,-43]]
for tag,angle,ident in [('36',36.027373385,'xl_rear_3'),('144',143.972626615,'xl_rear_4')]:
 r=math.radians(angle);v=np.array(case['v']);p=np.array([0,0,-85.5]);m=np.array([[1,0,0],[0,math.cos(r),-math.sin(r)],[0,math.sin(r),math.cos(r)]]);raw['case_'+tag]={'v':((v-p)@m.T+p).tolist(),'f':case['f']}
 # Choose actual lower hole by signed Y.
 f=next(x for x in axes if x['family']=='xl_rear' and x['head_center_L'][2]<-90 and ((x['head_center_L'][1]<0)==(tag=='36')))
 tool=ring(np.array(f['head_center_L'])+[-60,0,0],[1,0,0],1.5,0,60)
 render('access_'+tag,['258','knee','pitch_horn_fixed','case_'+tag],['case_'+tag],extra=fast(family('xl_rear'))+[(tool,'bearing')],view=(-1,.05,.05),focus=focus)
 render('access_'+tag+'_full',['258','knee','pitch_horn_fixed','case_'+tag],['case_'+tag],extra=fast(family('xl_rear'))+[(tool,'bearing')],view=(-1,.6,.4))
(OUT/'source'/'render_manifest.json').write_text(json.dumps(renders,indent=2))
