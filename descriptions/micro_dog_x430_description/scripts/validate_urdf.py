#!/usr/bin/env python3
"""Independent XML/STL/FK validator. Requires Python 3 and numpy, not ROS/FreeCAD.
Run from anywhere; generates validation/report.json. Exit 1 means a failed check.
Does not import generator math: parameter variants use its public CLI in temp dirs.
"""
import argparse, copy, hashlib, json, math, struct, subprocess, sys, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
CHECKS = []
def check(name, condition, details=None):
    CHECKS.append(dict(name=name, passed=bool(condition), details=details))
def arr(text, default='0 0 0'):
    return np.array([float(x) for x in (text or default).split()])
def tf(element):
    o=element.find('origin'); p=arr(o.get('xyz') if o is not None else None); a=arr(o.get('rpy') if o is not None else None)
    r,pitch,y=a; cr,sr=math.cos(r),math.sin(r); cp,sp=math.cos(pitch),math.sin(pitch); cy,sy=math.cos(y),math.sin(y)
    T=np.eye(4); T[:3,:3]=np.array([[cy,-sy,0],[sy,cy,0],[0,0,1]])@np.array([[cp,0,sp],[0,1,0],[-sp,0,cp]])@np.array([[1,0,0],[0,cr,-sr],[0,sr,cr]]);T[:3,3]=p
    return T
def tensor(link):
    i=link.find('inertial/inertia');a={k:float(v) for k,v in i.attrib.items()};return np.array([[a['ixx'],a['ixy'],a['ixz']],[a['ixy'],a['iyy'],a['iyz']],[a['ixz'],a['iyz'],a['izz']]])
def parse(path):
    r=ET.parse(path).getroot();return r,{e.get('name'):e for e in r.findall('link')},{e.get('name'):e for e in r.findall('joint')}
def fk(links,joints):
    roots=set(links)-{j.find('child').get('link') for j in joints.values()};poses={r:np.eye(4) for r in roots};pending=list(joints.values())
    while pending:
        done=[]
        for j in pending:
            p=j.find('parent').get('link');c=j.find('child').get('link')
            if p in poses: poses[c]=poses[p]@tf(j);done.append(j)
        if not done: raise ValueError('Cycle or disconnected invalid ancestry')
        pending=[j for j in pending if j not in done]
    return roots,poses
def stl_vertices(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:raise ValueError('Not a valid binary STL: '+str(path))
    records=np.frombuffer(data, dtype=np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attribute','<u2')]),offset=84,count=n)
    return records['v'].reshape(-1,3).astype(float), n

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,default=ROOT/'validation/report.json');args=ap.parse_args()
    cfg=json.loads((ROOT/'config/robot_parameters.json').read_text());frames=json.loads((ROOT/'config/cad_frames.json').read_text());geo=json.loads((ROOT/'config/cad_geometry.json').read_text())
    mesh_info={}; mesh_vertices={}; models={}
    for path in sorted((ROOT/'urdf').glob('*.urdf')):
        tag=path.name;r,links,joints=parse(path);models[tag]=(r,links,joints)
        check(tag+': counts',len(links)==17 and len(joints)==16 and sum(j.get('type')=='revolute' for j in joints.values())==12 and sum(j.get('type')=='fixed' for j in joints.values())==4)
        check(tag+': unique names',len(links)==len(r.findall('link')) and len(joints)==len(r.findall('joint')))
        children=[j.find('child').get('link') for j in joints.values()]
        check(tag+': one parent per child',len(set(children))==len(children))
        check(tag+': all references resolve',all(j.find(s).get('link') in links for j in joints.values() for s in ['parent','child']))
        roots,poses=fk(links,joints);check(tag+': connected acyclic base root',roots=={'base_link'} and set(poses)==set(links))
        for e in list(joints.values())+[el for l in links.values() for el in l if el.tag in ['inertial','visual','collision']]:
            T=tf(e);check(tag+': rigid origin '+(e.get('name') or e.tag),np.isfinite(T).all() and np.allclose(T[:3,:3].T@T[:3,:3],np.eye(3)) and np.isclose(np.linalg.det(T[:3,:3]),1))
        for name,j in joints.items():
            if j.get('type')=='fixed':continue
            axis=arr(j.find('axis').get('xyz'));lim=j.find('limit');v={k:float(lim.get(k)) for k in ['lower','upper','effort','velocity']}
            check(tag+': axis '+name,np.isfinite(axis).all() and np.isclose(np.linalg.norm(axis),1))
            check(tag+': limits '+name,all(math.isfinite(x) for x in v.values()) and v['lower']<0<v['upper'] and v['effort']>0 and v['velocity']>0)
        for name,l in links.items():
            mass=float(l.find('inertial/mass').get('value'));I=tensor(l);ev=np.linalg.eigvalsh(I)
            check(tag+': physical inertia '+name,math.isfinite(mass) and mass>0 and np.isfinite(I).all() and ev.min()>0 and ev[-1]<=sum(ev[:2])+1e-12,{'mass_kg':mass,'principal_inertias_kg_m2':ev.tolist()})
            for box in l.findall('.//box'):check(tag+': box positive '+name,np.all(arr(box.get('size'))>0))
            for mesh in l.findall('.//mesh'):
                uri=mesh.get('filename');p=ROOT/uri.split('package://micro_dog_x430_description/')[1] if uri.startswith('package://micro_dog_x430_description/') else path.parent/uri
                check(tag+': mesh resolves '+uri,p.is_file() and np.allclose(arr(mesh.get('scale'),'1 1 1'),1))
                if p.name not in mesh_info:
                    verts,n=stl_vertices(p);extent=np.ptp(verts,axis=0);mesh_vertices[p.name]=verts
                    check('STL metric finite extent '+p.name,np.isfinite(verts).all() and extent.min()>0.0001 and extent.max()<0.5,extent.tolist())
                    mesh_info[p.name]={'triangles':n,'min_m':verts.min(axis=0).tolist(),'max_m':verts.max(axis=0).tolist(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for corner in cfg['hip_attachments']:
            g=frames['corners']['LR' if corner=='RL' else corner];refs=g['joints_robot_mm'];shift=np.array(cfg['hip_attachments'][corner])-np.array(refs['roll']['point'])*.001
            for stage,joint in [('hip','roll'),('thigh','pitch'),('shank','knee'),('foot','foot_attachment')]:
                T=poses[corner+'_'+stage];target=np.array(refs[joint]['point'])*.001+shift
                check(tag+': CAD zero FK '+corner+'_'+stage,np.allclose(T[:3,3],target,atol=1e-10) and np.allclose(T[:3,:3],np.eye(3)),{'position_m':T[:3,3].tolist(),'reference_m':target.tolist()})
            for j in ['roll','pitch','knee']:
                check(tag+': CAD axis '+corner+'_'+j,np.allclose(arr(joints[corner+'_'+j+'_joint'].find('axis').get('xyz')),refs[j]['axis']))
    base=models['micro_dog_x430.urdf'];_,bl,bj=base;_,bp=fk(bl,bj)
    # Cross-check local CAD bounds against actual metre mesh vertices.
    for corner,g in geo['corners'].items():
        for stage,l in g['links'].items():
            v=np.concatenate([mesh_vertices[m['file']] for m in l['meshes']]);lo=v.min(axis=0);hi=v.max(axis=0)
            check('Geometry mesh bounds '+corner+'_'+stage,np.allclose((lo+hi)/2,l['center'],atol=1e-7) and np.allclose(np.maximum(hi-lo,.001),l['size'],atol=1e-7))
    # Test transforms from CAD. Reflections are intentional ONLY in baked meshes.
    for corner,g in frames['corners'].items():
        for name,value in g.items():
            if isinstance(value,list) and np.shape(value)==(4,4):
                T=np.array(value);R=T[:3,:3];check('CAD orthogonal '+corner+' '+name,np.allclose(R.T@R,np.eye(3)) and np.isclose(abs(np.linalg.det(R)),1) and np.allclose(T[3],[0,0,0,1]),{'determinant':float(np.linalg.det(R))})
    def generate_variant(c):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);cp=td/'params.json';cp.write_text(json.dumps(c));subprocess.run([sys.executable,str(ROOT/'scripts/generate_urdf.py'),'--config',str(cp),'--output-dir',str(td/'urdf')],check=True,capture_output=True)
            return parse(td/'urdf/micro_dog_x430.urdf')
    changed=copy.deepcopy(cfg)
    for k,factor in [('body_length',1.3),('body_width',1.7),('body_height',1.4)]:changed[k]*=factor
    _,dl,dj=generate_variant(changed)
    check('Body-only change preserves all joint definitions',all(ET.tostring(bj[k])==ET.tostring(dj[k]) for k in bj))
    check('Body-only change updates visual collision and inertia',all(not np.allclose(arr(bl['base_link'].find(k+'/geometry/box').get('size')),arr(dl['base_link'].find(k+'/geometry/box').get('size'))) for k in ['visual','collision']) and not np.allclose(tensor(bl['base_link']),tensor(dl['base_link'])))
    delta=np.array([.017,-.009,.013]);changed=copy.deepcopy(cfg);changed['hip_attachments']['FL']=(np.array(changed['hip_attachments']['FL'])+delta).tolist();_,hl,hj=generate_variant(changed);_,hp=fk(hl,hj)
    for name in bl:
        expected=delta if name.startswith('FL_') else np.zeros(3)
        check('Single attachment FK '+name,np.allclose(hp[name][:3,3]-bp[name][:3,3],expected,atol=1e-10) and np.allclose(hp[name][:3,:3],bp[name][:3,:3]))
    for bv,hv in zip(bl['base_link'].findall('visual'),hl['base_link'].findall('visual')):
        m=bv.find('geometry/mesh');expected=delta if m is not None and Path(m.get('filename')).name.startswith('FL_') else np.zeros(3)
        check('Single attachment base visual '+('box' if m is None else m.get('filename')),np.allclose(tf(hv)[:3,3]-tf(bv)[:3,3],expected))
    # Independently aggregate COM-centered inertia with parallel-axis theorem.
    for label,c,l in [('original',cfg,bl['base_link']),('hip_shift',changed,hl['base_link'])]:
        masses=np.array([c['body_mass']]+[c['fixed_mount_mass_each']]*4);positions=np.array([[0,0,0]]+list(c['hip_attachments'].values()));com=np.average(positions,axis=0,weights=masses);dims=[[c['body_length'],c['body_width'],c['body_height']]]+[[.05]*3]*4;I=np.zeros((3,3))
        for mass,pos,size in zip(masses,positions,dims):
            s=np.array(size)**2;I+=np.diag(mass*(s.sum()-s)/12);d=pos-com;I+=mass*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
        check('Aggregate base inertia '+label,np.allclose(tensor(l),I,atol=1e-12) and np.allclose(tf(l.find('inertial'))[:3,3],com,atol=1e-11) and np.isclose(float(l.find('inertial/mass').get('value')),masses.sum()))
    passed=all(c['passed'] for c in CHECKS);report={'passed':passed,'check_count':len(CHECKS),'failed_checks':[c for c in CHECKS if not c['passed']],'mesh_count':len(mesh_info),'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(list((ROOT/'urdf').glob('*.urdf'))+list((ROOT/'config').glob('*.json'))+[ROOT/'scripts/generate_urdf.py',ROOT/'scripts/export_cad_meshes.py'])},'checks':CHECKS,'meshes':mesh_info,'limitations':['Parser-level validation does not validate physical dynamics or simulator contact stability.','Masses, bounding-box inertias, collision boxes and limits are preliminary estimates, not measured hardware specifications.','Knee is an equivalent serial revolute, not motor shaft angle; omitted closed-loop linkage is not simulated.','Front pitch motors are reconstructed with pelvis transforms; no independently modeled front motor instances exist in overview CAD.','Joint link rotations are proper rotations. CAD mirror transforms are baked into mesh geometry and may have determinant -1.'],'cad_warnings':frames.get('warnings',[])}
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['passed','check_count','failed_checks','mesh_count']}));return 0 if passed else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print('Validation error: '+str(e),file=sys.stderr);raise
