"""Blender 5: all-quad construction, UV bake, rigid rig and FBX export."""
import bpy, bmesh, math, json
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent
T=P/'textures'; E=P/'exports'; R=P/'previews'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.render.fps=30
scene.frame_start=1;scene.frame_end=361
parts=[]; assignments={}; mats={}
def material(name,color,metal=0,rough=.3,img=None,emit=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    if img:
        uv=n.new('ShaderNodeUVMap');uv.uv_map='SourceUV'
        tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(T/img));m.node_tree.links.new(uv.outputs[0],tx.inputs['Vector']);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    m['metallic']=metal;m['roughness']=rough;m['emission']=emit;mats[name]=m
    return m
teal=material('Enamel_Petrol',(.018,.19,.16),.5,.26)
chrome=material('Polished_Chrome',(.64,.7,.72),1,.2)
gold=material('Champagne_Brass',(.63,.38,.13),.85,.26)
black=material('Recess_Rubber',(.012,.02,.018),.05,.55)
red=material('Ruby_Bakelite',(.57,.012,.018),.08,.2)
cream=material('Warm_Ivory',(.88,.79,.58),.12,.36)
marquee=material('Marquee_Art',(1,1,1),.15,.32,'Marquee_Generated.png')
pay=material('Paytable_Art',(1,1,1),.1,.4,'Paytable_Source.png')
reelmat=material('Reel_Art',(1,1,1),0,.4,'Reel_Source.png')
winner=material('Winner_Art',(1,1,1),.1,.35,'Winner_Source.png')
def mesh(name,vs,fs,mat,bone='Root',uvs=None):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);ob.data.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    layer=me.uv_layers.new(name='SourceUV')
    if uvs:
        for po,coords in zip(me.polygons,uvs):
            # Recalculated face winding can change loop order; coordinates are indexed by vertex.
            for li in po.loop_indices: layer.data[li].uv=coords[me.loops[li].vertex_index]
    for po in me.polygons:po.use_smooth=True
    parts.append(ob);assignments[name]=bone;return ob
def box(name,loc,dim,mat,r=.01,bone='Root',sphere=False):
    half=[a/2 for a in dim];r=min(r,min(half)*.99)
    axes=[[-h,-h+r*.293,-h+r,h-r,h-r*.293,h] for h in half]
    if sphere: axes=[[(-1+2*i/8)*h for i in range(9)] for h in half]
    vs=[];fs=[];ids={}
    def v(p):
        key=tuple(round(t,8) for t in p)
        if key not in ids:
            if sphere: q=Vector([p[i]/half[i] for i in range(3)]).normalized();p=[q[i]*half[i] for i in range(3)]
            else:
                c=Vector([max(-half[i]+r,min(half[i]-r,p[i])) for i in range(3)]);d=Vector(p)-c;p=c+d.normalized()*r
            ids[key]=len(vs);vs.append(tuple(p[i]+loc[i] for i in range(3)))
        return ids[key]
    for a in range(3):
        b,c=(a+1)%3,(a+2)%3
        for side in [-1,1]:
            for j in range(len(axes[b])-1):
                for k in range(len(axes[c])-1):
                    face=[]
                    for jj,kk in [(j,k),(j+1,k),(j+1,k+1),(j,k+1)]:
                        p=[0,0,0];p[a]=side*half[a];p[b]=axes[b][jj];p[c]=axes[c][kk];face.append(v(p))
                    fs.append(face)
    return mesh(name,vs,fs,mat,bone)
def panel(name,loc,w,h,mat,bone='Root'):
    x,y,z=loc;vs=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)]
    ob=mesh(name,vs,[(0,1,2,3)],mat,bone,[{0:(0,0),1:(1,0),2:(1,1),3:(0,1)}]);ob.data.polygons[0].use_smooth=False;return ob
def cylinder(name,loc,r,width,mat,bone='Root',axis='X',reel=False):
    # Square-to-disk cap grids share a 64-vertex circular boundary: no triangle fans.
    vs=[];fs=[];uv=[];ids={};N=16
    def pos(x,u,v):
        if u==0 and v==0: yy=zz=0
        elif abs(u)>abs(v): rr=u;ang=math.pi/4*v/u;yy=rr*math.cos(ang);zz=rr*math.sin(ang)
        else:rr=v;ang=math.pi/2-math.pi/4*u/v;yy=rr*math.cos(ang);zz=rr*math.sin(ang)
        # cap perimeter aligned to circumferential reel seam at -pi/8
        a=-math.pi/8;yy,zz=yy*math.cos(a)-zz*math.sin(a),yy*math.sin(a)+zz*math.cos(a)
        q=(x,-r*yy,r*zz)
        if axis=='Z':q=(q[1],q[2],q[0])
        if axis=='Y':q=(q[1],q[0],q[2])
        return tuple(q[i]+loc[i] for i in range(3))
    def add(p):
        k=tuple(round(c,8) for c in p)
        if k not in ids:ids[k]=len(vs);vs.append(p)
        return ids[k]
    boundaries=[]
    for x in [-width/2,width/2]:
        grid={}
        for i in range(N+1):
            for j in range(N+1):grid[i,j]=add(pos(x,2*i/N-1,2*j/N-1))
        for i in range(N):
            for j in range(N):fs.append([grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]]);uv.append({idx:(.5,.5) for idx in fs[-1]})
        ring=[]
        # Sorting by actual cylinder angle yields exact, contiguous UV strip.
        for i,j in grid:
            if i in [0,N] or j in [0,N]:
                p=pos(x,2*i/N-1,2*j/N-1); theta=(math.atan2(p[2]-loc[2],-(p[1]-loc[1]))+math.pi/8)%(2*math.pi) if axis=='X' else 0
                ring.append((round(theta,6),grid[i,j]))
        if axis!='X':
            # Use ordered square boundary for non-reel cylinders.
            ring=[(0,grid[N,j]) for j in range(N)]+[(0,grid[i,N]) for i in range(N,0,-1)]+[(0,grid[0,j]) for j in range(N,0,-1)]+[(0,grid[i,0]) for i in range(N)]
        else:ring.sort()
        boundaries.append([idx for _,idx in ring])
    for j in range(64):
        jj=(j+1)%64;f=[boundaries[0][j],boundaries[1][j],boundaries[1][jj],boundaries[0][jj]];fs.append(f);uv.append({f[0]:(0,j/64),f[1]:(1,j/64),f[2]:(1,(j+1)/64),f[3]:(0,(j+1)/64)})
    ob=mesh(name,vs,fs,mat,bone,uv if reel else None)
    if reel:
        ob.data.materials.append(chrome)
        for p in ob.data.polygons[:512]:p.material_index=1
    return ob

# Cabinet shell, stepped plinth and high shoulder marquee.
box('Plinth_Rubber',(0,0,.065),(.86,.63,.13),black,.035)
box('Plinth_Chrome',(0,-.015,.15),(.84,.61,.07),chrome,.023)
box('Cabinet_Base',(0,.025,.35),(.78,.53,.35),teal,.045)
box('Cabinet_Back',(0,.065,.96),(.76,.39,1.23),teal,.06)
box('Bottom_Chrome_Band',(0,-.005,.525),(.80,.55,.055),chrome,.015)
for x in [-.377,.377]:
    box('Chrome_Pillar_'+str(x),(x,-.27,1.025),(.057,.24,1.11),chrome,.024)
    box('Pillar_Gold_Inlay_'+str(x),(x,-.398,1.03),(.009,.009,.97),gold,.003)
box('Marquee_Housing',(0,-.238,1.49),(.76,.32,.36),chrome,.06)
box('Marquee_Enamel',(0,-.409,1.49),(.667,.022,.294),teal,.027)
panel('Marquee_UV',(0,-.423,1.49),.624,.263,marquee)
box('Reel_Window_Dark_Interior',(0,-.172,1.08),(.68,.025,.43),black,.015)
for x in [-.314,-.104,.104,.314]:box('Reel_Divider_'+str(x),(x,-.393,1.09),(.027,.065,.36),chrome,.011)
for z in [.9,1.28]:box('Reel_Frame_'+str(z),(0,-.397,z),(.674,.065,.04),chrome,.012)
reelcenters=[(-.209,-.212,1.09),(0,-.212,1.09),(.209,-.212,1.09)]
for i,c in enumerate(reelcenters):cylinder('Reel_'+str(i+1),c,.188,.177,reelmat,'Reel_'+str(i+1),reel=True)
# Payline markers leave the reel symbols unobstructed.
for x in [-.348,.348]:box('Payline_Marker_'+str(x),(x,-.437,1.09),(.027,.009,.012),red,.003)
box('Paytable_Bezel',(0,-.28,.724),(.7,.275,.3),chrome,.026)
panel('Paytable_UV',(0,-.422,.746),.633,.23,pay)
box('Coin_Entry_Plate',(.273,-.426,.557),(.104,.024,.073),gold,.012)
box('Coin_Slot',(.273,-.441,.563),(.05,.009,.009),black,.003)
box('Coin_Return_Button',(.19,-.439,.557),(.028,.022,.026),red,.008)
box('Payout_Tray_Back',(0,-.312,.389),(.60,.055,.19),black,.015)
box('Payout_Tray_Floor',(0,-.438,.316),(.655,.30,.047),chrome,.012)
box('Payout_Tray_Lip',(0,-.573,.358),(.655,.032,.11),chrome,.012)
for x in [-.313,.313]:box('Payout_Tray_Side_'+str(x),(x,-.451,.366),(.032,.24,.127),chrome,.013)
box('Winner_Bezel',(0,-.261,.236),(.64,.045,.10),gold,.012)
panel('Winner_UV',(0,-.287,.236),.594,.069,winner)
# Side trim and ventilation, locks and service hardware.
for x in [-.391,.391]:
    for z in [.67,.71,.75,.79,.83]:box('Side_Vent_'+str((x,z)),(x,.05,z),(.01,.215,.009),black,.003)
    box('Side_Flute_'+str(x),(x,.058,1.31),(.018,.20,.39),gold,.008)
for x in [-.32,.32]:
    for z in [.57,1.30,1.64]:
        cylinder('Screw_'+str((x,z)),(x,-.429,z),.008,.006,chrome,axis='Y')
        box('Screw_Slot_'+str((x,z)),(x,-.434,z),(.009,.002,.0017),black,.0005)
lever=(.466,-.045,.951)
cylinder('Lever_Mount',(.401,-.045,.951),.074,.073,chrome)
cylinder('Lever_Rosette',(.45,-.045,.951),.055,.035,gold)
cylinder('Lever_Hub',lever,.039,.055,chrome,'Lever')
shaft=box('Lever_Shaft',(.493,-.035,1.165),(.027,.031,.42),chrome,.012,'Lever')
box('Lever_Collar',(.493,-.035,1.373),(.051,.054,.049),gold,.012,'Lever')
box('Red_Ball',(.493,-.035,1.431),(.118,.118,.118),red,.055,'Lever',sphere=True)
# Small jackpot lamps along top chrome cap.
for i in range(7):
    box('Lamp_Socket_'+str(i),(-.27+i*.09,-.25,1.686),(.047,.051,.02),gold,.008)
    box('Amber_Lamp_'+str(i),(-.27+i*.09,-.25,1.708),(.033,.037,.034),cream,.016,sphere=True)

# Consolidate rigid components while retaining three separate editable reel meshes.
original_parts=list(parts);parts=[]
groups={bone:[ob for ob in original_parts if assignments[ob.name]==bone] for bone in ['Root','Lever','Reel_1','Reel_2','Reel_3']}
for bone in ['Root','Lever','Reel_1','Reel_2','Reel_3']:
    group=groups[bone]
    bpy.ops.object.select_all(action='DESELECT')
    for ob in group:ob.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    bpy.ops.object.join();ob=bpy.context.object;ob.name='Cabinet' if bone=='Root' else bone
    assignments[ob.name]=bone;parts.append(ob)
print('GEOMETRY COMPLETE - UNWRAPPING',flush=True)
# Unwrap all objects to one non-overlapping UV atlas, keeping source UVs for artwork.
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True);ob.data.uv_layers.new(name='BakeUV');ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.003,area_weight=.5,correct_aspect=True)
bpy.ops.object.mode_set(mode='OBJECT')
print('UV UNWRAP COMPLETE',flush=True)
# Quad and manifold audit before export (the four display faces are intentionally open).
audit={'objects':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),'quads':sum(len(o.data.polygons) for o in parts),'non_quad_faces':sum(sum(len(f.vertices)!=4 for f in o.data.polygons) for o in parts),'parts':[]}
for ob in parts:
    bm=bmesh.new();bm.from_mesh(ob.data);audit['parts'].append({'name':ob.name,'quads':len(ob.data.polygons),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'bone':assignments[ob.name]});bm.free()
assert audit['non_quad_faces']==0
scene.render.engine='CYCLES';scene.cycles.samples=8
scene.render.bake.margin=12;scene.render.bake.use_clear=True
def bake(kind):
    print('BAKING '+kind,flush=True)
    im=bpy.data.images.new('T_SlotMachine_'+kind,width=4096,height=4096,alpha=False)
    if kind=='ORM':im.colorspace_settings.name='Non-Color'
    for m in mats.values():
        nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output')
        en=nt.nodes.new('ShaderNodeEmission');en.name='BAKE_EMIT'
        if kind=='BaseColor':
            inp=bs.inputs['Base Color']
            if inp.is_linked:nt.links.new(inp.links[0].from_socket,en.inputs['Color'])
            else:en.inputs['Color'].default_value=inp.default_value
        else:en.inputs['Color'].default_value=(1,m['roughness'],m['metallic'],1)
        nt.links.new(en.outputs[0],out.inputs['Surface'])
        tx=nt.nodes.new('ShaderNodeTexImage');tx.name='BAKE_TARGET';tx.image=im;nt.nodes.active=tx
    bpy.ops.object.bake(type='EMIT')
    im.filepath_raw=str(T/(im.name+'.png'));im.file_format='PNG';im.save()
    for m in mats.values():
        nt=m.node_tree;nt.links.new(nt.nodes.get('Principled BSDF').outputs[0],nt.nodes.get('Material Output').inputs['Surface']);nt.nodes.remove(nt.nodes['BAKE_EMIT']);nt.nodes.remove(nt.nodes['BAKE_TARGET'])
    return im
base=bake('BaseColor');orm=bake('ORM')
baked=bpy.data.materials.new('M_SlotMachine_Baked');baked.use_nodes=True;n=baked.node_tree.nodes;l=baked.node_tree.links;bs=n.get('Principled BSDF')
u=n.new('ShaderNodeUVMap');u.uv_map='BakeUV'
tx=n.new('ShaderNodeTexImage');tx.image=base;l.new(u.outputs[0],tx.inputs[0]);l.new(tx.outputs['Color'],bs.inputs['Base Color'])
tr=n.new('ShaderNodeTexImage');tr.image=orm;l.new(u.outputs[0],tr.inputs[0]);sep=n.new('ShaderNodeSeparateColor');l.new(tr.outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Green'],bs.inputs['Roughness']);l.new(sep.outputs['Blue'],bs.inputs['Metallic'])
for ob in parts:
    ob.data.materials.clear();ob.data.materials.append(baked)
    for p in ob.data.polygons:p.material_index=0
    # Export atlas as channel 0, retain only final clean UVs.
    ob.data.uv_layers.remove(ob.data.uv_layers['SourceUV']);ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True

# Five-bone rigid rig. Source reel objects remain independent and editable.
bpy.ops.object.select_all(action='DESELECT')
arm=bpy.data.armatures.new('SlotMachine_Rig');rig=bpy.data.objects.new('SK_SlotMachine',arm);scene.collection.objects.link(rig);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for name,head in [('Root',(0,0,0)),('Lever',lever)]+[('Reel_'+str(i+1),c) for i,c in enumerate(reelcenters)]:
    b=arm.edit_bones.new(name);b.head=head;b.tail=Vector(head)+Vector((0,0,.1))
    if name!='Root':b.parent=arm.edit_bones['Root']
bpy.ops.object.mode_set(mode='OBJECT')
for ob in parts:
    g=ob.vertex_groups.new(name=assignments[ob.name]);g.add(list(range(len(ob.data.vertices))),1,'REPLACE');mod=ob.modifiers.new('Rigid skin','ARMATURE');mod.object=rig;ob.parent=rig
rig.animation_data_create();action=bpy.data.actions.new('A_Pull_Spin_Jackpot_12s');rig.animation_data.action=action
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def lever_angle(t):
    if t<.5:return 0
    if t<1.2:return math.radians(64)*smooth((t-.5)/.7)
    if t<1.4:return math.radians(64)
    if t<2.2:return math.radians(64)*(1-smooth((t-1.4)/.8))
    return 0
for frame in range(1,362):
    t=(frame-1)/30
    b=rig.pose.bones['Lever'];b.rotation_mode='XYZ';b.rotation_euler.x=lever_angle(t);b.keyframe_insert('rotation_euler',frame=frame,group='Lever')
    for i in range(3):
        duration=3.8+i*.65;u=max(0,min(1,(t-1.1)/duration));turns=7+i*2
        # Smooth deceleration with exact full-turn jackpot alignment.
        angle=2*math.pi*turns*(1-(1-u)**3)
        b=rig.pose.bones['Reel_'+str(i+1)];b.rotation_mode='XYZ';b.rotation_euler.x=angle;b.keyframe_insert('rotation_euler',frame=frame,group=b.name)
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for key in curve.keyframe_points:key.interpolation='LINEAR'
scene.frame_set(1)
for ob in parts:ob.select_set(True)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(E/'SK_SlotMachine.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE',use_mesh_modifiers=True,axis_forward='-Y',axis_up='Z',path_mode='COPY',embed_textures=True)
audit.update({'animation_seconds':12,'fps':30,'reel_stop_seconds':[4.9,5.55,6.2],'texture_resolution':[4096,4096],'UV':'Non-overlapping BakeUV, exported channel 0','ORM':'R=1 ambient-occlusion neutral, G=roughness, B=metallic','source_topology':'100% quads; FBX/game renderer triangulates for rendering'})
(P/'asset_audit.json').write_text(json.dumps(audit,indent=2))
# Studio presentation lives only in Blender; never included in the FBX export.
floor=box('STUDIO_Floor',(0,0,-.035),(200,200,.05),black,.01)
world=bpy.data.worlds.new('Studio World');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.15,.19,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
def area(name,loc,power,size,color):
    data=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.9))-ob.location).to_track_quat('-Z','Y').to_euler();data.energy=power;data.shape='DISK';data.size=size;data.color=color
area('Key Softbox',(2,-3,4),430,3,(.80,.9,1));area('Warm Fill',(-2,-2,2),300,2,(1,.79,.55));area('Rim',(1,2,3),600,2,(.64,.86,1))
data=bpy.data.cameras.new('Showcase Camera');cam=bpy.data.objects.new('Showcase Camera',data);scene.collection.objects.link(cam);cam.location=(2.35,-4.1,2.20);cam.rotation_euler=(Vector((.04,-.07,.91))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=2.22;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.frame_set(240)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Lucky_Star_1960s.blend'))
scene.render.filepath=str(R/'SlotMachine_Jackpot.png');bpy.ops.render.render(write_still=True)
scene.frame_set(36);scene.render.filepath=str(R/'SlotMachine_LeverPulled.png');bpy.ops.render.render(write_still=True)
print('SLOT_MACHINE_BUILD_COMPLETE',json.dumps(audit))
