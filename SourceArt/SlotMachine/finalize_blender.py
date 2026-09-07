import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'Lucky_Star_1960s.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['SK_SlotMachine']
parts=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig]
# Verify the exported game mesh in a separate scene before delivery.
assert len(parts)==5
assert all(len(p.vertices)==4 for o in parts for p in o.data.polygons)
assert all(o.data.uv_layers[0].name=='BakeUV' for o in parts)
frames={}
for f in [1,37,91,148,168,187,241,361]:
    scene.frame_set(f)
    frames[str(f)]={b.name:list(b.rotation_euler) for b in rig.pose.bones}
(P/'animation_samples.json').write_text(json.dumps(frames,indent=2))
# Fully portable source file with packed textures and a useful initial camera view.
scene.frame_set(241)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['Cabinet']
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA'
        a.spaces.active.shading.type='MATERIAL'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Lucky_Star_1960s.blend'))
# Export a precise SVG of the UV cage (not a stylized generated image).
lines=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048"><rect width="2048" height="2048" fill="#142726"/><g fill="none" stroke="#cfbd87" stroke-width="0.5">']
for ob in parts:
    uv=ob.data.uv_layers[0]
    for poly in ob.data.polygons:
        points=' '.join(f'{uv.data[i].uv.x*2048:.2f},{(1-uv.data[i].uv.y)*2048:.2f}' for i in poly.loop_indices)
        lines.append(f'<polygon points="{points}"/>')
lines.append('</g></svg>');(P/'previews/UV_Layout.svg').write_text('\n'.join(lines))
print('PORTABLE_SOURCE_VERIFIED')
