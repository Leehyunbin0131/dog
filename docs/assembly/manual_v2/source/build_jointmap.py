from render_cad import *
j=json.loads((OUT/'source'/'fastener_axes.json').read_text());by={x['id']:x for x in j['fasteners']}
ids=['m3_large_joint','m3_motor_link','m3_distal_link','m3_shank_upper','m3_shank_lower','m3_foot']
render('jointmap',[str(i) for i in range(251,264)]+['pitch','knee','roll'],labels=[(chr(65+i),by[k]['head_center_L']) for i,k in enumerate(ids)],view=(1,.65,.45))
