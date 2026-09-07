import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'Lucky_Star_1960s.blend'))
scene=bpy.context.scene
for m in list(scene.timeline_markers):scene.timeline_markers.remove(m)
for name,frame in [('READY',1),('PULL LEVER',16),('REELS SPIN',34),('LEVER RETURNS',43),('REEL 1 STOP',148),('REEL 2 STOP',168),('777 JACKPOT',187),('HOLD / REPEAT',361)]:scene.timeline_markers.new(name,frame=frame)
for old,new in [('Layout','01 Showcase'),('Modeling','02 Quad Topology'),('UV Editing','03 UV Atlas'),('Animation','04 Animation')]:
    ws=bpy.data.workspaces.get(old)
    if ws:ws.name=new
for ws in bpy.data.workspaces:
    for screen in ws.screens:
        for area in screen.areas:
            if area.type=='IMAGE_EDITOR':area.spaces.active.image=bpy.data.images.get('T_SlotMachine_BaseColor')
            if area.type=='VIEW_3D':
                space=area.spaces.active
                space.region_3d.view_perspective='CAMERA'
                if ws.name=='02 Quad Topology':space.shading.type='SOLID';space.overlay.show_wireframes=True
                elif ws.name in ['01 Showcase','03 UV Atlas','04 Animation']:space.shading.type='MATERIAL'
rig=bpy.data.objects['SK_SlotMachine'];rig['Cycle seconds']=12;rig['Jackpot settled at seconds']=6.2;rig['Topology']='18537 quads; three independent reels; rigid one-bone weights'
for filename in ['README.md','build_slot_machine.py','make_graphics.py']:
    t=bpy.data.texts.get(filename) or bpy.data.texts.new(filename);t.clear();t.write((P/filename).read_text(encoding='utf8'))
scene.frame_set(241)
bpy.context.window.workspace=bpy.data.workspaces['01 Showcase']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Lucky_Star_1960s.blend'))
print('WORKFLOW_READY')
