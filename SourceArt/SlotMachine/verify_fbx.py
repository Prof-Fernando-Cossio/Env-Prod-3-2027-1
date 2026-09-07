import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'exports/SK_SlotMachine.fbx'),use_anim=True)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
assert len(meshes)==5 and len(rig.data.bones)==5
assert all(len(o.data.uv_layers)>0 for o in meshes)
assert bpy.data.actions
out={'meshes':[o.name for o in meshes],'bones':[b.name for b in rig.data.bones],'actions':[{ 'name':a.name,'frame_range':list(a.frame_range)} for a in bpy.data.actions],'uv_channels':{o.name:len(o.data.uv_layers) for o in meshes},'mesh_vertices':sum(len(o.data.vertices) for o in meshes),'samples':{}}
for f in [1,37,91,190,361]:
    bpy.context.scene.frame_set(f)
    out['samples'][f]={b.name:list(b.matrix.to_quaternion()) for b in rig.pose.bones}
assert out['samples'][1]['Lever']!=out['samples'][37]['Lever']
assert out['samples'][1]['Reel_1']!=out['samples'][91]['Reel_1']
(P/'fbx_roundtrip_report.json').write_text(json.dumps(out,indent=2))
print('FBX_ROUNDTRIP_PASS')
